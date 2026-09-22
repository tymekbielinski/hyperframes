# Custom instructions — applied to every video

## Output
- Long-form: 1920x1080 @ 30fps MP4, 16:9.
- Shorts: 1080x1920 @ 30fps MP4, 9:16 — same tokens, type scaled up ~1.4x, captions higher (70% height).
- Filename: `videos/<slug>/<slug>.mp4`. Always run `npx hyperframes check` before rendering.

## Captions
- Burned-in captions ON by default, max 2 lines, word-level timing.
- Style: bottom-center pill on 16:9; on 9:16 place at 70% height to clear platform UI.

## Music & SFX
- Subtle BGM at -22dB under narration; duck under speech. No SFX except a soft tick on scene transitions.

## Branding
- Logo bottom-right at 60% opacity during BODY beats only (asset TBD — drop into `context/assets/logo.svg`).
- CTA lines are written per-script (Hook/CTA are verbatim per the root CLAUDE.md content rules) —
  don't invent a generic CTA here.

## Do / Don't
- DO hold every scene to `context/motion-craft.md` — it is the motion standard for this folder.
  Run its authoring checklist before `npx hyperframes check`.
- DO reuse blocks already in the registry (`hyperframes add`) before writing custom ones.
- DO reuse `lib/motion-blur.js`, `lib/demo-transitions.js`, `lib/deep-glow.js` for camera moves,
  scene transitions, and glow/highlight accents — see `lib/README.md`.
- DON'T use fonts, colors, or radii not in `frame.md` once it's filled in.
- DON'T exceed one accent color per frame.
- DON'T ship fade-in / hold-still / fade-out motion on a flat background — that is the failure
  mode `motion-craft.md` exists to prevent.
- DON'T ship a video without previewing at least the hook and one body beat.
- DON'T optimize pacing for views/retention gimmicks over clarity — see `narrative.md`.
