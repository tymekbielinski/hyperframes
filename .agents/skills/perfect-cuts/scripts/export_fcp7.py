#!/usr/bin/env python3
"""Export a Perfect Cuts cut-plan v1 as FCP7 XML for Premiere or Resolve."""

from __future__ import annotations

import argparse
import html
import math
import sys
import urllib.parse
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cut_plan import load_plan, validate_plan  # noqa: E402


NTSC = {23.976: 24, 29.97: 30, 59.94: 60}


def rate_info(fps: float) -> tuple[int, str]:
    for ntsc_fps, timebase in NTSC.items():
        if abs(fps - ntsc_fps) < 0.01:
            return timebase, "TRUE"
    return round(fps), "FALSE"


def _safe_id(value: str) -> str:
    cleaned = "".join(char if char.isalnum() else "-" for char in value).strip("-")
    return cleaned or "item"


def _path_url(path: str) -> str:
    if path.startswith("file://"):
        return path
    return "file://" + urllib.parse.quote(path)


def _source_meta(plan: dict, source_id: str) -> dict:
    sequence = plan["sequence"]
    source = plan["sources"][source_id]
    fps = float(sequence["fps"])
    return {
        "name": Path(source["path"]).name,
        "path": source["path"],
        "frames": source.get("source_frames")
        or int(math.ceil(float(source.get("duration_seconds", 0)) * fps)),
        "width": source.get("width", sequence["width"]),
        "height": source.get("height", sequence["height"]),
        "sample_rate": source.get("sample_rate", sequence.get("sample_rate", 48000)),
        "audio_channels": source.get(
            "audio_channels", sequence.get("audio_channels", 2)
        ),
    }


def _file_block(
    plan: dict,
    source_id: str,
    timebase: int,
    ntsc: str,
    include_details: bool,
) -> str:
    file_id = f"file-{_safe_id(source_id)}"
    if not include_details:
        return f'<file id="{file_id}"/>'
    meta = _source_meta(plan, source_id)
    return f"""<file id="{file_id}">
              <name>{html.escape(meta['name'])}</name>
              <pathurl>{html.escape(_path_url(meta['path']))}</pathurl>
              <rate><timebase>{timebase}</timebase><ntsc>{ntsc}</ntsc></rate>
              <duration>{meta['frames']}</duration>
              <media>
                <video><samplecharacteristics>
                  <rate><timebase>{timebase}</timebase><ntsc>{ntsc}</ntsc></rate>
                  <width>{meta['width']}</width><height>{meta['height']}</height>
                  <anamorphic>FALSE</anamorphic><pixelaspectratio>square</pixelaspectratio>
                  <fielddominance>none</fielddominance>
                </samplecharacteristics></video>
                <audio><samplecharacteristics>
                  <samplerate>{meta['sample_rate']}</samplerate><sampledepth>16</sampledepth>
                </samplecharacteristics></audio>
              </media>
            </file>"""


