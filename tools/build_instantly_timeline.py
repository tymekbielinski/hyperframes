#!/usr/bin/env python3
"""Build one gapless multi-source FCP7 timeline from Perfect Cuts speech maps."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_SCRIPTS = ROOT / ".agents" / "skills" / "perfect-cuts" / "scripts"
sys.path.insert(0, str(SKILL_SCRIPTS))
from edit_speech_map import build_edits  # noqa: E402
from cut_plan import save_plan  # noqa: E402
from export_edl import export_plan as export_edl_plan  # noqa: E402
from export_fcp7 import export_plan as export_fcp7_plan  # noqa: E402
from export_srt import export_plan as export_srt_plan  # noqa: E402


TMP = Path("/tmp/perfect-cuts-instantly")
OUT = ROOT / "videos" / "instantly-youtube" / "Instantly full perfect cut (C)"
FPS = 30
SEQ_W = 3840
SEQ_H = 2160
XML_FILENAME = "2 EDIT - Premiere + Resolve v6 (C).xml"
SEQUENCE_NAME = "Instantly YouTube — full perfect cut v6"


def expand_ranges(ranges: list[tuple[int, int, str]]) -> dict[int, str]:
    result: dict[int, str] = {}
    for start, end, reason in ranges:
        for index in range(start, end + 1):
            result[index] = reason
    return result


SOURCES = [
    {
        "label": "intro",
        "map": TMP / "intro-map.json",
        "cuts": expand_ranges([
            (0, 0, "Premiere transcript: short first take repeats at block 1"),
            (4, 5, "Premiere transcript: repeated verified-sources take; final delivery starts inside block 6"),
            (7, 8, "retake — later complete delivery kept"),
            (11, 15, "false start — complete delivery begins at block 16"),
            (16, 16, "short take — fuller delivery begins at block 18"),
            (17, 17, "false start fragment"),
            (22, 29, "abandoned delivery — no clean ending"),
            (30, 30, "false start — later delivery kept"),
            (33, 34, "repeated statistic — complete delivery follows"),
            (35, 35, "Premiere transcript: repeated 15-million-views take; final delivery starts inside block 36"),
            (37, 42, "repeated and abandoned phrase"),
            (44, 45, "retake — later complete delivery kept"),
            (46, 46, "Premiere transcript: short That's-exactly take repeats at block 47"),
            (48, 48, "Premiere transcript: first pulled-their-last-hundred take; complete delivery is block 49"),
            (51, 52, "Premiere transcript: two aborted and-sorted takes; complete delivery is block 53"),
            (56, 57, "repeated ending"),
            (58, 60, "CTA false starts — later delivery kept"),
            (62, 63, "mid-sentence restart"),
            (65, 69, "CTA false starts — later complete delivery kept"),
            (71, 78, "repeated CTA takes — final take kept"),
        ]),
        "trim_overrides": {
            6: {
                "in_frame": 571,
                "text": "and verified sources say that they added over $1 million in ARR to their business.",
            },
            36: {
                "in_frame": 4163,
                "text": "15 million views and number one channel in their niche.",
            },
            47: {
                "in_frame": 5218,
                "text": "That's exactly what I'm breaking down in this video.",
            },
            49: {
                "in_frame": 5454,
                "text": "I pulled the last 100 videos,",
            },
            53: {
                "in_frame": 5997,
                "text": "and sorted all of them into three kinds of videos.",
            },
        },
    },
    {
        "label": "body",
        "map": TMP / "body-map.json",
        "picture_offset_frames": 22,
        "picture_offset_reason": (
            "verified source-wide webcam picture delay at isolated speech onsets "
            "near 00:00:56, 00:25:03, 00:29:58, and 00:40:01"
        ),
        "cuts": expand_ranges([
            (2, 6, "false starts — complete framing begins at block 7"),
            (15, 16, "abandoned sentence"),
            (21, 23, "abandoned transition"),
            (28, 28, "Premiere transcript: block is the dangling So-that restart; its mislabeled channel word is retained at the end of block 27"),
            (29, 36, "false start — completed thought resumes at block 37"),
            (52, 52, "repeated phrase — fuller continuation begins at block 53"),
            (63, 64, "abandoned sentence"),
            (80, 82, "repeated transition"),
            (93, 97, "abandoned sentence"),
            (110, 116, "false start — later phrasing kept"),
            (123, 123, "repeated estimate — concise corrected estimate follows"),
            (129, 132, "false start — complete take begins at block 133"),
            (139, 142, "repeated transition — later take kept"),
            (143, 143, "Premiere transcript: first now-you-understand-the-math take; complete take begins inside block 144"),
            (146, 147, "false start — later take kept"),
            (149, 150, "repeated visual setup — cleaner continuation follows"),
            (155, 157, "mid-sentence restart"),
            (175, 175, "Premiere transcript: repeated or before copywriting techniques"),
            (192, 196, "false starts — complete explanation begins at block 197"),
            (203, 204, "abandoned sentence"),
            (211, 213, "repeated start — full take begins at block 214"),
            (217, 217, "false start"),
            (224, 224, "false start — stronger line follows"),
            (227, 227, "abandoned statistic"),
            (239, 239, "repeated phrase"),
            (253, 255, "false start — complete line begins at block 256"),
            (267, 272, "abandoned education transition"),
            (282, 289, "retake — fuller product explanation kept"),
            (309, 316, "mid-sentence restart"),
            (320, 324, "repeated question and false start — complete delivery begins at block 325"),
            (333, 334, "false start"),
            (338, 340, "repeated start — complete take begins at block 341"),
            (344, 346, "short retake — fuller take kept"),
            (363, 363, "mid-sentence restart"),
            (366, 366, "false start"),
            (368, 368, "repeated conjunction before corrected phrase"),
            (369, 369, "repeated ending"),
            (381, 381, "false start — complete sentence follows"),
            (394, 397, "false start"),
            (408, 416, "abandoned and repeated explanation"),
            (438, 438, "Premiere transcript: 'We only had one' false start; complete statistic begins inside block 439"),
            (444, 444, "Premiere transcript: first But-what-I'm-noticing take; complete take begins inside block 446"),
            (424, 426, "transition retakes — complete take follows"),
            (429, 431, "retake — fuller question follows"),
            (456, 457, "false start"),
            (463, 464, "abandoned qualification"),
            (465, 465, "Premiere transcript: first Maybe-in-case attempt; complete take starts inside block 466"),
            (467, 467, "Premiere transcript: first But-let's-assume-that take; complete take starts inside block 472"),
            (476, 479, "repeated setup"),
            (470, 471, "Premiere transcript: repeated let's-assume attempts; complete take starts inside block 472"),
            (480, 480, "Premiere transcript: isolated which before the complete question"),
            (491, 493, "false starts — clean teardown phrasing follows"),
            (495, 495, "mid-sentence restart — prior block is the clean grammatical take"),
            (501, 501, "repeated phrase"),
            (503, 508, "abandoned sentence"),
            (523, 529, "multiple false starts — complete take follows"),
            (531, 531, "Premiere transcript: first But-if-there-is-not take; complete take is block 532"),
            (533, 535, "abandoned phrasing"),
            (536, 536, "Premiere transcript: first Then-people-are-going-to attempt; complete take begins inside block 537"),
            (539, 543, "repeated point"),
            (552, 552, "Premiere transcript: first because-these-are take; complete take is block 553"),
            (561, 565, "repeated transition — final take kept"),
            (568, 569, "mid-sentence restart"),
            (582, 583, "false start"),
            (592, 593, "abandoned sentence"),
            (595, 595, "Premiere transcript: first demonstrated-how-to attempt"),
            (614, 614, "repeated start"),
            (610, 610, "Premiere transcript: duplicated that before the completed clause"),
            (621, 621, "repeated phrase"),
            (625, 625, "repeated phrase — already completed at the end of block 624"),
            (631, 631, "Premiere transcript: aborted videos-I-get attempt"),
            (640, 641, "Premiere transcript: repeated trust-infrastructure takes; final delivery starts in block 642"),
            (647, 647, "Premiere transcript: aborted If-you-build-trust take; complete delivery starts in block 649"),
            (655, 657, "retakes — final take kept"),
            (659, 660, "retake — more specific delivery kept"),
            (661, 661, "Premiere transcript: isolated It-should-answer take; complete delivery starts in block 662"),
            (668, 674, "false starts — clean conclusion begins at block 675"),
            (678, 680, "false starts — complete transition follows"),
            (683, 684, "Premiere transcript: garbled repeated ending after the complete operations question"),
            (691, 693, "abandoned sentence"),
            (697, 697, "repeated line"),
            (710, 710, "Premiere transcript: short one-on-one-formats take; complete strategy-teardown take follows"),
            (715, 716, "Premiere transcript: aborted second-question lead-in; complete question starts in block 717"),
            (718, 718, "Premiere transcript: first Or-are-they attempt; complete question starts inside block 719"),
            (721, 724, "abandoned sentence — complete point follows"),
            (729, 730, "Premiere transcript: aborted that-is-trying take; complete clause starts in block 731"),
            (751, 751, "false start"),
            (757, 757, "Premiere transcript: first problem-in-how-your-YouTube take; complete delivery is block 758"),
            (759, 759, "Premiere transcript: first Because-when-you-see take; complete delivery is block 760"),
            (755, 756, "mid-sentence restart"),
            (767, 768, "false start — cleaner explanation follows"),
            (770, 770, "mid-sentence restart — corrected clause follows"),
            (776, 778, "mid-sentence restart — corrected clause follows"),
            (780, 785, "multiple false starts — complete take follows"),
            (807, 808, "abandoned sentence — complete take follows"),
            (818, 820, "false start — complete take follows"),
            (821, 822, "Premiere transcript: you-end-up-paying-for-more false start; corrected clause begins inside block 823"),
            (828, 828, "repeated conjunction after mid-sentence restart"),
            (829, 829, "mid-sentence restart"),
            (832, 832, "Premiere transcript: first And-the-best-part take; complete delivery is block 833"),
            (836, 837, "abandoned ending; outro supplies the close"),
        ]),
        "trim_overrides": {
            27: {
                "out_frame": 2825,
                "text": "can you bring to your YouTube channel",
            },
            439: {
                "in_frame": 39065,
                "text": "We only had 100,000 views.",
            },
            144: {
                "in_frame": 12337,
                "text": "So now you understand the math behind the $1 million ARR.",
            },
            446: {
                "in_frame": 39907,
                "text": "But what I've noticed, after analyzing 100 videos",
            },
            466: {
                "in_frame": 41438,
                "text": "Maybe in case of Instantly that's not the most important KPI that they have for their YouTube",
            },
            472: {
                "in_frame": 41961,
                "text": "But let's assume that all of the bottom-of-the-funnel videos convert at 1% per",
            },
            481: {
                "in_frame": 42533,
                "text": "Which one of those brought the most subscriptions?",
            },
            594: {
                "out_frame": 52318,
                "text": "And instead of explaining how to actually fix these problems,",
            },
            632: {
                "in_frame": 56427,
                "text": "videos that are over 60 minutes get the most views.",
            },
            634: {
                "out_frame": 56680,
                "text": "for YouTube, the most important KPI is watch time.",
            },
            638: {
                "out_frame": 57492,
                "text": "So we can really take advantage of that because YouTube isn't just a traffic source,",
            },
            642: {
                "in_frame": 57816,
                "text": "It's a trust infrastructure system if you use it correctly.",
            },
            649: {
                "in_frame": 58338,
                "text": "If you build trust with hours of watch time,",
            },
            662: {
                "in_frame": 59366,
                "text": "It should answer objections before the demo calls.",
            },
            682: {
                "out_frame": 61842,
                "text": "How do you actually judge your YouTube operations?",
            },
            731: {
                "in_frame": 66097,
                "text": "that is trying to convert them to a free trial",
            },
            740: {
                "in_frame": 66788,
                "text": "people who are going through demos?",
            },
            753: {
                "out_frame": 68920,
                "text": "promises you YouTube results,",
            },
            754: {
                "in_frame": 68953,
                "text": "but can't really answer these questions,",
            },
            758: {
                "in_frame": 69336,
                "text": "Then there's definitely a problem in how your YouTube operations look right now.",
            },
            719: {
                "in_frame": 65035,
                "text": "Or are they trying to learn how to use it?",
            },
            537: {
                "in_frame": 47150,
                "text": "Then people are just going to feel like they've heard it already.",
            },
            823: {
                "in_frame": 75225,
                "text": "So you end up paying for the success they had before you and not really with you.",
            },
            793: {
                "out_frame": 72905,
                "text": "not really applying anything specific and new",
            },
            624: {
                "in_frame": 54774,
                "text": "Instead of just doing individual videos to get a lot of views, target anyone,",
            },
        },
        "split_overrides": {
            522: [
                {
                    "in_frame": 45971,
                    "out_frame": 46046,
                    "text": "And when someone's focusing on a lot of views for",
                },
                {
                    "in_frame": 46053,
                    "out_frame": 46078,
                    "text": "their videos,",
                },
            ],
        },
    },
    {
        "label": "outro",
        "map": TMP / "outro-map.json",
        "cuts": expand_ranges([
            (4, 4, "Premiere transcript: first across-three-stages take; complete take starts inside block 7"),
            (6, 6, "Premiere transcript: partial second take; complete take starts inside block 7"),
            (18, 20, "abandoned sentence — complete support line follows"),
            (10, 11, "mid-sentence restart — corrected scale clause follows"),
            (16, 16, "Premiere transcript: first And-because take; complete delivery starts inside block 17"),
            (21, 22, "Premiere transcript: repeated You-get attempts; complete delivery starts inside block 23"),
            (29, 30, "CTA false starts — later complete take kept"),
            (34, 34, "false start — complete worst-case line follows"),
            (38, 38, "mid-sentence restart — qualified-leads correction follows"),
            (41, 41, "Premiere transcript: repeated of-a lead-in; complete phrase starts inside block 42"),
        ]),
        "trim_overrides": {
            9: {
                "out_frame": 1009,
                "text": "but you don't have internal resources",
            },
            7: {
                "in_frame": 470,
                "text": "across three different stages of a YouTube funnel.",
            },
            17: {
                "in_frame": 2518,
                "text": "And because my client roster is limited to only five clients at a time,",
            },
            23: {
                "in_frame": 3304,
                "text": "You get real one-on-one support and strategy built specifically for your ICP,",
            },
            40: {
                "out_frame": 6508,
                "text": "And I've also posted this video that you can see on the screen right now, which is another great breakdown",
            },
            42: {
                "in_frame": 6588,
                "text": "of a successful YouTube channel.",
            },
        },
    },
]


def load_and_edit() -> tuple[list[dict], list[dict], dict]:
    return build_edits(SOURCES, fps=FPS, gap_threshold_seconds=0.6)


def build_cut_plan(clips: list[dict], source_meta: dict[str, dict]) -> dict:
    sources = {}
    for source_id, meta in source_meta.items():
        sources[source_id] = {
            "path": meta["source"],
            "hyperframes_src": f"public/media/{Path(meta['source']).name}",
            "fps": FPS,
            "source_frames": round(float(meta["duration"]) * FPS),
            "width": int(meta["width"]),
            "height": int(meta["height"]),
            "sample_rate": int(meta.get("samplerate", 48000)),
            "audio_channels": int(meta.get("channels") or 2),
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
                "source_blocks": {
                    "source": clip["source"],
                    "first": clip["first_block"],
                    "last": clip["last_block"],
                },
                "layers": [
                    {
                        "track": "picture-v1",
                        "source": clip["source"],
                        "in_frame": clip.get("video_in_frame", clip["in_frame"]),
                        "out_frame": clip.get("video_out_frame", clip["out_frame"]),
                    },
                    {
                        "track": "dialogue-a1",
                        "source": clip["source"],
                        "in_frame": clip["in_frame"],
                        "out_frame": clip["out_frame"],
                    },
                ],
            }
        )
    return {
        "version": 1,
        "sequence": {
            "name": SEQUENCE_NAME,
            "fps": FPS,
            "width": SEQ_W,
            "height": SEQ_H,
            "sample_rate": 48000,
            "audio_channels": 2,
            "gapless": True,
        },
        "sources": sources,
        "tracks": [
            {"id": "picture-v1", "kind": "video", "index": 1, "name": "V1 — picture"},
            {"id": "dialogue-a1", "kind": "audio", "index": 1, "name": "A1 — dialogue"},
        ],
        "clips": plan_clips,
    }


def write_xml(clips: list[dict], source_meta: dict[str, dict]) -> None:
    export_fcp7_plan(build_cut_plan(clips, source_meta), OUT / XML_FILENAME)


def write_srt(clips: list[dict], source_meta: dict[str, dict]) -> None:
    export_srt_plan(build_cut_plan(clips, source_meta), OUT / "6 CAPTIONS (C).srt")


def write_edl(clips: list[dict], source_meta: dict[str, dict]) -> None:
    export_edl_plan(
        build_cut_plan(clips, source_meta),
        OUT / "7 AVID + LEGACY (C).edl",
        track_id="picture-v1",
    )


def write_package(clips: list[dict], rows: list[dict], source_meta: dict[str, dict]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    plan = build_cut_plan(clips, source_meta)
    write_xml(clips, source_meta)
    write_srt(clips, source_meta)
    write_edl(clips, source_meta)

    with (OUT / "3 REVIVE - cut decisions (C).csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    duration = sum(c["out_frame"] - c["in_frame"] for c in clips)
    cut_data = {
        "sequence_name": SEQUENCE_NAME,
        "fps": FPS,
        "width": SEQ_W,
        "height": SEQ_H,
        "duration_frames": duration,
        "sources": {label: meta["source"] for label, meta in source_meta.items()},
        "clips": clips,
    }
    (OUT / "cut data (C).json").write_text(json.dumps(cut_data, indent=2))
    save_plan(plan, OUT / "cut-plan.json")

    readme = f"""PERFECT CUTS — TIMELINE-ONLY PACKAGE
