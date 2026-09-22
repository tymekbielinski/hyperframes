#!/usr/bin/env python3
"""Fail when an edited cut list still contains likely spoken restarts."""

from __future__ import annotations

import json
import re
import sys
import argparse
from pathlib import Path


def tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", text.lower())


RESTART_FILLERS = {"am", "are", "is", "was", "were", "actually", "uh", "um"}


def without_restart_fillers(items: list[str]) -> list[str]:
    return [item for item in items if item not in RESTART_FILLERS]


def adjacent_repeat(items: list[str]) -> tuple[int, int, list[str]] | None:
    for size in range(min(8, len(items) // 2), 0, -1):
        for start in range(len(items) - 2 * size + 1):
            phrase = items[start : start + size]
            if phrase == items[start + size : start + 2 * size]:
                return start, size, phrase
    return None


def interrupted_repeat(items: list[str]) -> tuple[int, int, list[str]] | None:
    """Find a phrase restarted after one to five abandoned words."""
    # Three words plus a very short interruption is a strong restart signal.
    # Two-word recurrences and longer gaps are common normal speech ("of the",
    # parallel questions, lists), so leave those to the boundary/window audit.
    for size in range(min(8, len(items) // 2), 2, -1):
        for start in range(len(items) - 2 * size):
            phrase = items[start : start + size]
            for gap in range(1, 3):
                again = start + size + gap
                if again + size > len(items):
                    break
                if phrase == items[again : again + size]:
                    return start, size, phrase
    return None


def boundary_overlap(left: list[str], right: list[str]) -> list[str]:
    limit = min(10, len(left), len(right))
    for size in range(limit, 2, -1):
        if left[-size:] == right[:size]:
            return right[:size]
    tail = left[-16:]
    for size in range(min(10, len(right)), 2, -1):
        prefix = right[:size]
        if any(tail[pos : pos + size] == prefix for pos in range(len(tail) - size + 1)):
            return prefix
    simple_left = without_restart_fillers(left)[-12:]
    simple_right = without_restart_fillers(right)
    for size in range(min(6, len(simple_left), len(simple_right)), 1, -1):
        prefix = simple_right[:size]
        if any(
            simple_left[pos : pos + size] == prefix
            for pos in range(len(simple_left) - size + 1)
        ):
            return prefix
    return []


def find_candidates(clips: list[dict]) -> list[dict]:
    candidates = []
    for index, clip in enumerate(clips):
        clip_tokens = tokens(clip.get("text", ""))
        repeat = adjacent_repeat(clip_tokens)
        if repeat:
            start, size, phrase = repeat
            candidates.append(
                {
                    "id": f"internal-{index}-{start}-{size}",
                    "left_clip": index,
                    "right_clip": index,
                    "phrase": " ".join(phrase),
                }
            )
        interrupted = interrupted_repeat(clip_tokens)
        if interrupted:
            start, size, phrase = interrupted
            candidates.append(
                {
                    "id": f"internal-interrupted-{index}-{start}-{size}",
                    "left_clip": index,
                    "right_clip": index,
                    "phrase": " ".join(phrase),
                }
            )
    for right_index in range(1, len(clips)):
        right = tokens(clips[right_index].get("text", ""))
        best = None
        for left_index in range(max(0, right_index - 4), right_index):
            left_text = " ".join(
                clip.get("text", "") for clip in clips[left_index:right_index]
            )
            overlap = boundary_overlap(tokens(left_text), right)
            if overlap and (best is None or len(overlap) > len(best[1])):
                best = (left_index, overlap)
        if best:
            left_index, overlap = best
            candidates.append(
                {
                    "id": f"boundary-{left_index}-{right_index}",
                    "left_clip": left_index,
                    "right_clip": right_index,
                    "phrase": " ".join(overlap),
                }
            )
            continue
        left_tail = tokens(clips[right_index - 1].get("text", ""))[-8:]
        right_head = right[:8]
        combined = left_tail + right_head
        repeat = adjacent_repeat(combined)
        if repeat:
            start, size, phrase = repeat
            boundary = len(left_tail)
            if start < boundary < start + 2 * size:
                candidates.append(
                    {
                        "id": f"boundary-stutter-{right_index - 1}-{right_index}",
                        "left_clip": right_index - 1,
                        "right_clip": right_index,
                        "phrase": " ".join(phrase),
                    }
                )
    return candidates


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cuts")
    parser.add_argument("--decisions")
    args = parser.parse_args()
    data = json.loads(Path(args.cuts).read_text())
    allow = {}
    if args.decisions:
        allow = json.loads(Path(args.decisions).read_text()).get("allow", {})
    candidates = find_candidates(data.get("clips", []))
    unresolved = [candidate for candidate in candidates if not allow.get(candidate["id"], "").strip()]
    if not unresolved:
        print("restart audit: 0 unresolved candidates")
        if candidates:
            print(f"restart audit: {len(candidates)} documented intentional repetition(s)")
        return 0
    print(f"restart audit: {len(unresolved)} unresolved candidate(s)")
    for candidate in unresolved:
        print(
            f"{candidate['id']}: clips {candidate['left_clip']}->{candidate['right_clip']} "
            f"repeat '{candidate['phrase']}'"
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
