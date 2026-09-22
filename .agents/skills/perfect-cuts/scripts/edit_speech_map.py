#!/usr/bin/env python3
"""Turn reviewed speech-map decisions into deterministic gapless source clips."""

from __future__ import annotations

import json
import math
from pathlib import Path


def _integer_keys(mapping: dict | None) -> dict:
    return {int(key): value for key, value in (mapping or {}).items()}


def _load_map(value: dict | str | Path) -> dict:
    if isinstance(value, dict):
        return value
    return json.loads(Path(value).read_text())


def timecode(frames: int, fps: int) -> str:
    return (
        f"{frames // (3600 * fps):02d}:"
        f"{frames % (3600 * fps) // (60 * fps):02d}:"
        f"{frames % (60 * fps) // fps:02d}:"
        f"{frames % fps:02d}"
    )


def build_edits(
    source_specs: list[dict],
    fps: int,
    gap_threshold_seconds: float = 0.6,
) -> tuple[list[dict], list[dict], dict[str, dict]]:
    """Apply explicit editorial decisions to one or more speech maps.

    The output retains the legacy flat clip shape used by existing projects.
    Feed these clips into a project adapter that creates cut-plan v1 layers.
    """
    all_clips: list[dict] = []
    log_rows: list[dict] = []
    source_meta: dict[str, dict] = {}
    timeline_frame = 0

    for source_number, item in enumerate(source_specs, 1):
        data = _load_map(item["map"])
        label = item["label"]
        source_meta[label] = data
        cut_reasons = _integer_keys(item.get("cuts"))
        trim_overrides = _integer_keys(item.get("trim_overrides"))
        split_overrides = _integer_keys(item.get("split_overrides"))
        picture_offsets = _integer_keys(item.get("picture_offsets"))
        picture_offset_reasons = _integer_keys(item.get("picture_offset_reasons"))
        source_picture_offset = int(item.get("picture_offset_frames", 0))
        source_picture_offset_reason = item.get("picture_offset_reason", "")
        blocks = data["blocks"]

        kept_flags = [
            bool(block.get("text", "").strip()) and int(block["i"]) not in cut_reasons
            for block in blocks
        ]

        index = 0
        while index < len(blocks):
            block = blocks[index]
            block_id = int(block["i"])
            if not kept_flags[index]:
                index += 1
                continue

            if block_id in split_overrides:
                for fragment in split_overrides[block_id]:
                    in_frame = int(fragment["in_frame"])
                    out_frame = int(fragment["out_frame"])
                    picture_offset = int(
                        picture_offsets.get(block_id, source_picture_offset)
                    )
                    clip = {
                        "source": label,
                        "source_number": source_number,
                        "take_group": f"{label}-delivery-{len(all_clips) + 1}",
                        "first_block": block_id,
                        "last_block": block_id,
                        "in_frame": in_frame,
                        "out_frame": out_frame,
                        "video_in_frame": in_frame + picture_offset,
                        "video_out_frame": out_frame + picture_offset,
                        "text": fragment["text"],
                        "timeline_start": timeline_frame,
                    }
                    if picture_offset:
                        clip["picture_offset_frames"] = picture_offset
                        clip["picture_offset_reason"] = picture_offset_reasons.get(
                            block_id, source_picture_offset_reason
                        )
                    all_clips.append(clip)
                    timeline_frame += out_frame - in_frame
                index += 1
                continue

            first = index
            last = index
            while last + 1 < len(blocks) and kept_flags[last + 1]:
                current_id = int(blocks[last]["i"])
                next_id = int(blocks[last + 1]["i"])
                if (
                    current_id in trim_overrides
                    or next_id in trim_overrides
                    or next_id in split_overrides
                    or float(blocks[last].get("gap_after", 0)) >= gap_threshold_seconds
                ):
                    break
                last += 1

            first_block = blocks[first]
            last_block = blocks[last]
            first_id = int(first_block["i"])
            last_id = int(last_block["i"])
            in_frame = math.floor(float(first_block["onset"]) * fps)
            out_frame = math.ceil(float(last_block["end"]) * fps) + 1
            if first == last and first_id in trim_overrides:
                override = trim_overrides[first_id]
                in_frame = int(override.get("in_frame", in_frame))
                out_frame = int(override.get("out_frame", out_frame))
            text = " ".join(
                candidate["text"].strip()
                for candidate in blocks[first : last + 1]
                if candidate.get("text", "").strip()
            )
            if first == last and first_id in trim_overrides:
                text = trim_overrides[first_id].get("text", text)
            picture_offset = int(picture_offsets.get(first_id, source_picture_offset))
            clip = {
                "source": label,
                "source_number": source_number,
                "take_group": f"{label}-delivery-{len(all_clips) + 1}",
                "first_block": first_id,
                "last_block": last_id,
                "in_frame": in_frame,
                "out_frame": out_frame,
                "video_in_frame": in_frame + picture_offset,
                "video_out_frame": out_frame + picture_offset,
                "text": text,
                "timeline_start": timeline_frame,
            }
            if picture_offset:
                clip["picture_offset_frames"] = picture_offset
                clip["picture_offset_reason"] = picture_offset_reasons.get(
                    first_id, source_picture_offset_reason
                )
            all_clips.append(clip)
            timeline_frame += out_frame - in_frame
            index = last + 1

        clip_by_block = {}
        for clip in all_clips:
            if clip["source"] != label:
                continue
            for block_index in range(clip["first_block"], clip["last_block"] + 1):
                clip_by_block.setdefault(block_index, clip)
        for block in blocks:
            block_id = int(block["i"])
            if block_id in clip_by_block:
                clip = clip_by_block[block_id]
                offset = math.floor(float(block["onset"]) * fps) - clip["in_frame"]
                timeline_position = timecode(clip["timeline_start"] + max(offset, 0), fps)
                status = "KEPT"
                take_group = clip["take_group"]
                decision = (
                    "selected delivery; begins final take group"
                    if block_id == clip["first_block"]
                    else "grammatical continuation within selected delivery"
                )
            else:
                timeline_position = ""
                status = "CUT"
                take_group = ""
                decision = cut_reasons.get(block_id, "non-speech / mouth noise")
            log_rows.append(
                {
                    "source": label,
                    "block": block_id,
                    "status": status,
                    "take_group": take_group,
                    "source_in": timecode(math.floor(float(block["onset"]) * fps), fps),
                    "source_out": timecode(math.ceil(float(block["end"]) * fps) + 1, fps),
                    "timeline_position": timeline_position,
                    "text": block.get("text", "").strip(),
                    "decision": decision,
                    "reason": decision,
                }
            )

    return all_clips, log_rows, source_meta
