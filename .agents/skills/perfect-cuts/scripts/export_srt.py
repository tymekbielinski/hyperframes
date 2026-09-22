#!/usr/bin/env python3
"""Generate edited-timeline SRT captions from a Perfect Cuts plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def ts(seconds: float) -> str:
    milliseconds = int(round(seconds * 1000))
    return (
        f"{milliseconds // 3_600_000:02d}:"
        f"{milliseconds % 3_600_000 // 60_000:02d}:"
        f"{milliseconds % 60_000 // 1000:02d},"
        f"{milliseconds % 1000:03d}"
    )


def export_plan(plan: dict, output_path: str | Path) -> Path:
    is_v1 = plan.get("version") == 1
    fps = float(plan["sequence"]["fps"] if is_v1 else plan["fps"])
    blocks: list[str] = []
    legacy_cursor = 0
    subtitle_number = 0
    for clip in plan.get("clips", []):
        if is_v1:
            start_frame = clip["timeline_start_frame"]
            duration_frames = clip["duration_frames"]
        else:
            start_frame = legacy_cursor
            duration_frames = clip["out_frame"] - clip["in_frame"]
            legacy_cursor += duration_frames
        text = clip.get("text", "").strip()
        if not text:
            continue
        subtitle_number += 1
        start = start_frame / fps
        end = (start_frame + duration_frames) / fps
        blocks.append(f"{subtitle_number}\n{ts(start)} --> {ts(end)}\n{text}\n")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(blocks))
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text())
    result = export_plan(plan, args.output)
    print(result)


if __name__ == "__main__":
    main()
