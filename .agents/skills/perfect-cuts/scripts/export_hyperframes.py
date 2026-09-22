#!/usr/bin/env python3
"""Export a Perfect Cuts cut-plan v1 as an editable HyperFrames project."""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cut_plan import load_plan, validate_plan  # noqa: E402


def _seconds(frames: int, fps: float) -> str:
    return f"{frames / fps:.6f}".rstrip("0").rstrip(".") or "0"


def _attr(value: object) -> str:
    return html.escape(str(value), quote=True)


def export_plan(plan: dict, output_dir: str | Path) -> Path:
    summary = validate_plan(plan)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    sequence = plan["sequence"]
    fps = float(sequence["fps"])
    width = int(sequence["width"])
    height = int(sequence["height"])
    tracks = {track["id"]: track for track in plan["tracks"]}

    elements: list[str] = []
    for clip in plan["clips"]:
        start = _seconds(clip["timeline_start_frame"], fps)
        duration = _seconds(clip["duration_frames"], fps)
        for layer in clip["layers"]:
            track = tracks[layer["track"]]
            source = plan["sources"][layer["source"]]
            src = source.get("hyperframes_src", source["path"])
            media_start = _seconds(layer["in_frame"], fps)
            element_id = f"{clip['id']}-{track['id']}"
            if track["kind"] == "video":
                track_index = track["index"]
                elements.append(
                    f'      <video id="{_attr(element_id)}" src="{_attr(src)}" '
                    f'data-start="{start}" data-duration="{duration}" '
                    f'data-media-start="{media_start}" data-track-index="{track_index}" '
                    'muted playsinline></video>'
                )
            else:
                track_index = 10 + track["index"]
                elements.append(
                    f'      <audio id="{_attr(element_id)}" src="{_attr(src)}" '
                    f'data-start="{start}" data-duration="{duration}" '
                    f'data-media-start="{media_start}" data-track-index="{track_index}"></audio>'
                )

    duration = _seconds(summary["duration_frames"], fps)
    title = html.escape(sequence.get("name", "Perfect Cuts timeline"))
    document = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={width}, height={height}" />
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ box-sizing: border-box; }}
      html, body {{ margin: 0; width: {width}px; height: {height}px; overflow: hidden; background: #000; }}
      #root {{ position: relative; width: {width}px; height: {height}px; overflow: hidden; background: #000; }}
      video {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: contain; background: #000; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{duration}" data-fps="{_attr(sequence['fps'])}" data-width="{width}" data-height="{height}">
{chr(10).join(elements)}
    </div>
    <script>window.__timelines["main"] = gsap.timeline({{ paused: true }});</script>
  </body>
</html>
"""
    index = output / "index.html"
    index.write_text(document)
    (output / "cut-plan.json").write_text(json.dumps(plan, indent=2) + "\n")
    config = {
        "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
        "media": {"autoProxy": True},
        "authoringSkill": "general-video",
    }
    (output / "hyperframes.json").write_text(json.dumps(config, indent=2) + "\n")
    return index


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    plan = load_plan(args.plan)
    index = export_plan(plan, args.output_dir)
    print(index)


if __name__ == "__main__":
    main()
