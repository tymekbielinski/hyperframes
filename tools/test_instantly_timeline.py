import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("build_instantly_timeline.py")
SPEC = importlib.util.spec_from_file_location("build_instantly_timeline", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class InstantlyTimelineRegressionTests(unittest.TestCase):
    def test_full_builder_emits_generic_plan_with_independent_picture_ranges(self):
        clips, _, source_meta = MODULE.load_and_edit()
        plan = MODULE.build_cut_plan(clips, source_meta)
        self.assertEqual(plan["version"], 1)
        body = next(
            clip
            for clip in plan["clips"]
            if clip.get("text", "").startswith("If you build trust with hours")
        )
        picture = next(layer for layer in body["layers"] if layer["track"] == "picture-v1")
        audio = next(layer for layer in body["layers"] if layer["track"] == "dialogue-a1")
        self.assertEqual(picture["in_frame"], audio["in_frame"] + 22)
        self.assertEqual(picture["out_frame"], audio["out_frame"] + 22)

    def test_rebuild_uses_a_new_import_identity(self):
        self.assertEqual(
            MODULE.XML_FILENAME,
            "2 EDIT - Premiere + Resolve v6 (C).xml",
        )
        self.assertIn("v6", MODULE.SEQUENCE_NAME)

    def test_reported_body_take_can_offset_picture_without_moving_audio(self):
        clips, _, source_meta = MODULE.load_and_edit()
        clip = next(
            item
            for item in clips
            if item["source"] == "body"
            and item["first_block"] == 17
            and item["last_block"] == 20
        )
        self.assertEqual(clip["in_frame"], 1696)
        self.assertEqual(clip["out_frame"], 2147)
        self.assertEqual(clip["video_in_frame"], 1718)
        self.assertEqual(clip["video_out_frame"], 2169)
        self.assertEqual(clip["picture_offset_frames"], 22)
        self.assertTrue(clip["picture_offset_reason"])

        MODULE.write_xml(clips, source_meta)
        import xml.etree.ElementTree as ET

        root = ET.parse(MODULE.OUT / MODULE.XML_FILENAME).getroot()
        videos = root.findall(".//media/video/track/clipitem")
        audios = root.findall(".//media/audio/track/clipitem")
        index = clips.index(clip)
        self.assertEqual(int(videos[index].findtext("in")), 1718)
        self.assertEqual(int(videos[index].findtext("out")), 2169)
        self.assertEqual(int(audios[index].findtext("in")), 1696)
        self.assertEqual(int(audios[index].findtext("out")), 2147)
        self.assertEqual(
            int(videos[index].findtext("end")) - int(videos[index].findtext("start")),
            int(audios[index].findtext("end")) - int(audios[index].findtext("start")),
        )

    def test_verified_body_source_offset_applies_to_every_body_clip(self):
        clips, _, _ = MODULE.load_and_edit()
        body_clips = [clip for clip in clips if clip["source"] == "body"]
        self.assertTrue(body_clips)

        for clip in body_clips:
            self.assertEqual(clip["video_in_frame"], clip["in_frame"] + 22)
            self.assertEqual(clip["video_out_frame"], clip["out_frame"] + 22)
            self.assertEqual(clip["picture_offset_frames"], 22)
            self.assertTrue(clip["picture_offset_reason"])

    def test_confirmed_restart_blocks_are_not_kept(self):
        clips, _, _ = MODULE.load_and_edit()
        kept = {
            (clip["source"], block)
            for clip in clips
            for block in range(clip["first_block"], clip["last_block"] + 1)
        }
        removed = {
            ("intro", 0),
            ("intro", 4),
            ("intro", 5),
            ("intro", 16),
            ("intro", 35),
            ("intro", 46),
            ("intro", 48),
            ("intro", 51),
            ("intro", 52),
            ("body", 321),
            ("body", 52),
            ("body", 123),
            ("body", 149),
            ("body", 150),
            ("body", 320),
            ("body", 322),
            ("body", 323),
            ("body", 324),
            ("body", 368),
            ("body", 495),
            ("body", 175),
            ("body", 465),
            ("body", 470),
            ("body", 471),
            ("body", 480),
            ("body", 531),
            ("body", 552),
            ("body", 595),
            ("body", 610),
            ("body", 631),
            ("body", 640),
            ("body", 641),
            ("body", 647),
            ("body", 661),
            ("body", 683),
            ("body", 684),
            ("body", 729),
            ("body", 730),
            ("body", 757),
            ("body", 759),
            ("body", 832),
            ("body", 438),
            ("body", 28),
            ("body", 444),
            ("body", 467),
            ("body", 710),
            ("body", 715),
            ("body", 716),
            ("body", 718),
            ("body", 143),
            ("body", 536),
            ("body", 821),
            ("body", 822),
            ("body", 625),
            ("body", 770),
            ("body", 776),
            ("body", 777),
            ("body", 778),
            ("body", 828),
            ("outro", 10),
            ("outro", 11),
            ("outro", 4),
            ("outro", 6),
            ("outro", 16),
            ("outro", 21),
            ("outro", 22),
            ("outro", 41),
            ("outro", 38),
        }
        self.assertTrue(removed.isdisjoint(kept), removed & kept)
        self.assertIn(("body", 623), kept)

    def test_premiere_only_restarts_have_surgical_boundaries(self):
        clips, _, _ = MODULE.load_and_edit()

        body_27 = next(
            clip
            for clip in clips
            if clip["source"] == "body" and clip["last_block"] == 27
        )
        self.assertEqual(body_27["out_frame"], 2825)
        self.assertTrue(body_27["text"].endswith("channel"))

        body_439 = next(
            clip
            for clip in clips
            if clip["source"] == "body" and clip["first_block"] == 439
        )
        self.assertEqual(body_439["in_frame"], 39065)
        self.assertTrue(body_439["text"].startswith("We only had 100,000"))

        body_793 = next(
            clip
            for clip in clips
            if clip["source"] == "body" and clip["last_block"] == 793
        )
        self.assertEqual(body_793["out_frame"], 72905)

        body_719 = next(
            clip
            for clip in clips
            if clip["source"] == "body" and clip["first_block"] == 719
        )
        self.assertEqual(body_719["in_frame"], 65035)
        self.assertTrue(body_719["text"].startswith("Or are they trying"))

        body_144 = next(
            clip
            for clip in clips
            if clip["source"] == "body" and clip["first_block"] == 144
        )
        self.assertEqual(body_144["in_frame"], 12337)

        body_537 = next(
            clip
            for clip in clips
            if clip["source"] == "body" and clip["first_block"] == 537
        )
        self.assertEqual(body_537["in_frame"], 47150)

        body_823 = next(
            clip
            for clip in clips
            if clip["source"] == "body" and clip["first_block"] == 823
        )
        self.assertEqual(body_823["in_frame"], 75225)

    def test_single_block_stutter_can_be_split_without_dropping_the_sentence(self):
        clips, _, _ = MODULE.load_and_edit()
        fragments = [
            clip
            for clip in clips
            if clip["source"] == "body"
            and clip["first_block"] == 522
            and clip["last_block"] == 522
        ]
        self.assertEqual(len(fragments), 2)
        self.assertEqual(fragments[0]["out_frame"], 46046)
        self.assertEqual(fragments[1]["in_frame"], 46053)

    def test_outro_resources_clause_ends_before_aborted_to_have(self):
        clips, _, _ = MODULE.load_and_edit()
        block_nine = next(
            clip
            for clip in clips
            if clip["source"] == "outro"
            and clip["first_block"] <= 9 <= clip["last_block"]
        )
        self.assertLessEqual(block_nine["out_frame"], 1009)
        self.assertEqual(block_nine["text"], "but you don't have internal resources")

    def test_within_block_restarts_use_frame_level_overrides(self):
        clips, _, _ = MODULE.load_and_edit()

        intro_47 = next(
            clip for clip in clips
            if clip["source"] == "intro" and clip["first_block"] == 47
        )
        self.assertTrue(intro_47["text"].startswith("That's exactly"))

        body_642 = next(
            clip for clip in clips
            if clip["source"] == "body" and clip["first_block"] == 642
        )
        self.assertTrue(body_642["text"].startswith("It's a trust infrastructure"))

        body_624 = next(
            clip for clip in clips
            if clip["source"] == "body" and clip["first_block"] == 624
        )
        self.assertGreaterEqual(body_624["in_frame"], 54774)
        self.assertTrue(body_624["text"].startswith("Instead of"))

    def test_premiere_transcript_restarts_use_verified_source_boundaries(self):
        clips, _, _ = MODULE.load_and_edit()

        expected_starts = {
            ("intro", 6): 571,
            ("intro", 36): 4163,
            ("intro", 47): 5218,
            ("intro", 49): 5454,
            ("intro", 53): 5997,
            ("body", 466): 41438,
            ("body", 472): 41961,
            ("body", 481): 42533,
            ("body", 632): 56427,
            ("body", 642): 57816,
            ("body", 649): 58338,
            ("body", 662): 59366,
            ("body", 731): 66097,
            ("body", 740): 66788,
            ("body", 754): 68953,
            ("body", 758): 69336,
            ("outro", 7): 470,
            ("outro", 17): 2518,
            ("outro", 23): 3304,
            ("outro", 42): 6588,
        }
        for key, expected in expected_starts.items():
            source, block = key
            clip = next(
                item
                for item in clips
                if item["source"] == source and item["first_block"] == block
            )
            self.assertEqual(clip["in_frame"], expected, key)

        expected_ends = {
            ("body", 594): 52318,
            ("body", 634): 56680,
            ("body", 638): 57492,
            ("body", 682): 61842,
            ("body", 753): 68920,
            ("outro", 40): 6508,
        }
        for key, expected in expected_ends.items():
            source, block = key
            clip = next(
                item
                for item in clips
                if item["source"] == source and item["first_block"] == block
            )
            self.assertEqual(clip["out_frame"], expected, key)

    def test_every_block_has_an_explicit_editorial_decision(self):
        _, rows, _ = MODULE.load_and_edit()
        self.assertTrue(rows)
        self.assertTrue(all(row["status"] in {"KEPT", "CUT"} for row in rows))
        self.assertTrue(all(row["decision"].strip() for row in rows))
        self.assertTrue(
            all(row["take_group"].strip() for row in rows if row["status"] == "KEPT")
        )
        self.assertNotIn("clean delivery", {row["decision"] for row in rows})


if __name__ == "__main__":
    unittest.main()
