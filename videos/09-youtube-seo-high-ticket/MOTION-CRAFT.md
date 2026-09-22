# Motion Craft — what separates professional editing from default animation

Normative for every HyperFrames composition in this folder. Reverse-engineered frame-by-frame from
five reference edits by working video editors (short-form ad, two 2x2 editor showreels, a 4K UGC
promo, and a vertical B2B short). Measurements below are real — pulled at native frame rate, not
estimated.

**Scope:** this file governs *motion, timing and composition only*. It deliberately prescribes no
colors, fonts, or radii — those come from `frame.md`. Where a rule says "accent," it means whatever
`frame.md` defines as the accent.

**Why this file exists:** the default failure mode is animation that is technically correct and
completely lifeless — elements fade in, sit still, fade out, on a flat background. Every rule below
is a specific correction to that failure mode.

---

## 1. The two-speed law (the single most important rule)

Professional motion runs **two clocks at once**:

| Layer | Duration | What it is |
|---|---|---|
| **Events** | 85–250 ms | An element arriving, a word landing, a line drawing, a digit locking |
| **Bed** | continuous, never stops | Slow scale/drift/light movement under everything |

Events are *brutally* fast — far faster than feels right when you author them. The bed never stops,
not even during a "hold." The contrast between the two is the entire effect. Get either one wrong
and it reads amateur: slow events feel like a PowerPoint transition; a still bed feels like a
screenshot with text on it.

**Bed rate:** 0.5–2% scale per second, or an equivalent slow translate. Measured on every single
reference — a calendar card grew ~3% over 0.8 s while pips appeared; a caption block was still
scaling 400 ms after its word had "landed"; a form scene drifted the whole time text typed into it.

Use `HFDemoTransitions.microDrift(tl, "#drift", T, total, {seed})` for the bed, or a plain
`tl.to(cam, {scale: 1.04, duration: SCENE_LEN, ease: "none"}, T)`. **Never author a scene with a
static bed.**

---

## 2. Entrances: scale DOWN from oversize, don't scale up from zero

Measured on title words and caption words: the element appears at **1.6–2.5× final size, low
opacity, blurred**, and *shrinks* into place while sharpening and gaining opacity. It reads as
arriving at the camera — impact.

```js
// PRIMARY entrance — impact. ~100-160ms. This is the default.
tl.fromTo(el,
  { scale: 2.0, opacity: 0, filter: "blur(14px)" },
  { scale: 1, opacity: 1, filter: "blur(0px)", duration: 0.14, ease: "power4.out" }, T);
```

Scale-**up**-from-small is reserved for *secondary/accent* objects (an emoji, a terminal label on a
diagram) where you want playful rather than authoritative — and there it gets an overshoot and a
much longer settle (~350–400 ms, `back.out(1.7)`).

**Corollary — nothing arrives axis-aligned.** Every object that flew in across the references
carried rotation and shed it on settle: a diagram icon −25°→−8°, a sticker −60°→−15°. Enter rotated,
de-rotate into place.

**Corollary — the settle outlasts the move.** The visible travel finished in ~250 ms but residual
motion continued for ~800 ms. Author it as two tweens, not one: a fast move, then a long
low-amplitude settle.

---

## 3. Stagger is 110–170 ms. Always.

The same interval showed up independently in three references: pill cards populating a composition
(165 ms), calendar pips filling a month (110–130 ms), caption words accumulating (~150 ms). At
24–30 fps that's **one element every 3–5 frames**.

- Faster than ~90 ms reads as simultaneous — you lose the sense of assembly.
- Slower than ~200 ms reads as sluggish and the viewer gets ahead of you.

**Order elements spatially, not in reading order.** The reference cascade went bottom-left →
upper-right → lower-right → bottom-right → upper-left. It bounces around the frame, which keeps the
eye scanning the whole composition instead of parking on a corner.

```js
ORDER.forEach((sel, i) =>            // ORDER is hand-sequenced for spatial bounce, NOT DOM order
  tl.fromTo(sel, {scale: 1.8, opacity: 0, filter: "blur(10px)"},
    {scale: 1, opacity: 1, filter: "blur(0px)", duration: 0.11, ease: "power4.out"},
    T + i * 0.15));
```

---

## 4. Chain causally — never fire everything at once

Every multi-part reveal in the references was a **chain with visible beats of nothing between the
links**:

> Diagram build: icon flies in (250 ms) → *beat* → dashed connector draws dash-by-dash (350 ms) →
> *beat* → terminal label pops at the line's endpoint (100 ms)

> Number reveal: digits roll and lock (350 ms) → **~270 ms hold where nothing happens** →
> hand-drawn ellipse strokes around it (330 ms) → sticker stamps in rotated (330 ms)

