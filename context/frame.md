---
# BRAND TOKENS — normative. Measured frame-by-frame from Tymek's own two reference reels
# (`tymek.bielinski_DXPO0upgpDE.mp4`, `tymek ad v3.mp4`) on 2026-09-01. Quote verbatim; never round.
# Full grammar, motion timings and structural rules: `context/design-system.md` (read it first).
#
# NOTE: source files are compressed social exports, so hex values are accurate to ~±3 per channel.
# Where a true brand value is known, prefer it over the sampled one.
colors:
  # --- DARK GROUND (use when the screenshot being annotated is dark-mode) ---
  dark_bg: "#0C0C0C"            # near-black, never pure #000
  dark_surface: "#404040"       # opaque mid-grey panel (matches macOS/iOS dark card fill)
  dark_label: "#A8A9AB"         # secondary labels inside a panel
  dark_value: "#FBFBFB"         # primary values inside a panel
  dark_title: "#F9F9F9"         # scene title, carries a soft outer glow
  dark_ghost: "#192012"         # giant watermark numerals behind content
  # --- LIGHT GROUND (use when the screenshot being annotated is light-mode) ---
  light_bg_centre: "#ECECEC"    # soft radial, brighter in the middle
  light_bg_edge: "#E5E5E5"
  light_surface: "#F2F2F2"      # sheet / card, with a soft drop shadow
  light_ink: "#464646"          # headings
  # --- ANNOTATION (identical on both grounds — this is Tymek's pen) ---
  annotation_red: "#EE4B4A"     # arrows, underlines, highlight blocks, rings, outlines, pips
  emphasis_green_light: "#57A22F"   # the ONE accent word in a headline, light ground
  emphasis_green_dark: "#A6FF69"    # same role on dark ground (lime, glowing)
  state_blue: "#4285F4"         # "before" state ONLY — always ends up recoloured red
typography:
  title: "HelveticaNowDisplay Bold"   # graphic-scene titles. Neo-grotesque. SF Pro Display Bold = likely original
  captions: "Garet Heavy"             # burned-in captions. Rounded geometric. Poppins Bold = same look
  handwriting: "Caveat / NanumPenScript"  # marginalia only
  ui: "never restyled — it is a real screenshot"
motion:
  peer_stagger_ms: 125          # within a set of equals (calendar pips)
  chain_gap_ms: [300, 630]      # between causal beats (chip -> chip)
  state_swap_ms: 133            # recolouring a whole set: hard, global, NOT staggered
  typewriter_ms_per_char: 67
  word_reveal_ms_per_word: 200
  blur_crossfade_ms: 200
  camera_travel_pct_per_sec: [7, 16]   # across document-shaped screenshots
  hold_push_pct_per_sec: 3.4
spacing:
  frame_padding: 72             # px at 1080x1920
  radius: 14
  screenshot_rotation_deg: [1, 3]   # every composited screenshot is slightly off-axis
components:
  graphic_scene: "FULL-FRAME. The edit hard-cuts to it; the speaker disappears. 1.4-8.8s. ~45% of runtime."
  artifact: "a REAL screenshot, sourced before any animation is written. If you can't screenshot it, don't build the scene."
  annotation: "only the seven marks in design-system.md §5, all in annotation_red"
  caption: "burned into source footage — do NOT re-add"
---

# Frame Spec — Contentporary

## Read this first
`context/design-system.md` is the normative spec. This file is only its token sheet.

## The one rule that matters most
**Graphics are full-frame scenes the edit CUTS TO — not overlays floating on the talking head.**
Both reference reels spend ~45% of their runtime in full-frame graphic scenes built on real
screenshots. A short with graphics sprinkled over the speaker is a different, weaker product.

## Aspect ratios
- 9:16 (1080x1920) shorts — primary.
- 16:9 (1920x1080) long-form — same tokens, type scaled down ~1/1.3.

## Ground selection
Pick the ground from the screenshot you are annotating, not from taste: dark-mode UI -> dark_bg;
light-mode UI -> light_bg. Never mix within a scene.

## Background is lit, always
Dark ground: a blurred, oversized brand mark behind the panel + a coloured glow that tracks the
argument (teal while it is good, red once it is the problem). Light ground: a soft radial plus a
very faint blueprint grid. Never a flat fill.

## One accent word
Exactly one word per headline takes emphasis_green. Everything else is ink/white.
