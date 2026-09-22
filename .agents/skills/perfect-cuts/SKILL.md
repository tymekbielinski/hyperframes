---
name: perfect-cuts
description: Use when raw talking-head, interview, podcast, tutorial, or screen-recorded footage needs silence removal, false-start and repeated-take cleanup, a Premiere-ready timeline, or the same edits applied to aligned alternate media for HyperFrames or Premiere.
---

# Perfect Cuts

Build a reviewable rough cut that keeps the best complete take of each idea while preserving source audio/video synchronization.

## Core contract

The deliverable is a timeline, not a rendered video. Unless the user explicitly asks for media rendering, produce a cut plan plus an editable Premiere XML, EDL, SRT, or HyperFrames composition.

Every edit must satisfy all four gates:

1. The kept speech is intelligible and semantically complete.
2. Earlier abandoned or weaker versions of the same idea are removed.
3. Picture and source audio come from the same source-time interval.
4. Automated audits pass before the timeline is handed off.

## Route the job

| Situation | Required path |
|---|---|
| New raw recording | Follow **New editorial cut** below. |
| Existing cut plan applied to another recording | Read [references/reusing-cut-plans.md](references/reusing-cut-plans.md). |
| HyperFrames delivery | Read [references/hyperframes-delivery.md](references/hyperframes-delivery.md). |
| Creating or editing machine-readable timeline data | Read [references/cut-plan-schema.md](references/cut-plan-schema.md). |
| Reported drift or lip-sync mismatch | Read both reference files before changing any timing. |

## New editorial cut

1. Probe every source with `ffprobe`; record duration, frame rate, time base, audio streams, and dimensions.
2. Generate a timestamped speech map with `scripts/speech_map.py` or an equivalent word-timestamp transcription.
3. Identify retake groups by meaning, not only matching words. Prefer the final complete, confident take unless an earlier take is clearly better.
4. Apply the reviewed cut/trim/split decisions with `scripts/edit_speech_map.py`, then build a version 1 cut plan with explicit layers for every video and audio track. Do not make cuts directly from transcript timestamps without checking the waveform or decoded audio.
5. Validate the plan, then export the editable timeline from it.
6. Run both audits:

```bash
python3 scripts/audit_restarts.py cut-plan.json
python3 scripts/cut_plan.py cut-plan.json
python3 scripts/audit_premiere_sequence.py cut-plan.json --cache raw=/path/to/transcript.mfdc
```

7. Spot-check every audit warning and every boundary near a retake. Do not dismiss a warning solely because it is short.

## Editorial defaults

- Use loose pacing unless the brief says otherwise.
- Remove dead air over roughly 0.5 seconds, but preserve intentional pauses and breath.
- Add 40–80 ms handles around speech boundaries when the source permits.
- Remove false starts, repeated openings, abandoned fragments, and duplicate explanations.
- Keep one best delivery of each idea.
- Never stretch, slip, or offset source audio independently to repair a cut. Fix the source mapping.
- Do not infer one global camera offset from a single clap, word, or take when latency may vary.

## Required outputs

- Editable timeline or HyperFrames composition.
- A version 1 machine-readable cut plan containing source in/out and timeline placement for every track layer.
- Short audit summary: duplicate/restart result, A/V mapping result, and any deliberate exceptions.

## Common failure modes

- **Repeated takes remain:** the selection was transcript-only or the audit result was not manually resolved.
- **Drift begins after a cut:** picture and source audio ranges differ, or frame/second conversions were mixed.
- **Some sections sync and others do not:** the recording has variable latency; solve per aligned source section, not with one global offset.
- **Alternate footage no longer matches:** cuts were recreated by transcript instead of replaying the existing cut plan.
