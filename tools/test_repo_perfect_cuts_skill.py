from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = PROJECT_ROOT / ".agents" / "skills" / "perfect-cuts"


class RepoPerfectCutsSkillTests(unittest.TestCase):
    def test_skill_package_is_team_owned_and_discoverable(self):
        skill_text = (SKILL_ROOT / "SKILL.md").read_text()
        self.assertIn("name: perfect-cuts", skill_text)
        self.assertIn("Use when", skill_text)
        self.assertTrue((SKILL_ROOT / "agents" / "openai.yaml").is_file())

        for path in SKILL_ROOT.rglob("*"):
            if path.is_file() and path.suffix not in {".pyc"}:
                text = path.read_text(errors="ignore")
                self.assertNotIn("/Users/tymek", text, path)
                self.assertNotIn(".claude/skills", text, path)

    def test_team_workflows_cover_reuse_and_hyperframes(self):
        reuse = (SKILL_ROOT / "references" / "reusing-cut-plans.md").read_text()
        delivery = (SKILL_ROOT / "references" / "hyperframes-delivery.md").read_text()
        schema = (SKILL_ROOT / "references" / "cut-plan-schema.md").read_text()
        self.assertIn("aligned", reuse.lower())
        self.assertIn("source audio", reuse.lower())
        self.assertIn("data-media-start", delivery)
        self.assertIn("data-track-index", delivery)
        self.assertIn("timeline_start_frame", schema)
        self.assertIn("layers", schema)
        self.assertIn("export_hyperframes.py", delivery)
        self.assertNotIn("data-start` and `data-duration` in composition frames", delivery)

    def test_proven_audits_and_exports_are_vendored(self):
        expected = {
            "audit_restarts.py",
            "audit_premiere_sequence.py",
            "cut_plan.py",
            "edit_speech_map.py",
            "export_edl.py",
            "export_fcp7.py",
            "export_hyperframes.py",
            "export_srt.py",
            "render_mp4.py",
            "speech_map.py",
        }
        present = {path.name for path in (SKILL_ROOT / "scripts").glob("*.py")}
        self.assertTrue(expected.issubset(present))


if __name__ == "__main__":
    unittest.main()