The 200–300 ms of dead air is not a mistake, it is the point. It tells the viewer the previous
event completed and gives the next one somewhere to land. Simultaneous reveals read as a template.

---

## 5. Two-pass build: construct the artifact, then annotate it

Three separate references used the identical structure:

1. **Pass 1 — build.** Assemble the thing plainly: three stacked screenshots, a month of calendar
   pips, a number counting up.
2. **Pass 2 — annotate.** *On top of the finished artifact*, in a visually different register, add
   the commentary: outline boxes + labels, a hand-drawn circle, a stamped sticker, a recolor of the
   existing pips.

The annotation pass must look like it came from a different tool than the artifact — hand-drawn
stroke, rough sticker, marker outline. That contrast is what makes it read as *someone explaining*
rather than *a slide that was designed this way*.

Pass 2 can also **reinterpret** pass 1 rather than adding to it: one reference filled a calendar
with blue "booked" pips, then recolored the same pips red and labelled them — the narrative twist
executed by mutating existing elements instead of rebuilding the scene. Cheap, and much stronger.

---

## 6. Blur is a channel, not an effect

This is the clearest amateur/professional tell in the whole teardown: **amateur animation moves
without blurring.** Reference material blurs constantly, in five distinct ways:

| Use | Where | How |
|---|---|---|
| Entrance blur | every element reveal | `filter: blur(10–14px)` → `0`, on the same tween as scale |
| Rate-proportional blur | count-ups, odometers | blur tracks the *derivative*: heavy mid-count, sharp at rest |
| Directional/motion blur | camera pans, fast object travel | `HFMotionBlur` — pick a preset by material |
| Blur crossfade | scene changes inside one idea | `HFDemoTransitions.blurCrossfade(tl, old, new, T, {blur: 12})` — measured at ~200 ms, both layers blur |
| Content motion blur | footage inside cards | source footage, chosen for its own motion |

For count-ups, drive the blur off the rate of change so it self-tunes:

```js
const n = {v: 0}; let prev = 0;
tl.to(n, { v: 1600000, duration: 1.6, ease: "power2.out", onUpdate() {
    el.textContent = fmt(n.v);
    const rate = Math.abs(n.v - prev); prev = n.v;
    el.style.filter = `blur(${Math.min(10, rate / 26000)}px)`;   // sharp when it settles
}}, T);
```

**Odometer detail:** on the neon-number reference each digit column rolled *vertically with its own
motion blur* and the digits **locked right-to-left, leading digit last** (…$320M → $220M → $120M).
Locking left-to-right or all-at-once looks wrong; people read the settle as the value resolving.

---

## 7. Backgrounds are lit. Flat is the tell.

Not one reference used a flat fill. Every background was one of:

- light radial gradient + soft vignette (the two product references)
- dark charcoal with a **directional light that slowly moves across the scene** (the keys scene)
- a soft radial glow blob behind the subject, fading in as the subject lands
- a full-frame gradient that *animates* — a blue field receding upward to white over ~800 ms as a
  transition device in its own right

Add depth the same way objects got it: soft drop shadows, slight perspective/rotation on cards,
never dead-on flat. A composition of flat rectangles on a flat fill is the single most recognizable
"generated animation" signature.

*(Which colors — from `frame.md`. This rule is about luminance structure, not palette.)*

---

## 8. Idle animation on hero objects

A 3D key-ring swung on a slow pendulum for its entire 3-second scene. Floating app icons drifted on
**independent slow paths at different rates** — parallax, so the composition has depth even when
nothing is "happening."

