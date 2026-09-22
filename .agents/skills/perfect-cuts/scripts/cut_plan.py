#!/usr/bin/env python3
"""Validate the Contentporary Perfect Cuts cut-plan v1 format."""

from __future__ import annotations

import json
import math
import argparse
from pathlib import Path
from typing import Any


def _integer(value: Any, label: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be an integer")
    if value < minimum:
        raise ValueError(f"{label} must be at least {minimum}")
    return value


def _number(value: Any, label: str, minimum: float = 0) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a number")
    result = float(value)
    if not math.isfinite(result) or result <= minimum:
        raise ValueError(f"{label} must be greater than {minimum}")
    return result


def validate_plan(plan: dict) -> dict:
    """Validate a cut plan and return useful derived values.

    A layer consumes one source frame for every timeline frame. Different layers
    may start at different source frames, but their durations must be identical.
    This invariant prevents cut-induced picture/audio drift.
    """
    if not isinstance(plan, dict):
        raise ValueError("cut plan must be a JSON object")
    if plan.get("version") != 1:
        raise ValueError("cut plan version must be 1")

    sequence = plan.get("sequence")
    if not isinstance(sequence, dict):
        raise ValueError("sequence must be an object")
    sequence_fps = _number(sequence.get("fps"), "sequence.fps")
    _integer(sequence.get("width"), "sequence.width", 1)
    _integer(sequence.get("height"), "sequence.height", 1)
    _integer(sequence.get("sample_rate", 48000), "sequence.sample_rate", 1)
    _integer(sequence.get("audio_channels", 2), "sequence.audio_channels", 1)

    sources = plan.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("sources must be a non-empty object")
    for source_id, source in sources.items():
        if not source_id or not isinstance(source, dict):
            raise ValueError("each source must have a non-empty id and object metadata")
        if not isinstance(source.get("path"), str) or not source["path"]:
            raise ValueError(f"source {source_id!r} requires path")
        if "fps" in source:
            source_fps = _number(source["fps"], f"sources.{source_id}.fps")
            if abs(source_fps - sequence_fps) > 0.001:
                raise ValueError(
                    f"source {source_id!r} frame rate {source_fps} does not match "
                    f"sequence frame rate {sequence_fps}"
                )
        if "source_frames" in source:
            _integer(source["source_frames"], f"sources.{source_id}.source_frames", 1)

    tracks = plan.get("tracks")
    if not isinstance(tracks, list) or not tracks:
        raise ValueError("tracks must be a non-empty array")
    tracks_by_id: dict[str, dict] = {}
    occupied: set[tuple[str, int]] = set()
    for track in tracks:
        if not isinstance(track, dict) or not isinstance(track.get("id"), str):
            raise ValueError("each track requires a string id")
        track_id = track["id"]
        if track_id in tracks_by_id:
            raise ValueError(f"duplicate track id {track_id!r}")
        kind = track.get("kind")
        if kind not in {"video", "audio"}:
            raise ValueError(f"track {track_id!r} kind must be video or audio")
        index = _integer(track.get("index"), f"track {track_id!r} index", 1)
        lane = (kind, index)
        if lane in occupied:
            raise ValueError(f"duplicate {kind} track index {index}")
        occupied.add(lane)
        tracks_by_id[track_id] = track

    clips = plan.get("clips")
    if not isinstance(clips, list) or not clips:
        raise ValueError("clips must be a non-empty array")
    clip_ids: set[str] = set()
    expected_start = 0
    duration_frames = 0
    for clip_index, clip in enumerate(clips):
        label = f"clips[{clip_index}]"
        if not isinstance(clip, dict) or not isinstance(clip.get("id"), str):
            raise ValueError(f"{label} requires a string id")
        if clip["id"] in clip_ids:
            raise ValueError(f"duplicate clip id {clip['id']!r}")
        clip_ids.add(clip["id"])
        start = _integer(clip.get("timeline_start_frame"), f"{label}.timeline_start_frame")
        duration = _integer(clip.get("duration_frames"), f"{label}.duration_frames", 1)
        if sequence.get("gapless", True) and start != expected_start:
            raise ValueError(
                f"{label} breaks the gapless timeline: expected {expected_start}, got {start}"
            )
        expected_start = start + duration
        duration_frames = max(duration_frames, expected_start)

        layers = clip.get("layers")
        if not isinstance(layers, list) or not layers:
            raise ValueError(f"{label}.layers must be a non-empty array")
        seen_tracks: set[str] = set()
        for layer_index, layer in enumerate(layers):
            layer_label = f"{label}.layers[{layer_index}]"
            if not isinstance(layer, dict):
                raise ValueError(f"{layer_label} must be an object")
            track_id = layer.get("track")
            source_id = layer.get("source")
            if track_id not in tracks_by_id:
                raise ValueError(f"{layer_label} references unknown track {track_id!r}")
            if track_id in seen_tracks:
                raise ValueError(f"{label} has more than one layer on track {track_id!r}")
            seen_tracks.add(track_id)
            if source_id not in sources:
                raise ValueError(f"{layer_label} references unknown source {source_id!r}")
            in_frame = _integer(layer.get("in_frame"), f"{layer_label}.in_frame")
            out_frame = _integer(layer.get("out_frame"), f"{layer_label}.out_frame", 1)
            if out_frame <= in_frame:
                raise ValueError(f"{layer_label} out_frame must be after in_frame")
            if out_frame - in_frame != duration:
                raise ValueError(
                    f"{layer_label} source duration {out_frame - in_frame} does not match "
                    f"clip duration {duration}; this would cause drift"
                )
            source_frames = sources[source_id].get("source_frames")
            if source_frames is not None and out_frame > source_frames:
                raise ValueError(
                    f"{layer_label}.out_frame {out_frame} exceeds source duration {source_frames}"
                )

    return {
        "clip_count": len(clips),
        "duration_frames": duration_frames,
        "duration_seconds": duration_frames / float(sequence["fps"]),
        "track_count": len(tracks),
        "source_count": len(sources),
    }


def load_plan(path: str | Path) -> dict:
    plan = json.loads(Path(path).read_text())
    validate_plan(plan)
    return plan


def save_plan(plan: dict, path: str | Path) -> Path:
    validate_plan(plan)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(plan, indent=2) + "\n")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    args = parser.parse_args()
    plan = load_plan(args.plan)
    summary = validate_plan(plan)
    print(
        f"valid: {summary['clip_count']} clips, {summary['track_count']} tracks, "
        f"{summary['duration_frames']} frames ({summary['duration_seconds']:.3f}s)"
    )


if __name__ == "__main__":
    main()
