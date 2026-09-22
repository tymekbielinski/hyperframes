#!/usr/bin/env python3
"""Generate a single-picture-track CMX3600 EDL from a Perfect Cuts plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def tc(frames: int, fps: float) -> str:
    fpsi = round(fps)
    value = int(frames)
    return (
        f"{value // (3600 * fpsi):02d}:"
        f"{value % (3600 * fpsi) // (60 * fpsi):02d}:"
        f"{value % (60 * fpsi) // fpsi:02d}:"
        f"{value % fpsi:02d}"
    )


def export_plan(plan: dict, output_path: str | Path, track_id: str | None = None) -> Path:
    is_v1 = plan.get("version") == 1
    if is_v1:
        fps = float(plan["sequence"]["fps"])
        name = plan["sequence"].get("name", "perfect cut")
        video_tracks = sorted(
            (track for track in plan["tracks"] if track["kind"] == "video"),
            key=lambda track: track["index"],
        )
        chosen = track_id or (video_tracks[0]["id"] if video_tracks else None)
        if chosen is None or chosen not in {track["id"] for track in video_tracks}:
            raise ValueError("EDL export requires a valid video track id")
        events = []
        for clip in plan["clips"]:
            layer = next((item for item in clip["layers"] if item["track"] == chosen), None)
            if layer is None:
                continue
            source = plan["sources"][layer["source"]]
            events.append(
                {
                    "in_frame": layer["in_frame"],
                    "out_frame": layer["out_frame"],
                    "timeline_start": clip["timeline_start_frame"],
                    "duration": clip["duration_frames"],
                    "source_name": Path(source["path"]).name,
                }
            )
    else:
        fps = float(plan["fps"])
        name = plan.get("sequence_name", "perfect cut")
        source_name = Path(plan["source"]).name
        cursor = 0
        events = []
        for clip in plan["clips"]:
            duration = clip["out_frame"] - clip["in_frame"]
            events.append(
                {
                    "in_frame": clip["in_frame"],
                    "out_frame": clip["out_frame"],
                    "timeline_start": cursor,
                    "duration": duration,
                    "source_name": source_name,
                }
            )
            cursor += duration

    lines = [f"TITLE: {name}", "FCM: NON-DROP FRAME", ""]
    for number, event in enumerate(events, 1):
        start = event["timeline_start"]
        end = start + event["duration"]
        lines.append(
            f"{number:03d}  AX       V     C        "
            f"{tc(event['in_frame'], fps)} {tc(event['out_frame'], fps)} "
            f"{tc(start, fps)} {tc(end, fps)}"
        )
        lines.append(f"* FROM CLIP NAME: {event['source_name']}")
        lines.append("")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--track", help="video track id for a v1 multi-track plan")
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text())
    result = export_plan(plan, args.output, args.track)
    print(result)


if __name__ == "__main__":
    main()
