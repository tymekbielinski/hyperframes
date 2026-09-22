#!/usr/bin/env python3
"""Build a fresh body-only timeline with native linked picture/audio ranges."""

from __future__ import annotations

import csv
import json
import sys
import urllib.parse
import uuid
from pathlib import Path
from xml.sax.saxutils import escape


TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import build_instantly_timeline as previous_edit  # noqa: E402


ROOT = Path("/Users/tymek/Desktop/Contentporary/Content Team/hyperframes")
OUT = ROOT / "videos" / "instantly-youtube" / "Instantly Body fresh perfect cut (C)"
XML_FILENAME = "2 EDIT - Premiere + Resolve body fresh v1 (C).xml"
SEQUENCE_NAME = "Instantly Body — fresh perfect cut v1"
FPS = 30


def _remove_verified_hidden_restarts(clip: dict) -> list[dict]:
    """Return native-range clip fragments after transcript/waveform-verified cuts."""
    source_range = (clip["in_frame"], clip["out_frame"])

    if source_range == (25556, 25907):
        cleaned = dict(clip)
        cleaned["in_frame"] = 25608
        cleaned["text"] = (
            "They just educate their viewers. They share some cool lessons and provide "
            "value. But they never really make videos about how to use Instantly."
        )
        cleaned["fresh_edit_reason"] = (
            "removed superseded false start: And they just educate users"
        )
        return [cleaned]

    if source_range == (36737, 37040):
        before = dict(clip)
        before["out_frame"] = 36909
        before["first_block"] = 417
        before["last_block"] = 417
        before["text"] = (
            "and I simply think that people are less reactive to this kind of content "
            "because we get tired of hearing that cold email."
        )
        before["fresh_edit_reason"] = "kept sentence before abandoned Is that restart"

        after = dict(clip)
        after["in_frame"] = 36934
        after["first_block"] = 418
        after["last_block"] = 419
        after["text"] = "that the new rules now are a reality."
        after["fresh_edit_reason"] = "resumed after abandoned Is that restart"
        return [before, after]

    return [clip]


def build_body_clips() -> tuple[list[dict], dict[str, dict]]:
    prior_clips, _, all_source_meta = previous_edit.load_and_edit()
    clips: list[dict] = []
    cursor = 0
    for prior in prior_clips:
        if prior["source"] != "body":
            continue
        clip = dict(prior)
        for field in (
            "video_in_frame",
            "video_out_frame",
            "picture_offset_frames",
            "picture_offset_reason",
        ):
            clip.pop(field, None)
        clip["source_number"] = 1
        for fragment in _remove_verified_hidden_restarts(clip):
            fragment["timeline_start"] = cursor
            clips.append(fragment)
            cursor += fragment["out_frame"] - fragment["in_frame"]
    return clips, {"body": all_source_meta["body"]}


def _source_file_block(meta: dict) -> str:
    name = escape(Path(meta["source"]).name)
    pathurl = "file://" + urllib.parse.quote(meta["source"])
    frames = round(meta["duration"] * meta["fps"])
    return f"""<file id="file-body">
      <name>{name}</name><pathurl>{pathurl}</pathurl>
      <rate><timebase>30</timebase><ntsc>FALSE</ntsc></rate><duration>{frames}</duration>
      <media><video><samplecharacteristics>
        <rate><timebase>30</timebase><ntsc>FALSE</ntsc></rate>
        <width>{meta['width']}</width><height>{meta['height']}</height>
        <anamorphic>FALSE</anamorphic><pixelaspectratio>square</pixelaspectratio>
        <fielddominance>none</fielddominance>
      </samplecharacteristics></video>
      <audio><samplecharacteristics><samplerate>{meta['samplerate']}</samplerate><sampledepth>16</sampledepth></samplecharacteristics></audio>
      </media></file>"""