Any object on screen for more than ~1.5 s needs an idle: a slow rotation, a drift, a breathe. Seed
it (`microDrift`'s `{seed}`) so it stays deterministic under seeking. Give each object a *different*
seed and rate — synchronized idles look mechanical.

---

## 9. Text has three reveal modes and they mean different things

| Mode | Timing measured | Meaning |
|---|---|---|
| **Character typewriter** + caret | 67–125 ms/char | "someone is doing this right now" — search fields, forms, prompts |
| **Word-by-word fade** | ~150 ms/word, incoming word starts faded then darkens | "the narration is landing" — checklists, bullets |
| **Whole-word punch** (§2 entrance) | ~100–200 ms | emphasis — one word at a time carries the beat |

Don't mix modes inside one element. Do use different modes across a video — it's how the viewer
tells "system doing work" apart from "point being made."

**Type-on synchronizes with its connector.** On the keys reference, a label typed character by
character *while* a thin curved line drew from the label toward the object — the arc grew as the
text grew, both finishing together. Then the *second* label started. Sequential, never parallel.

**Progressive draw, not mask-wipe.** Dashed connectors appeared **dash by dash** along the path
rather than a solid line being wiped. Cheap to fake with a staggered per-dash reveal, and it reads
far more deliberate.

---

## 10. Captions are kinetic typography, not subtitles

Every short-form reference treated captions as the primary graphic layer:

- **word-level** timing, words accumulate on screen then the block clears
- **mixed size and weight within one caption block** — the emphasized word 3–5× the others
- **mixed style** — an italic/serif connector word against a heavy grotesque keyword
- **one accent color** on the emphasized word only, everything else neutral
- type is allowed to **bleed off the frame edges** — a word cropped by the left edge, a word running
  top-to-bottom of frame. Overscan is an energy device, use it on the payload word.
- each word gets its own §2 entrance; the block keeps drifting after the word lands

A bottom-centered pill with two lines of uniform text is a subtitle. It is correct for
accessibility and wrong as the design. If `custom.md` requires a caption pill for legibility, run it
*in addition to* the kinetic layer, not instead of it.

---

## 11. Cuts: hard for emphasis, dissolve for continuity

Measured hard-cut rates (scene threshold 0.30):

| Reference | Format | Hard cuts/min | Avg shot |
|---|---|---|---|
| Short-form ad | 1:1, 15 s | **40** | 1.5 s |
| UGC promo | 4K 16:9, 24 s | 15 | 3.9 s |
| Vertical B2B short | 9:16, 44 s | 12 | 4.9 s |
| Product promos (showreel) | 16:9 | ~0 | crossfade-driven throughout |

Targets: **short-form 25–40 cuts/min; long-form explainer 10–15 cuts/min.** But note the perceived
pace is much higher than these numbers, because element-level animation never stops between cuts.
Don't chase pace by cutting more — chase it with §1 and §3.

- **Hard cut** to switch register: talking head → graphic scene, or a full palette inversion. The
  strongest moment in the ad reference was a hard cut to a single word filling the frame on an
  inverted palette, already at ~85% scale and still growing, held over a second.
- **Blur crossfade** (~200 ms) to move within one continuous idea.
- Reserve `zoomThrough` / `colorDip` for once each per video — they're accents; using them
  repeatedly flattens them back into wallpaper.

---

## 12. Mock UI at product fidelity

The UI scenes carried real chrome — correct calendar day-headers, a real government search page's
layout, a real dropdown with a caret. The credibility comes from details nobody consciously
notices. The one that gives it away: in the form scene, **the favicon inside the field swapped in
the moment the typed text became a recognizable name.**

Budget one micro-detail like that per UI scene. It costs a single extra tween and does more for
perceived production value than any transition.

---

## Authoring checklist

Before `npx hyperframes check`, verify each scene:

- [ ] The bed never stops — a slow scale/drift runs under every hold
- [ ] Every entrance is 85–250 ms, and scales **down** from oversize unless it's a playful accent
- [ ] Every entrance carries entrance blur, and rotation it sheds on settle
- [ ] Multi-element reveals stagger at 110–170 ms, sequenced for spatial bounce
- [ ] Multi-part reveals are chained with 200–300 ms of dead air between links
- [ ] Anything explained gets built first, then annotated in a different visual register
- [ ] Background is a gradient with a vignette or a moving light — never a flat fill
- [ ] Every object on screen >1.5 s has a seeded idle at its own rate
- [ ] Count-ups blur proportionally to rate; odometer digits lock right-to-left
- [ ] Captions are word-level with mixed scale and one accent word — not a uniform subtitle
- [ ] Cut rate is in band for the format (§11)
- [ ] Each UI scene has one micro-detail that only a real product would have

## Seek-safety reminders

Everything above must survive the deterministic renderer (see `motion-waapi.md`):

- One paused master timeline; helpers only add tweens at explicit times.
- No `Math.random()` / `Date.now()` — seed idles and jitter deterministically.
- No `repeat: -1`; idles are finite tweens filling `[T, T + sceneLen]`.
- Transforms, opacity and `filter` only — never animate `width`/`height`/`top`/`left`. For the
  "container grows to fit new content" effect (measured on a checklist card), animate `scaleY` on a
  wrapper or pre-measure the two heights and tween a transform — do not tween layout.

## Appendix — reference teardown index

Frame-accurate strips used to derive the numbers above are regenerable with:
`ffmpeg -ss <t> -t <n/fps> -i <file> -vf "scale=<w>:-2,tile=6x4" -frames:v 1 out.png`

Note two of the five references are **2×2 quad showreels** — four independent editor pieces tiled
into one frame. Crop quadrants (`crop=960:540:<x>:<y>`) before analysing them.
