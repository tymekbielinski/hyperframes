#!/usr/bin/env python3
"""Apply the approved body-only cut list to matching raw and screen-only files."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_SCRIPTS = ROOT / ".agents" / "skills" / "perfect-cuts" / "scripts"
sys.path.insert(0, str(SKILL_SCRIPTS))
from cut_plan import save_plan  # noqa: E402
from export_fcp7 import export_plan  # noqa: E402


MEDIA_DIR = Path("/Users/tymek/Desktop/Contentporary/Content Team/Youtube Videos/10 Instantly")
REFERENCE = (
    ROOT
    / "videos"
    / "instantly-youtube"
    / "Instantly Body fresh perfect cut (C)"
)
OUT = (
    ROOT
    / "videos"
    / "instantly-youtube"
    / "Instantly Body dual-source perfect cut (C)"
)
XML_FILENAME = "2 EDIT - Premiere dual-source body cut (C).xml"
SEQUENCE_NAME = "Instantly Body — dual-source perfect cut"
FPS = 30

SOURCE_PATHS = {
    "screen": MEDIA_DIR / "Instantly Body screen only.mp4",
    "raw": MEDIA_DIR / "Instantly Body raw.mp4",
}


def _probe(path: Path) -> dict:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=index,codec_type,width,height,r_frame_rate,"
            "duration,nb_frames,sample_rate,channels",
            "-of",
            "json",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)
    video = next(stream for stream in data["streams"] if stream["codec_type"] == "video")
    audio = next(stream for stream in data["streams"] if stream["codec_type"] == "audio")
    return {
        "path": str(path),
        "duration": float(data["format"]["duration"]),
        "width": int(video["width"]),
        "height": int(video["height"]),
        "fps": video["r_frame_rate"],
        "video_frames": int(video["nb_frames"]),
        "audio_duration": float(audio["duration"]),
        "samplerate": int(audio["sample_rate"]),
        "channels": int(audio["channels"]),
    }


def load_inputs() -> tuple[list[dict], dict[str, dict]]:
    reference = json.loads((REFERENCE / "cut data (C).json").read_text())
    clips = [dict(clip) for clip in reference["clips"]]
    sources = {label: _probe(path) for label, path in SOURCE_PATHS.items()}

    signatures = {
        (
            meta["width"],
            meta["height"],
            meta["fps"],
            meta["video_frames"],
            meta["samplerate"],
            meta["channels"],
            meta["audio_duration"],
        )
        for meta in sources.values()
    }
    if len(signatures) != 1:
        raise ValueError("raw and screen-only media do not share one exact timeline signature")
    if next(iter(sources.values()))["fps"] != "30/1":
        raise ValueError("approved body cuts require exact 30 fps replacement media")
    if max(clip["out_frame"] for clip in clips) > min(
        meta["video_frames"] for meta in sources.values()
    ):
        raise ValueError("approved cut list extends beyond replacement media")
    return clips, sources


def build_cut_plan(clips: list[dict], sources: dict[str, dict]) -> dict:
    raw = sources["raw"]
    plan_sources = {}
    for source_id, meta in sources.items():
        plan_sources[source_id] = {
            "path": meta["path"],
            "hyperframes_src": f"public/media/{Path(meta['path']).name}",
            "source_frames": meta["video_frames"],
            "fps": FPS,
            "width": meta["width"],
            "height": meta["height"],
            "sample_rate": meta["samplerate"],
            "audio_channels": meta["channels"],
        }
    plan_clips = []
    for number, clip in enumerate(clips, 1):
        duration = clip["out_frame"] - clip["in_frame"]
        plan_clips.append(
            {
                "id": f"cut-{number:03d}",
                "timeline_start_frame": clip["timeline_start"],
                "duration_frames": duration,
                "text": clip.get("text", ""),
                "layers": [
                    {"track": "screen-v1", "source": "screen", "in_frame": clip["in_frame"], "out_frame": clip["out_frame"]},
                    {"track": "camera-v2", "source": "raw", "in_frame": clip["in_frame"], "out_frame": clip["out_frame"]},
                    {"track": "dialogue-a1", "source": "raw", "in_frame": clip["in_frame"], "out_frame": clip["out_frame"]},
                ],
            }
        )
    return {
        "version": 1,
        "sequence": {
            "name": SEQUENCE_NAME,
            "fps": FPS,
            "width": raw["width"],
            "height": raw["height"],
            "sample_rate": raw["samplerate"],
            "audio_channels": raw["channels"],
            "gapless": True,
        },
        "sources": plan_sources,
        "tracks": [
            {"id": "screen-v1", "kind": "video", "index": 1, "name": "V1 — screen only fallback"},
            {"id": "camera-v2", "kind": "video", "index": 2, "name": "V2 — raw camera version"},
            {"id": "dialogue-a1", "kind": "audio", "index": 1, "name": "A1 — raw audio"},
        ],
        "clips": plan_clips,
        "provenance": {"cut_source": str(REFERENCE / "cut data (C).json")},
    }


def write_xml(clips: list[dict], sources: dict[str, dict]) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    return export_plan(build_cut_plan(clips, sources), OUT / XML_FILENAME)


def write_package(clips: list[dict], sources: dict[str, dict]) -> None:
    plan = build_cut_plan(clips, sources)
    write_xml(clips, sources)
    save_plan(plan, OUT / "cut-plan.json")
    duration = sum(clip["out_frame"] - clip["in_frame"] for clip in clips)
    data = {
        "sequence_name": SEQUENCE_NAME,
        "fps": FPS,
        "duration_frames": duration,
        "layout": {
            "V1": "screen-only fallback",
            "V2": "raw camera version",
            "A1": "raw audio only",
        },
        "sources": {label: meta["path"] for label, meta in sources.items()},
        "cut_source": str(REFERENCE / "cut data (C).json"),
        "clips": clips,
    }
    (OUT / "cut data (C).json").write_text(json.dumps(data, indent=2))

    for filename in (
        "3 REVIVE - body cut decisions (C).csv",
        "6 CAPTIONS - body (C).srt",
        "restart decisions (C).json",
    ):
        source = REFERENCE / filename
        if source.exists():
            shutil.copyfile(source, OUT / filename)

    readme = f"""DUAL-SOURCE BODY PERFECT CUT — TIMELINE ONLY
================================================

Import: {XML_FILENAME}

V2: Instantly Body raw.mp4 (camera version, visible by default)
V1: Instantly Body screen only.mp4 (matching fallback underneath)
A1: one copy of the raw audio; no doubled audio

Both video layers use the same {len(clips)} approved source ranges as the fresh
body-only perfect cut. Delete or disable a V2 camera section to reveal the
frame-matched V1 screen-only section beneath it. No render is included.

Edited duration: {duration / FPS:.2f} seconds ({duration} frames at {FPS} fps).
"""
    (OUT / "README (C).txt").write_text(readme)


def main() -> None:
    clips, sources = load_inputs()
    write_package(clips, sources)
    duration = sum(clip["out_frame"] - clip["in_frame"] for clip in clips)
    print(f"{len(clips)} cuts on both video layers; {duration} frames; {duration / FPS:.2f}s")
    print(OUT)


if __name__ == "__main__":
    main()
