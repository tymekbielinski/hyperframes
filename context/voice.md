# Voice — TTS configuration

voice_id: "TBD"          # pick with `npx hyperframes tts` (or /media-use), then lock it here
provider: "hyperframes tts"   # local Kokoro; needs kokoro-onnx (see setup note below)
language: "en"
speed: 1.0                # adjust per pillar if needed
style: "confident, plain, second-person — demonstration over tutorial (see narrative.md)"

## Rules
- Generate narration audio FIRST, then time composition beats to the audio (transcribe for exact timings).
- Numbers: pronounce naturally ("about fifteen hundred", not "one five zero zero").
- Product/tool names: spell in script phonetically if TTS mangles them; keep a pronunciation list here.
- One audio file per beat (easier re-renders) OR one file per video with word timestamps — default: per beat.
- Captions are generated from the final audio via transcription, not from the script text.

## Local TTS setup (Kokoro)
`hyperframes tts` needs `kokoro-onnx` + `soundfile`. System Python may have no wheels; use a 3.12 venv:
`python3.12 -m venv .venv-tts && .venv-tts/bin/pip install kokoro-onnx soundfile`, then run the CLI
with `HYPERFRAMES_PYTHON=<repo>/.venv-tts/bin/python`.
