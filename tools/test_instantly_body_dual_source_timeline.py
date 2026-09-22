import importlib.util
import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


TOOLS = Path(__file__).resolve().parent
MODULE_PATH = TOOLS / "build_instantly_body_dual_source_timeline.py"
REFERENCE_CUTS = (
    TOOLS.parent
    / "videos"
    / "instantly-youtube"
    / "Instantly Body fresh perfect cut (C)"
    / "cut data (C).json"
)


class DualSourceBodyTimelineTests(unittest.TestCase):
    def test_project_builder_emits_the_generic_cut_plan_shape(self):
        spec = importlib.util.spec_from_file_location(
            "build_instantly_body_dual_source_timeline", MODULE_PATH
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        clips, sources = module.load_inputs()
        plan = module.build_cut_plan(clips, sources)
        self.assertEqual(plan["version"], 1)
        self.assertEqual(
            [track["id"] for track in plan["tracks"]],
            ["screen-v1", "camera-v2", "dialogue-a1"],
        )
        self.assertEqual(len(plan["clips"]), len(clips))
        self.assertEqual(len(plan["clips"][0]["layers"]), 3)

    def test_identical_reference_cuts_are_stacked_on_both_video_sources(self):
        if not MODULE_PATH.exists():
            self.fail("dual-source body timeline builder is not implemented")

        spec = importlib.util.spec_from_file_location(
            "build_instantly_body_dual_source_timeline", MODULE_PATH
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        reference = json.loads(REFERENCE_CUTS.read_text())
        clips, sources = module.load_inputs()
        self.assertEqual(
            [(c["in_frame"], c["out_frame"]) for c in clips],
            [(c["in_frame"], c["out_frame"]) for c in reference["clips"]],
        )
        self.assertEqual(len(clips), 260)
        self.assertEqual(set(sources), {"screen", "raw"})

        xml_path = module.write_xml(clips, sources)
        root = ET.parse(xml_path).getroot()
        video_tracks = root.findall(".//media/video/track")
        audio_tracks = root.findall(".//media/audio/track")
        self.assertEqual(len(video_tracks), 2)
        self.assertEqual(len(audio_tracks), 1)

        screen_items = video_tracks[0].findall("clipitem")
        raw_items = video_tracks[1].findall("clipitem")
        audio_items = audio_tracks[0].findall("clipitem")
        self.assertEqual(len(screen_items), len(clips))
        self.assertEqual(len(raw_items), len(clips))
        self.assertEqual(len(audio_items), len(clips))

        for expected, screen, raw, audio in zip(clips, screen_items, raw_items, audio_items):
            expected_values = {
                "start": str(expected["timeline_start"]),
                "end": str(
                    expected["timeline_start"]
                    + expected["out_frame"]
                    - expected["in_frame"]
                ),
                "duration": str(expected["out_frame"] - expected["in_frame"]),
                "in": str(expected["in_frame"]),
                "out": str(expected["out_frame"]),
            }
            for field, value in expected_values.items():
                self.assertEqual(screen.findtext(field), value)
                self.assertEqual(raw.findtext(field), value)
                self.assertEqual(audio.findtext(field), value)

        xml_text = xml_path.read_text()
        self.assertIn("Instantly Body screen only.mp4", xml_text)
        self.assertIn("Instantly Body raw.mp4", xml_text)
        self.assertEqual(len(root.findall(".//filter")), 0)


if __name__ == "__main__":
    unittest.main()
