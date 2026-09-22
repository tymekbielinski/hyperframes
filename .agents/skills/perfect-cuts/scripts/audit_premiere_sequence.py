#!/usr/bin/env python3
"""Audit an edited sequence against words independently observed by Premiere.

Premiere Pro stores Speech-to-Text results in FlatBuffers V216 ``.mfdc`` cache
files.  This script rebuilds every edited clip's text from those word timings,
then runs the normal Perfect Cuts restart detector on what Premiere heard—not
on the potentially cleaned or incomplete text declared in ``cuts.json``.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from audit_restarts import find_candidates  # noqa: E402


TICKS_PER_SECOND = 254_016_000_000


def _u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def _u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def _i32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<i", data, offset)[0]


def _i64(data: bytes, offset: int) -> int:
    return struct.unpack_from("<q", data, offset)[0]


def _field(data: bytes, table: int, number: int) -> int | None:
    """Return an absolute FlatBuffers field address, or None if absent."""
    vtable = table - _i32(data, table)
    vtable_size = _u16(data, vtable)
    slot = vtable + 4 + number * 2
    if slot + 2 > vtable + vtable_size:
        return None
    relative = _u16(data, slot)
    return table + relative if relative else None


def _indirect(data: bytes, address: int) -> int:
    return address + _u32(data, address)


def _vector(data: bytes, field_address: int) -> tuple[int, int]:
    vector = _indirect(data, field_address)
    return vector + 4, _u32(data, vector)


def _string(data: bytes, field_address: int) -> str:
    start = _indirect(data, field_address)
    length = _u32(data, start)
    return data[start + 4 : start + 4 + length].decode("utf-8", errors="replace")


def decode_mfdc(path: str | Path) -> list[dict]:
    """Decode word text and timing from a Premiere V216 transcript cache."""
    data = Path(path).read_bytes()
    root = _u32(data, 0)
    main_field = _field(data, root, 0)
    if main_field is None:
        raise ValueError(f"No transcript table in {path}")
    main = _indirect(data, main_field)
    segments_field = _field(data, main, 0)
    if segments_field is None:
        return []

    segment_entries, segment_count = _vector(data, segments_field)
    words: list[dict] = []
    for segment_index in range(segment_count):
        entry = segment_entries + segment_index * 4
        segment = _indirect(data, entry)
        words_field = _field(data, segment, 3)
        if words_field is None:
            continue
        word_entries, word_count = _vector(data, words_field)
        for word_index in range(word_count):
            word_entry = word_entries + word_index * 4
            word = _indirect(data, word_entry)
            start_field = _field(data, word, 0)
            duration_field = _field(data, word, 1)
            text_field = _field(data, word, 2)
            if start_field is None or duration_field is None or text_field is None:
                continue
            start = _i64(data, start_field) / TICKS_PER_SECOND
            duration = _i64(data, duration_field) / TICKS_PER_SECOND
            words.append(
                {
                    "text": _string(data, text_field),
                    "start": start,
                    "end": start + duration,
                }
            )
    return words


def rebuild_observed_clips(
    cuts: dict, premiere_words: dict[str, list[dict]]
) -> list[dict]:
    """Replace declared clip text with Premiere words falling inside each cut."""
    is_v1 = cuts.get("version") == 1
    fps = float(cuts["sequence"]["fps"] if is_v1 else cuts["fps"])
    track_kinds = {
        track["id"]: track["kind"] for track in cuts.get("tracks", [])
    }
    observed = []
    for clip in cuts.get("clips", []):
        if is_v1:
            layers = clip.get("layers", [])
            layer = next(
                (item for item in layers if track_kinds.get(item.get("track")) == "audio"),
                layers[0] if layers else None,
            )
            if layer is None:
                raise ValueError(f"clip {clip.get('id', '?')} has no auditable layer")
            source = layer["source"]
            in_frame = layer["in_frame"]
            out_frame = layer["out_frame"]
        else:
            source = clip.get("source", "source")
            in_frame = clip["in_frame"]
            out_frame = clip["out_frame"]
        start = float(in_frame) / fps
        end = float(out_frame) / fps
        selected = []
        for word in premiere_words.get(source, []):
            midpoint = (float(word["start"]) + float(word["end"])) / 2
            if start <= midpoint < end:
                selected.append(str(word["text"]).strip())
        rebuilt = dict(clip)
        rebuilt["declared_text"] = clip.get("text", "")
        rebuilt["text"] = " ".join(item for item in selected if item)
        observed.append(rebuilt)
    return observed


def _parse_cache(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("cache must be LABEL=/absolute/path.mfdc")
    label, raw_path = value.split("=", 1)
    if not label or not raw_path:
        raise argparse.ArgumentTypeError("cache must be LABEL=/absolute/path.mfdc")
    return label, Path(raw_path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cuts")
    parser.add_argument(
        "--cache",
        action="append",
        type=_parse_cache,
        required=True,
        help="source-label=/path/to/Premiere-transcript.mfdc (repeatable)",
    )
    parser.add_argument("--decisions")
    parser.add_argument("--observed-out")
    args = parser.parse_args()

    cuts = json.loads(Path(args.cuts).read_text())
    premiere_words = {label: decode_mfdc(path) for label, path in args.cache}
    observed = rebuild_observed_clips(cuts, premiere_words)
    if args.observed_out:
        output = dict(cuts)
        output["clips"] = observed
        Path(args.observed_out).write_text(json.dumps(output, indent=2) + "\n")

    allow = {}
    if args.decisions:
        allow = json.loads(Path(args.decisions).read_text()).get("allow", {})
    candidates = find_candidates(observed)
    unresolved = [
        candidate
        for candidate in candidates
        if not allow.get(candidate["id"], "").strip()
    ]
    if not unresolved:
        print("Premiere transcript audit: 0 unresolved candidates")
        if candidates:
            print(
                "Premiere transcript audit: "
                f"{len(candidates)} documented intentional repetition(s)"
            )
        return 0

    print(f"Premiere transcript audit: {len(unresolved)} unresolved candidate(s)")
    for candidate in unresolved:
        print(
            f"{candidate['id']}: clips {candidate['left_clip']}"
            f"->{candidate['right_clip']} repeat '{candidate['phrase']}'"
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
