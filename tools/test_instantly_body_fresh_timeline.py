import importlib.util
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("build_instantly_body_fresh_timeline.py")


class FreshBodyTimelineTests(unittest.TestCase):
    def test_hidden_false_starts_are_removed_at_verified_waveform_boundaries(self):
        if not MODULE_PATH.exists():
            self.fail("fresh body-only timeline builder is not implemented")

        spec = importlib.util.spec_from_file_location("build_instantly_body_fresh_timeline", MODULE_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        clips, _ = module.build_body_clips()
        source_ranges = {(clip["in_frame"], clip["out_frame"]) for clip in clips}

        # "And they just educate users" is superseded by the clean restart.
        self.assertIn((25608, 25907), source_ranges)
        self.assertFalse(
            any(clip["in_frame"] < 25608 and clip["out_frame"] > 25556 for clip in clips)
        )

        # "Is that" is an abandoned mid-sentence restart between these fragments.
        self.assertTrue(any(clip["out_frame"] == 36909 for clip in clips))
        self.assertTrue(any(clip["in_frame"] == 36934 for clip in clips))
        self.assertFalse(
            any(clip["in_frame"] < 36934 and clip["out_frame"] > 36909 for clip in clips)
        )

    def test_body_only_timeline_uses_native_linked_source_ranges_from_zero(self):
        if not MODULE_PATH.exists():
            self.fail("fresh body-only timeline builder is not implemented")

        spec = importlib.util.spec_from_file_location("build_instantly_body_fresh_timeline", MODULE_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        clips, source_meta = module.build_body_clips()
        self.assertTrue(clips)
        self.assertEqual(set(source_meta), {"body"})

        cursor = 0
        for clip in clips:
            self.assertEqual(clip["source"], "body")
            self.assertEqual(clip["timeline_start"], cursor)
            self.assertNotIn("video_in_frame", clip)
            self.assertNotIn("video_out_frame", clip)
            cursor += clip["out_frame"] - clip["in_frame"]

        xml_path = module.write_xml(clips, source_meta)
        root = ET.parse(xml_path).getroot()
        videos = root.findall(".//media/video/track/clipitem")
        audios = root.findall(".//media/audio/track/clipitem")
        self.assertEqual(len(videos), len(audios))
        self.assertEqual(len(videos), len(clips))

        for video, audio in zip(videos, audios):
            for field in ("start", "end", "duration", "in", "out"):
                self.assertEqual(video.findtext(field), audio.findtext(field))

        xml_text = Path(xml_path).read_text()
        self.assertIn("Instantly Body.mp4", xml_text)
        self.assertNotIn("instantly intro.mp4", xml_text)
        self.assertNotIn("instantly outro.mp4", xml_text)


if __name__ == "__main__":
    unittest.main()