====================================

Start with: {XML_FILENAME}

This is one continuous {duration / FPS:.2f}-second timeline in this order:
instantly intro.mp4 -> Instantly Body.mp4 -> instantly outro.mp4.

No rendered MP4 was created, as requested. The timeline links to the three
original source files. Keep them in their current folder or relink them inside
your editor if they are moved.

Premiere Pro: File -> Import -> choose the v6 XML. XML imports are snapshots,
so an already imported older sequence will not update when its source XML changes.
DaVinci Resolve: File -> Import Timeline -> choose the XML.

3 REVIVE - cut decisions (C).csv lists every detected speech block and why it
was kept or removed. The SRT is aligned to the edited timeline. The EDL is a
legacy fallback. cut data (C).json contains the reversible machine-readable edit.
cut-plan.json is the canonical reusable timeline used by the shared exporters.
"""
    (OUT / "README (C).txt").write_text(readme)


def main() -> None:
    clips, rows, source_meta = load_and_edit()
    write_package(clips, rows, source_meta)
    kept = sum(1 for row in rows if row["status"] == "KEPT")
    cut = len(rows) - kept
    duration = sum(c["out_frame"] - c["in_frame"] for c in clips) / FPS
    print(f"{len(clips)} timeline clips; {kept} blocks kept; {cut} blocks cut; {duration:.2f}s")
    print(OUT)


if __name__ == "__main__":
    main()
