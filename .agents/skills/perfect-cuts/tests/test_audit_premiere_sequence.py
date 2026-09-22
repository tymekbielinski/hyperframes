import importlib.util
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
MODULE_PATH = SKILL_DIR / "scripts" / "audit_premiere_sequence.py"


class PremiereSequenceAuditTests(unittest.TestCase):
    def load_module(self):
        spec = importlib.util.spec_from_file_location(
            "audit_premiere_sequence", MODULE_PATH
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_uses_premiere_words_instead_of_the_declared_clip_text(self):
        module = self.load_module()
        cuts = {
            "fps": 30,
            "clips": [
                {
                    "source": "intro",
                    "in_frame": 0,
                    "out_frame": 30,
                    "text": "Instantly gets",
                },
                {
                    "source": "intro",
                    "in_frame": 30,
                    "out_frame": 90,
                    "text": "thousands of customers",
                },
            ],
        }
        premiere_words = {
            "intro": [
                {"text": "Instantly", "start": 0.10, "end": 0.30},
                {"text": "gets.", "start": 0.35, "end": 0.55},
                {"text": "Instantly", "start": 1.10, "end": 1.30},
                {"text": "gets", "start": 1.35, "end": 1.55},
                {"text": "thousands", "start": 1.60, "end": 1.95},
                {"text": "of", "start": 2.00, "end": 2.10},
                {"text": "customers", "start": 2.15, "end": 2.60},
            ]
        }

        observed = module.rebuild_observed_clips(cuts, premiere_words)

        self.assertEqual(observed[1]["text"], "Instantly gets thousands of customers")
        candidates = module.find_candidates(observed)
        self.assertEqual(candidates[0]["phrase"], "instantly gets")

    def test_assigns_each_word_to_only_one_adjacent_clip(self):
        module = self.load_module()
        cuts = {
            "fps": 30,
            "clips": [
                {"source": "intro", "in_frame": 0, "out_frame": 30, "text": ""},
                {"source": "intro", "in_frame": 30, "out_frame": 60, "text": ""},
            ],
        }
        premiere_words = {
            "intro": [
                {"text": "boundary", "start": 0.90, "end": 1.20},
            ]
        }

        observed = module.rebuild_observed_clips(cuts, premiere_words)

        self.assertEqual([clip["text"] for clip in observed], ["", "boundary"])

    def test_v1_plan_audits_the_designated_audio_layer(self):
        module = self.load_module()
        cuts = {
            "version": 1,
            "sequence": {"fps": 30},
            "tracks": [
                {"id": "camera-v1", "kind": "video", "index": 1},
                {"id": "dialogue-a1", "kind": "audio", "index": 1},
            ],
            "clips": [
                {
                    "id": "cut-001",
                    "text": "declared text",
                    "layers": [
                        {"track": "camera-v1", "source": "raw", "in_frame": 22, "out_frame": 52},
                        {"track": "dialogue-a1", "source": "raw", "in_frame": 0, "out_frame": 30},
                    ],
                }
            ],
        }
        premiere_words = {
            "raw": [
                {"text": "audio", "start": 0.1, "end": 0.3},
                {"text": "master", "start": 0.4, "end": 0.7},
                {"text": "picture-only", "start": 0.8, "end": 1.2},
            ]
        }

        observed = module.rebuild_observed_clips(cuts, premiere_words)

        self.assertEqual(observed[0]["text"], "audio master")


if __name__ == "__main__":
    unittest.main()
