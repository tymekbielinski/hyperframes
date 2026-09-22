# Contentporary Content — HyperFrames Pipeline

Produce Contentporary's own YouTube long-form and Shorts animations at scale from one reusable
template: shared brand/voice context + a portable animation library + per-video scripts.

Ported from `/Users/tymek/Desktop/Hyperframes` (originally built for SaaS product-explainer demos
for clients). Only the brand-agnostic pieces came over — see `lib/README.md` for what each module
does. All client/LiveSession-specific brand tokens, fonts, and old video projects were left behind;
this pipeline is scoped to Contentporary's own content per the root `CLAUDE.md`.

## How it works

```
context/            ← the "template" — set up ONCE, reused by every video
  design-system.md  ← NORMATIVE house style: full-frame graphic scenes, real screenshots, the
                        seven annotation marks, measured motion timings. Read before frame.md.
  frame.md          ← brand truth: colors, fonts, spacing — MEASURED from Tymek's reference reels
  narrative.md       ← how Contentporary content is told: beat structure, tone, the 3 pillars
  voice.md           ← TTS voice config: voice id, speed, pronunciation rules
  custom.md           ← custom instructions (output specs, captions, CTA rules, do's/don'ts)
  motion-craft.md     ← NORMATIVE motion standard: measured timings, entrance/stagger/chaining
                        rules, blur usage, cut rates — reverse-engineered from real editors' work
  motion-waapi.md     ← WAAPI seek-safe animation technique reference (ported, generic)
  assets/             ← logos, fonts, thumbnails, client-result screenshots (create as needed)

lib/                 ← portable animation modules (ported from the original Hyperframes project)
  motion-blur.js      ← HFMotionBlur — analytic camera motion blur
  demo-transitions.js ← HFDemoTransitions — scene transitions + camera rig
  deep-glow.js        ← HFDeepGlow — multi-scale bloom/glow filter
  README.md           ← usage + API for all three

templates/
  script-template.md  ← blank script skeleton — copy per video, fill in (Hook/CTA verbatim, Body outline)

scripts/             ← INPUT: one filled script file per video
videos/              ← OUTPUT: one HyperFrames project per script (rendered MP4s land here)
```

## Producing a video (the loop)

1. Copy `templates/script-template.md` → `scripts/<slug>.md`, fill in hook/body/CTA per the root
   `CLAUDE.md` content rules (Hook and CTAs verbatim, Body as a bullet outline).
2. Tell your agent: *"Using /hyperframes, produce the video for `scripts/<slug>.md` following
   `hyperframes/PIPELINE.md`."*
3. The agent will:
   - Read `context/frame.md` (brand tokens are normative once filled in — exact hex/fonts, never
     invented), `context/motion-craft.md` (normative motion standard), `context/narrative.md`,
     `context/voice.md`, `context/custom.md`
   - Scaffold `videos/<slug>/`, copy `context/frame.md` into it, copy needed `lib/*.js` modules in
   - Generate TTS narration per `voice.md`, build the composition, add captions per `custom.md`
   - `npx hyperframes check` then `npx hyperframes render --output videos/<slug>/<slug>.mp4`
4. Batch: point the agent at the whole `scripts/` folder — it iterates.

## Setting up the template (one-time, still pending)

- **Brand tokens**: `context/frame.md` has placeholders only — fill in Contentporary's own video
  colors/fonts (or supply a Figma file for the agent to pull tokens from) before the first real render.
- **Voice**: pick a voice with `npx hyperframes tts` (or `/media-use`) and record the id in `voice.md`.
- **Logo/assets**: drop a logo into `context/assets/logo.svg` and reference it from `custom.md`.
- **Format variants**: for a different treatment (e.g. Business Figure Breakdown vs Tool Rebuild),
  clone `context/` → `context-<name>/` and reference it in the script's frontmatter (`context: context-<name>`).