def export_plan(plan: dict, output_path: str | Path) -> Path:
    summary = validate_plan(plan)
    sequence = plan["sequence"]
    fps = float(sequence["fps"])
    timebase, ntsc = rate_info(fps)
    tracks = sorted(plan["tracks"], key=lambda track: (track["kind"] != "video", track["index"]))
    tracks_by_id = {track["id"]: track for track in tracks}

    records: dict[tuple[str, str], dict] = {}
    positions: dict[tuple[str, str], int] = {}
    for track in tracks:
        position = 0
        for clip in plan["clips"]:
            layer = next((item for item in clip["layers"] if item["track"] == track["id"]), None)
            if layer is None:
                continue
            position += 1
            item_id = f"clipitem-{_safe_id(clip['id'])}-{_safe_id(track['id'])}"
            records[(clip["id"], track["id"])] = {
                "id": item_id,
                "clip": clip,
                "layer": layer,
                "track": track,
            }
            positions[(clip["id"], track["id"])] = position

    def links_for(clip: dict) -> str:
        links: list[str] = []
        for layer in clip["layers"]:
            record = records[(clip["id"], layer["track"])]
            track = record["track"]
            group = "<groupindex>1</groupindex>" if track["kind"] == "audio" else ""
            links.append(
                "<link>"
                f"<linkclipref>{record['id']}</linkclipref>"
                f"<mediatype>{track['kind']}</mediatype>"
                f"<trackindex>{track['index']}</trackindex>"
                f"<clipindex>{positions[(clip['id'], track['id'])]}</clipindex>"
                f"{group}</link>"
            )
        return "".join(links)

    declared_sources: set[str] = set()
    rendered_tracks: dict[str, list[str]] = {"video": [], "audio": []}
    for track in tracks:
        items: list[str] = []
        for clip in plan["clips"]:
            key = (clip["id"], track["id"])
            if key not in records:
                continue
            record = records[key]
            layer = record["layer"]
            source_id = layer["source"]
            include_details = source_id not in declared_sources
            declared_sources.add(source_id)
            source = plan["sources"][source_id]
            source_name = Path(source["path"]).stem
            common = f"""<name>{html.escape(source_name)}</name>
              <enabled>{'FALSE' if layer.get('enabled') is False else 'TRUE'}</enabled>
              <duration>{clip['duration_frames']}</duration>
              <start>{clip['timeline_start_frame']}</start>
              <end>{clip['timeline_start_frame'] + clip['duration_frames']}</end>
              <in>{layer['in_frame']}</in><out>{layer['out_frame']}</out>"""
            channel_count = ""
            if track["kind"] == "audio":
                channels = _source_meta(plan, source_id)["audio_channels"]
                channel_count = f"<channelcount>{channels}</channelcount>"
            items.append(
                f"""<clipitem id="{record['id']}">
              {common}
              {_file_block(plan, source_id, timebase, ntsc, include_details)}
              <sourcetrack><mediatype>{track['kind']}</mediatype><trackindex>{layer.get('source_track_index', 1)}</trackindex></sourcetrack>
              {channel_count}{links_for(clip)}
            </clipitem>"""
            )
        rendered_tracks[track["kind"]].append(
            f"<track><name>{html.escape(track.get('name', track['id']))}</name>{''.join(items)}</track>"
        )

    uid = str(uuid.uuid4())
    width = sequence["width"]
    height = sequence["height"]
    sample_rate = sequence.get("sample_rate", 48000)
    audio_channels = sequence.get("audio_channels", 2)
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="5"><sequence id="sequence-{uid}"><uuid>{uid}</uuid>
  <name>{html.escape(sequence.get('name', 'Perfect Cuts timeline'))}</name>
  <duration>{summary['duration_frames']}</duration>
  <rate><timebase>{timebase}</timebase><ntsc>{ntsc}</ntsc></rate>
  <in>0</in><out>{summary['duration_frames']}</out>
  <timecode><rate><timebase>{timebase}</timebase><ntsc>{ntsc}</ntsc></rate><frame>0</frame><displayformat>NDF</displayformat></timecode>
  <media><video><format><samplecharacteristics>
    <rate><timebase>{timebase}</timebase><ntsc>{ntsc}</ntsc></rate>
    <width>{width}</width><height>{height}</height><anamorphic>FALSE</anamorphic>
    <pixelaspectratio>square</pixelaspectratio><fielddominance>none</fielddominance>
  </samplecharacteristics></format>{''.join(rendered_tracks['video'])}</video>
  <audio><numOutputChannels>{audio_channels}</numOutputChannels><format><samplecharacteristics>
    <samplerate>{sample_rate}</samplerate><sampledepth>16</sampledepth>
  </samplecharacteristics></format>{''.join(rendered_tracks['audio'])}</audio></media>
</sequence></xmeml>
"""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(xml)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("output", type=Path, nargs="?")
    args = parser.parse_args()
    plan = load_plan(args.plan)
    output = args.output or Path(plan.get("output", args.plan.with_suffix(".xml")))
    result = export_plan(plan, output)
    print(result)


if __name__ == "__main__":
    main()
