import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "edit_speech_map.py"


class SpeechMapEditingTests(unittest.TestCase):
    def load_module(self):
        spec = importlib.util.spec_from_file_location("edit_speech_map", MODULE_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_builds_gapless_clips_from_cuts_trims_splits_and_picture_offset(self):
        module = self.load_module()
        speech_map = {
            "source": "/media/raw.mp4",
            "fps": 30,
            "width": 1920,
            "height": 1080,
            "samplerate": 48000,
            "blocks": [
                {"i": 0, "onset": 0.0, "end": 0.4, "gap_after": 0.6, "text": "false start"},
                {"i": 1, "onset": 1.0, "end": 1.3, "gap_after": 0.2, "text": "Hello"},
                {"i": 2, "onset": 1.5, "end": 1.8, "gap_after": 0.8, "text": "world"},
                {"i": 3, "onset": 3.0, "end": 3.8, "gap_after": 0.7, "text": "I I agree"},
                {"i": 4, "onset": 5.0, "end": 5.8, "gap_after": 0.0, "text": "trim me"},
            ],
        }
        sources = [
            {
                "label": "body",
                "map": speech_map,
                "cuts": {0: "superseded take"},
                "picture_offset_frames": 2,
                "picture_offset_reason": "verified camera latency",
                "split_overrides": {
                    3: [
                        {"in_frame": 90, "out_frame": 96, "text": "I"},
                        {"in_frame": 99, "out_frame": 114, "text": "agree"},
                    ]
                },
                "trim_overrides": {4: {"in_frame": 152, "out_frame": 170, "text": "trimmed"}},
            }
        ]

        clips, decisions, metadata = module.build_edits(sources, fps=30)

        self.assertEqual(len(clips), 4)
        self.assertEqual((clips[0]["first_block"], clips[0]["last_block"]), (1, 2))
        self.assertEqual((clips[0]["in_frame"], clips[0]["out_frame"]), (30, 55))
        self.assertEqual((clips[0]["video_in_frame"], clips[0]["video_out_frame"]), (32, 57))
        self.assertEqual((clips[1]["in_frame"], clips[1]["out_frame"]), (90, 96))
        self.assertEqual((clips[2]["in_frame"], clips[2]["out_frame"]), (99, 114))
        self.assertEqual((clips[3]["in_frame"], clips[3]["out_frame"]), (152, 170))
        self.assertEqual(clips[3]["text"], "trimmed")
        self.assertEqual(clips[1]["timeline_start"], 25)
        self.assertEqual(clips[3]["timeline_start"], 46)
        self.assertEqual(metadata["body"]["source"], "/media/raw.mp4")
        self.assertEqual(len(decisions), 5)
        self.assertEqual(decisions[0]["status"], "CUT")
        self.assertEqual(decisions[0]["reason"], "superseded take")


if __name__ == "__main__":
    unittest.main()
