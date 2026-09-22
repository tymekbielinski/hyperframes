import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
AUDITOR = SKILL_DIR / "scripts" / "audit_restarts.py"


class RestartAuditTests(unittest.TestCase):
    def run_audit(self, texts, allow=None):
        with tempfile.TemporaryDirectory() as tmp:
            cuts = Path(tmp) / "cuts.json"
            cuts.write_text(json.dumps({"clips": [{"text": text} for text in texts]}))
            command = [sys.executable, str(AUDITOR), str(cuts)]
            if allow is not None:
                decisions = Path(tmp) / "restart-decisions.json"
                decisions.write_text(json.dumps({"allow": allow}))
                command.extend(["--decisions", str(decisions)])
            return subprocess.run(
                command,
                capture_output=True,
                text=True,
            )

    def test_rejects_short_attempt_followed_by_completed_sentence(self):
        result = self.run_audit([
            "They use the same three kinds of videos.",
            "Use the same three kinds of videos every B2B company should be using.",
        ])

        self.assertEqual(result.returncode, 1)
        self.assertIn("same three kinds of videos", result.stdout.lower())

    def test_rejects_restart_spanning_several_short_clips(self):
        result = self.run_audit([
            "but you don't have internal resources to have",
            "your team",
            "work,",
            "to have your team scale your YouTube channel,",
        ])

        self.assertEqual(result.returncode, 1)
        self.assertIn("to have your team", result.stdout.lower())

    def test_accepts_documented_intentional_repetition(self):
        result = self.run_audit(
            [
                "Are you sharing your YouTube videos with sales?",
                "Are you sharing your YouTube videos with people going through demos?",
            ],
            allow={
                "boundary-0-1": "intentional parallel questions for different destinations"
            },
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("0 unresolved", result.stdout.lower())

    def test_rejects_restart_with_auxiliary_word_changed(self):
        result = self.run_audit([
            "It's because I see more and more agencies who are just,",
            "who just got lucky with one or two case studies.",
        ])

        self.assertEqual(result.returncode, 1)
        self.assertIn("who just", result.stdout.lower())

    def test_rejects_two_word_clause_restart(self):
        result = self.run_audit([
            "what you could pay to someone who's actually,",
            "to someone who's more invested in your individual project.",
        ])

        self.assertEqual(result.returncode, 1)
        self.assertIn("someone who's", result.stdout.lower())

    def test_rejects_single_word_stutter_across_boundary(self):
        result = self.run_audit([
            "That's exactly, that's",
            "exactly what I'm breaking down in this video.",
        ])

        self.assertEqual(result.returncode, 1)
        self.assertIn("exactly", result.stdout.lower())

    def test_rejects_repeated_phrase_inside_one_clip(self):
        result = self.run_audit([
            "And as you can see, as you can see the breakdown on screen."
        ])

        self.assertEqual(result.returncode, 1)
        self.assertIn("as you can see", result.stdout.lower())

    def test_rejects_interrupted_restart_inside_one_clip(self):
        result = self.run_audit([
            "This is where subscriptions come from. We only had one. We only had 100,000 views."
        ])

        self.assertEqual(result.returncode, 1)
        self.assertIn("we only had", result.stdout.lower())


if __name__ == "__main__":
    unittest.main()
