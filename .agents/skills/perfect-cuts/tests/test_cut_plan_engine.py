import importlib.util
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def load_module(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sample_plan() -> dict:
    return {
        "version": 1,
        "sequence": {
            "name": "Reusable body cut",
            "fps": 30,
            "width": 1920,
            "height": 1080,
            "sample_rate": 48000,
            "audio_channels": 1,
            "gapless": True,
        },
        "sources": {
            "screen": {
                "path": "/media/screen.mp4",
                "hyperframes_src": "public/media/screen.mp4",
                "source_frames": 900,
                "width": 1920,
                "height": 1080,
                "sample_rate": 48000,
                "audio_channels": 2,
            },
            "raw": {
                "path": "/media/raw.mp4",
                "hyperframes_src": "public/media/raw.mp4",
                "source_frames": 900,
                "width": 1920,
                "height": 1080,
                "sample_rate": 48000,
                "audio_channels": 1,
            },
        },
        "tracks": [
            {"id": "screen-v1", "kind": "video", "index": 1, "name": "Screen"},
            {"id": "camera-v2", "kind": "video", "index": 2, "name": "Camera"},
            {"id": "dialogue-a1", "kind": "audio", "index": 1, "name": "Dialogue"},
        ],
        "clips": [
            {
                "id": "cut-001",
                "timeline_start_frame": 0,
                "duration_frames": 60,
                "text": "First kept thought.",
                "layers": [
                    {"track": "screen-v1", "source": "screen", "in_frame": 90, "out_frame": 150},
                    {"track": "camera-v2", "source": "raw", "in_frame": 112, "out_frame": 172},
                    {"track": "dialogue-a1", "source": "raw", "in_frame": 90, "out_frame": 150},
                ],
            },
            {
                "id": "cut-002",
                "timeline_start_frame": 60,
                "duration_frames": 30,
                "text": "Second kept thought.",
                "layers": [
                    {"track": "screen-v1", "source": "screen", "in_frame": 300, "out_frame": 330},
                    {"track": "camera-v2", "source": "raw", "in_frame": 322, "out_frame": 352},
                    {"track": "dialogue-a1", "source": "raw", "in_frame": 300, "out_frame": 330},
                ],
            },
        ],
    }


class CutPlanValidationTests(unittest.TestCase):
    def test_accepts_explicit_multi_source_layers(self):
        cut_plan = load_module("cut_plan")
        validated = cut_plan.validate_plan(sample_plan())
        self.assertEqual(validated["duration_frames"], 90)
        self.assertEqual(validated["clip_count"], 2)

    def test_rejects_layer_duration_that_would_cause_drift(self):
        cut_plan = load_module("cut_plan")
        plan = sample_plan()
        plan["clips"][1]["layers"][1]["out_frame"] = 353
        with self.assertRaisesRegex(ValueError, "duration"):
            cut_plan.validate_plan(plan)

    def test_rejects_non_gapless_timeline_when_gapless_is_requested(self):
        cut_plan = load_module("cut_plan")
        plan = sample_plan()
        plan["clips"][1]["timeline_start_frame"] = 61
        with self.assertRaisesRegex(ValueError, "gapless"):
            cut_plan.validate_plan(plan)

    def test_rejects_source_frame_rate_mismatch(self):
        cut_plan = load_module("cut_plan")
        plan = sample_plan()
        plan["sources"]["screen"]["fps"] = 29.97
        with self.assertRaisesRegex(ValueError, "frame rate"):
            cut_plan.validate_plan(plan)


class TimelineExporterTests(unittest.TestCase):
    def test_edl_can_select_one_video_track_from_multi_layer_plan(self):
        exporter = load_module("export_edl")
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "timeline.edl"
            exporter.export_plan(sample_plan(), output, track_id="camera-v2")
            contents = output.read_text()

        self.assertIn("FROM CLIP NAME: raw.mp4", contents)
        self.assertIn("00:00:03:22 00:00:05:22", contents)
        self.assertIn("00:00:10:22 00:00:11:22", contents)

    def test_srt_uses_explicit_timeline_placement_from_v1_plan(self):
        exporter = load_module("export_srt")
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "captions.srt"
            exporter.export_plan(sample_plan(), output)
            contents = output.read_text()

        self.assertIn("00:00:00,000 --> 00:00:02,000", contents)
        self.assertIn("00:00:02,000 --> 00:00:03,000", contents)
        self.assertIn("Second kept thought.", contents)

    def test_fcp7_preserves_offsets_tracks_and_source_channel_count(self):
        exporter = load_module("export_fcp7")
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "timeline.xml"
            exporter.export_plan(sample_plan(), output)
            root = ET.parse(output).getroot()

        video_tracks = root.findall(".//media/video/track")
        audio_tracks = root.findall(".//media/audio/track")
        self.assertEqual(len(video_tracks), 2)
        self.assertEqual(len(audio_tracks), 1)
        self.assertEqual(video_tracks[0].find("clipitem/in").text, "90")
        self.assertEqual(video_tracks[1].find("clipitem/in").text, "112")
        self.assertEqual(audio_tracks[0].find("clipitem/in").text, "90")
        self.assertEqual(audio_tracks[0].find("clipitem/channelcount").text, "1")

    def test_hyperframes_uses_seconds_and_matching_audio_timing(self):
        exporter = load_module("export_hyperframes")
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            index = exporter.export_plan(sample_plan(), output)
            html = index.read_text()
            saved = json.loads((output / "cut-plan.json").read_text())

        self.assertIn('data-duration="3"', html)
        self.assertIn('data-start="2"', html)
        self.assertIn('data-media-start="10"', html)
        self.assertIn('data-media-start="10.733333"', html)
        self.assertIn('id="cut-002-dialogue-a1"', html)
        self.assertIn('data-track-index="11"', html)
        self.assertEqual(saved["version"], 1)


if __name__ == "__main__":
    unittest.main()