def write_xml(clips: list[dict], source_meta: dict[str, dict]) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    meta = source_meta["body"]
    video_items: list[str] = []
    audio_items: list[str] = []
    for number, clip in enumerate(clips, 1):
        duration = clip["out_frame"] - clip["in_frame"]
        start = clip["timeline_start"]
        end = start + duration
        common = f"""<name>Instantly Body</name><enabled>TRUE</enabled><duration>{duration}</duration>
          <start>{start}</start><end>{end}</end><in>{clip['in_frame']}</in><out>{clip['out_frame']}</out>"""
        links = f"""
          <link><linkclipref>body-video-{number}</linkclipref><mediatype>video</mediatype><trackindex>1</trackindex><clipindex>{number}</clipindex></link>
          <link><linkclipref>body-audio-{number}</linkclipref><mediatype>audio</mediatype><trackindex>1</trackindex><clipindex>{number}</clipindex><groupindex>1</groupindex></link>"""
        video_items.append(
            f"""<clipitem id="body-video-{number}">{common}{_source_file_block(meta)}
              <sourcetrack><mediatype>video</mediatype><trackindex>1</trackindex></sourcetrack>{links}
            </clipitem>"""
        )
        audio_items.append(
            f"""<clipitem id="body-audio-{number}">{common}{_source_file_block(meta)}
              <sourcetrack><mediatype>audio</mediatype><trackindex>1</trackindex></sourcetrack><channelcount>2</channelcount>{links}
            </clipitem>"""
        )

    duration = sum(clip["out_frame"] - clip["in_frame"] for clip in clips)
    sequence_id = str(uuid.uuid4())
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="5"><sequence id="body-sequence-{sequence_id}"><uuid>{sequence_id}</uuid>
  <name>{SEQUENCE_NAME}</name><duration>{duration}</duration>
  <rate><timebase>30</timebase><ntsc>FALSE</ntsc></rate><in>0</in><out>{duration}</out>
  <timecode><rate><timebase>30</timebase><ntsc>FALSE</ntsc></rate><frame>0</frame><displayformat>NDF</displayformat></timecode>
  <media><video><format><samplecharacteristics>
    <rate><timebase>30</timebase><ntsc>FALSE</ntsc></rate><width>{meta['width']}</width><height>{meta['height']}</height>
    <anamorphic>FALSE</anamorphic><pixelaspectratio>square</pixelaspectratio><fielddominance>none</fielddominance>
  </samplecharacteristics></format><track>{''.join(video_items)}</track></video>
  <audio><numOutputChannels>2</numOutputChannels><format><samplecharacteristics><samplerate>{meta['samplerate']}</samplerate><sampledepth>16</sampledepth></samplecharacteristics></format>
  <track>{''.join(audio_items)}</track></audio></media>
</sequence></xmeml>
"""
    path = OUT / XML_FILENAME
    path.write_text(xml)
    return path


def write_package(clips: list[dict], source_meta: dict[str, dict]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    write_xml(clips, source_meta)

    duration = sum(clip["out_frame"] - clip["in_frame"] for clip in clips)
    cut_data = {
        "sequence_name": SEQUENCE_NAME,
        "fps": FPS,
        "width": source_meta["body"]["width"],
        "height": source_meta["body"]["height"],
        "duration_frames": duration,
        "sources": {"body": source_meta["body"]["source"]},
        "sync_policy": "native linked ranges; no picture or audio source offset",
        "clips": clips,
    }
    (OUT / "cut data (C).json").write_text(json.dumps(cut_data, indent=2))

    _, prior_rows, _ = previous_edit.load_and_edit()
    rows = [dict(row) for row in prior_rows if row["source"] == "body"]
    for row in rows:
        if row["status"] == "KEPT":
            block = int(row["block"])
            clip = next(
                item for item in clips if item["first_block"] <= block <= item["last_block"]
            )
            row["timeline_position"] = previous_edit.tc(clip["timeline_start"])
    with (OUT / "3 REVIVE - body cut decisions (C).csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    srt_entries = []
    for number, clip in enumerate(clips, 1):
        start = clip["timeline_start"]
        end = start + clip["out_frame"] - clip["in_frame"]
        srt_entries.append(
            f"{number}\n{previous_edit.srt_tc(start)} --> {previous_edit.srt_tc(end)}\n{clip['text']}\n"
        )
    (OUT / "6 CAPTIONS - body (C).srt").write_text("\n".join(srt_entries))

    readme = f"""FRESH BODY-ONLY PERFECT CUT — TIMELINE ONLY
================================================

Start with: {XML_FILENAME}

This sequence begins at 00:00:00:00 and references only Instantly Body.mp4.
Picture and audio use identical native source in/out ranges on every clip.
No picture offset, audio offset, speed change, intro, outro, or rendered MP4
is included. The sequence uses the source's native {source_meta['body']['width']}x{source_meta['body']['height']} frame size.

Edited duration: {duration / FPS:.2f} seconds.
"""
    (OUT / "README (C).txt").write_text(readme)


def main() -> None:
    clips, source_meta = build_body_clips()
    write_package(clips, source_meta)
    print(f"{len(clips)} body clips; {sum(c['out_frame'] - c['in_frame'] for c in clips) / FPS:.2f}s")
    print(OUT)


if __name__ == "__main__":
    main()
