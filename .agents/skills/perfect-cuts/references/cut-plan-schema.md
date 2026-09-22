# Cut-plan v1

The cut plan is the single source of truth for editorial decisions. Premiere XML and HyperFrames compositions are generated from this file; do not maintain separate hand-edited timing lists.

For transcript-driven cuts, `scripts/edit_speech_map.py` provides `build_edits(source_specs, fps, gap_threshold_seconds=0.6)`. It applies explicit cut reasons, frame-level trim overrides, within-block split overrides, and verified picture offsets while building a reversible decision log. Project adapters then translate those clips into the layer schema below. The Instantly builders in `tools/` are compatibility examples, not part of the generic engine.

## Shape

```json
{
  "version": 1,
  "sequence": {
    "name": "Client video rough cut",
    "fps": 30,
    "width": 1920,
    "height": 1080,
    "sample_rate": 48000,
    "audio_channels": 1,
    "gapless": true
  },
  "sources": {
    "raw": {
      "path": "/absolute/path/raw.mp4",
      "hyperframes_src": "public/media/raw.mp4",
      "fps": 30,
      "source_frames": 90000,
      "width": 1920,
      "height": 1080,
      "sample_rate": 48000,
      "audio_channels": 1
    }
  },
  "tracks": [
    {"id": "camera-v1", "kind": "video", "index": 1, "name": "Camera"},
    {"id": "dialogue-a1", "kind": "audio", "index": 1, "name": "Dialogue"}
  ],
  "clips": [
    {
      "id": "cut-001",
      "timeline_start_frame": 0,
      "duration_frames": 90,
      "text": "The selected delivery.",
      "layers": [
        {"track": "camera-v1", "source": "raw", "in_frame": 360, "out_frame": 450},
        {"track": "dialogue-a1", "source": "raw", "in_frame": 360, "out_frame": 450}
      ]
    }
  ]
}
```

## Invariants

- Frame values are integers in the sequence frame rate.
- Every declared source frame rate must match the sequence frame rate. Normalize variable-frame-rate media before using frame-based ranges.
- Each track ID and each `(kind, index)` lane is unique.
- A clip contains at most one layer per track.
- Every layer satisfies `out_frame - in_frame == duration_frames`.
- When `gapless` is true, each `timeline_start_frame` equals the previous clip's end.
- Different layers may have different source ranges only when the difference is intentional, such as a verified picture offset or aligned alternate source.
- `hyperframes_src` is a browser-loadable project path. `path` remains the local media identity used by Premiere XML.

## Commands

```bash
# Validate only
python3 scripts/cut_plan.py cut-plan.json

# Premiere / Resolve
python3 scripts/export_fcp7.py cut-plan.json timeline.xml

# Single-picture-track interchange and captions
python3 scripts/export_edl.py cut-plan.json timeline.edl --track camera-v1
python3 scripts/export_srt.py cut-plan.json captions.srt

# HyperFrames project; no render
python3 scripts/export_hyperframes.py cut-plan.json path/to/project
```
