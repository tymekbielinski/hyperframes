# Reusing a cut plan across aligned sources

Use this workflow when two or more files contain the same performance or screen recording and must receive exactly the same editorial cuts.

## Preconditions

The files must share the same recording clock or have a measured mapping to it. Before applying cuts, compare:

- frame rate and whether it is constant or variable;
- duration and start time;
- audio sample rate and channel layout;
- a waveform or visual landmark near the beginning, middle, and end.

If alignment changes over time, the sources are not globally aligned. Create explicit alignment sections with their own mapping. Never use one offset merely because the first section lines up.

## Canonical rule

Treat the existing cut plan as the editorial source of truth. Do not transcribe the alternate file and do not re-decide takes.

For each kept segment, preserve:

- timeline start and duration;
- source start and duration;
- transition and handle decisions;
- segment identity and ordering.

Map that source interval to every aligned visual layer. In the version 1 cut plan, each visual or audio item is an explicit entry in the clip's `layers` array. Keep source audio from the designated audio master only. Duplicate source audio must be disabled or omitted.

## Multi-source timeline layout

- V1: primary screen-only or clean presentation source.
- V2: camera or alternate picture source, using the same segment boundaries.
- A1/A2: source audio from the chosen audio master.
- Other source audio: disabled unless intentionally mixed.

For every clip, source audio and its source picture must reference the same source-time interval. If V2 comes from a separately encoded but aligned file, apply the explicit alignment mapping before creating its in/out values.

## Verification

Check at least one cut near the beginning, middle, and end, plus every boundary where an alignment section changes. Confirm visible mouth movement, UI actions, or waveform peaks against source audio. Then run the Premiere-sequence audit.

If drift appears only after certain cuts, inspect those clip items first: compare their source in/out, duration, frame rate, and time base. Do not compensate by slipping all later audio.

Run `scripts/cut_plan.py` before exporting. It rejects any layer whose source duration differs from its timeline clip duration.
