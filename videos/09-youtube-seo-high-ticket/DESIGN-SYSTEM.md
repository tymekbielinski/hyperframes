# Contentporary — Graphic Design System

**Normative.** Reverse-engineered frame-by-frame from two of Tymek's own reels. Every number below
was measured at native frame rate from the source files, not estimated:

- **Reel A** — `tymek.bielinski_DXPO0upgpDE.mp4` · 720×1280 · 30fps · 43.77s · organic short
- **Reel B** — `tymek ad v3.mp4` · 1440×2560 · 30fps · 63.21s · paid ad

`motion-craft.md` is the *abstract* motion standard. **This file is the concrete house style** — the
actual grammar, palette, and structure of Contentporary's graphics. Where the two disagree, this
file wins, and § 9 lists the specific places `motion-craft.md` over-generalizes these reels.

---

## 1. The structural rule everything else hangs off

**Graphics are not overlays. They are full-frame scenes that the edit CUTS TO.**

The talking head disappears entirely. A graphic scene occupies the whole canvas, runs 1.4–8.8s,
and hard-cuts back to the speaker. Nothing dissolves; nothing floats over the footage.

Measured hard cuts:

| Reel | Cuts | Graphic scenes | Graphic screen time |
|---|---|---|---|
| A | 4.53 · 9.53 · 12.17 · 18.90 · 24.23 · 25.93 · 34.73 · 36.13 · 38.90 | 5 | **~20.0s of 43.8s — 46%** |
| B | 2.17 · 4.77 · 7.23 · 12.50 · 13.80 · 16.67 · 19.10 · 27.93 · 31.80 · 36.07 · 36.73 · 38.07 · 38.73 · 40.40 · 50.93 · 54.73 | 6 | **~28s of 63.2s — 44%** |

**Roughly 45% of the runtime is full-frame graphics.** That is the format. A short with graphics
sprinkled over the speaker is a different, weaker product — it is not what these reels do.

Corollary — **the graphic scene REPLACES the captions too.** Re-checked frame by frame: no
burned-in caption appears over any graphic scene in either reel (reel A's calendar t=4.6-9.5,
channel t=18.9-24.2 and funnel t=25.9-34.7 all run caption-free; same in reel B). The subtitle
layer belongs to the talking head only. So a composition never needs to dodge a caption corridor —
but be aware that heavy graphic coverage removes the subtitle layer for that share of the runtime.

### The scene transition — a bezier-eased motion-blurred wipe

Scenes change on a travelling soft-edged **mask**, not a cut and not an opacity fade. The card's
content is smeared along the travel axis by a directional `feGaussianBlur`, and the reveal is a
moving gradient mask whose feather decays in lockstep with the smear, so edge and content sharpen
together as the wipe lands. (Masking, not `clip-path` — clipping applies *after* the filter and
keeps a razor edge no matter how blurred the content is.)

| knob | value | why |
|---|---|---|
| easing | **`cubic-bezier(0.65, 0, 0.35, 1)`** | symmetric ease-in-out — the wipe leaves and arrives at **zero velocity** |
| duration in | **0.42s** | |
| duration out | **0.36s** | |
| blur | `14px` in / `12px` out, scaled by `4q(1-q)` | peaks mid-travel, nothing at either end |
| mask feather | `8 + 34 · 4q(1-q)` (%) | softest while moving fastest, tight at rest |

**The easing is the whole point.** `power2.out` on the way in and `power2.in` on the way out both
put peak velocity *exactly at the cut* — the transition starts and ends at full speed, which reads
as a snap however short you make it. A symmetric bezier moves the peak to the middle of the travel,
where the blur and the feather are also at maximum, so the fast part of the move is the part the eye
can't resolve anyway.

Blur and feather must ride the wipe's **speed**, not its position. Driving them off `(1 - q)` — max
at the start, zero at the end — smears hardest at the instant the scene appears, which is backwards.

Solve the bezier deterministically (bisection, ~24 iterations) rather than reaching for CustomEase;
the renderer seeks, so the curve has to be a pure function of time.

### Land scene boundaries ON the footage's own cuts

The underlying clip has its own jump cuts. A graphic scene that ends a few frames *before* one
leaves an orphaned tail of the outgoing shot — it flashes for 2-8 frames and then hard-cuts, which
reads as a glitch, not an edit.

Probe the source first:

```bash
ffmpeg -v info -i input-video.mp4 -filter_complex "select='gt(scene,0.20)',metadata=print:file=-" \
  -an -f null - 2>/dev/null | grep -oE "pts_time:[0-9.]+"
```

Then place every scene end so the **exit transition finishes just AFTER** the nearest source cut —
end = cut + the exit duration. The cut then happens while the graphic still covers the frame, and
the transition only ever reveals the incoming shot. Ending exactly ON the cut is second best (the
exit reveals slivers of the outgoing shot); ending before it is the failure case.

A scene *start* has no such constraint — it can begin mid-shot.

---

## 2. The artifact is always a REAL screenshot

Not one drawn box, invented chart, or generic icon appears in either reel. Every scene is built on
captured product UI:

| Reel | Scene | Real artifact used |
|---|---|---|
| A | calendar | a real dark-mode date picker, March 2026 |
| A | channel | a real YouTube channel page + real thumbnails with real durations (42:07, 47:07, 10:30) |
| A | funnel | three real competitor thumbnails |
| A | booking | a real Cal.com booking page |
| B | proof | a real Stripe payments dashboard (dates, Paid chips, descriptions) |
| B | channel | a real YouTube channel header with real sub count |
| B | receipt | a real payment-receipt card |
| B | capacity | a real "Free Trial Capacity" widget |

**Rule: if you cannot screenshot it, do not build the scene.** Source the real UI first; the
graphic is an annotation *of a real thing*, never an illustration of an idea. This is the whole
credibility mechanism.

Screenshots are composited **slightly rotated (~1–3°) with a soft drop shadow**, floating above the
ground — never flush, never dead-on flat.

---

## 3. Two grounds, chosen by the screenshot's own chrome

There is no single background. The ground **matches the mode of the UI being shown**.

### Dark ground (Reel A)
```
bg            #0C0C0C     near-black, not pure black
card surface  #404040     opaque mid-grey (the date picker's own fill)
label grey    #A8A9AB
value white   #FBFBFB
title white   #F9F9F9     with a soft white outer glow
```
Behind the card sits a **heavily blurred, oversized brand mark** — in the calendar scene, an
out-of-focus Google Calendar/Meet logo throwing green, yellow and blue light across the black. Plus
a **coloured glow floor** that changes with the argument: blue-teal arc top-left during the "booked"
phase, red glow from below during the "uneducated" phase. *The background is lit by the story.*

### Light ground (Reel B)
```
ground centre #ECECEC     soft radial — brighter in the middle
ground edge   #E5E5E5
card / sheet  #F2F2F2     with a soft drop shadow
ink           #464646     headings (true value likely ~#3A3A3A; video is compressed)
```
Carries a **very faint blueprint grid** — thin light rules, barely visible, giving the white a
surface instead of a void.

---

## 4. One annotation palette, shared by both grounds

```
ANNOTATION RED   #EE4B4A     highlight blocks, arrows, underlines, boxes, pips
                             (measured: #EA5253 reel A pips · #EE4B4A reel B block · #F0504F handwriting)
EMPHASIS GREEN   #57A22F     the one accent word in a dark headline (light ground)
                 #A6FF69     the same role on the dark ground — lime, with glow
STATE BLUE       ~#4285F4    "before" state only, always replaced by red
```

**Red is the annotation voice — it is what Tymek's pen looks like.** Green is what a *good* number
looks like. Blue only ever exists to be turned red.

---

## 5. The annotation vocabulary — seven marks, nothing else

Every graphic moment in both reels is one of these seven, drawn in ANNOTATION RED:

1. **Hand-drawn curved arrow with arrowhead** — an arc, not a straight line, pointing at a thing.
   ~2px at 720w. Used constantly.
2. **Hand-drawn underline** — slightly wobbly, under one data point *inside the screenshot*
   (e.g. under "2.82K subscribers" in the real channel header).
3. **Solid highlight block** — sharp-cornered red fill behind white text, sized to the number
   (`$50,000.00`). A marker slab, not a rounded chip.
4. **Hand-drawn ellipse / ring** around a number.
5. **Hand-drawn outline grouping several items** — in the funnel scene, a red trapezoid drawn
   around three stacked thumbnails with horizontal dividers, so the shape itself carries the meaning.
6. **Handwriting** — marginalia in a marker script (`$5,000/month → 4 videos`), red for the
   subject, dark for the comparison, with a drawn arrow between them.
7. **Tinted tool chips** — a rounded pill carrying a real product icon and an uppercase label,
   tinted to that product's own brand colour (blue STRATEGY, purple SCRIPTING, orange EDITING,
   green POSTING), connected to the artifact by a thin red arc.

Ghost numerals sit *behind* content as a watermark, never as a label — reel A's funnel has enormous
`1` `2` `3` in `#192012`, barely above the black.

---

## 6. Measured motion — the calendar scene, beat by beat

Reel A, 4.567 → 9.533 (4.97s). This is the canonical two-pass build; copy its shape.

| t | event | measured detail |
|---|---|---|
| 4.567 | **hard cut** to the dark scene | card already at full size — no entrance |
| 4.700–5.700 | 8 blue pips fill the month | **~125 ms apart**, card **completely static** |
| 5.800–6.800 | camera pushes **1.00 → 1.10** | starts *after* the pips, runs *under* the title |
| 6.067–6.600 | `Meetings` types on | **~2 frames per character ≈ 67 ms/char**, each char settling from below |
| 6.800–7.400 | whole composition **translates up ~280px** | the layout move that makes room for pass 2 |
| **7.200–7.333** | **all pips recolour blue → red** | **4 frames ≈ 133 ms — a hard global swap, NOT staggered** |
| 7.37–7.90 | `Uneducated Leads` lands below | |
| 8.2+ | red glowing lead icon fades up beneath | |
| 8.400–9.200 | slow push **1.075 → 1.105** | ≈ 3.4 %/s during the hold |
| 9.533 | **hard cut** back to the speaker | |

Two things to take from this that are easy to get wrong:

- **The recolour is instant.** 133 ms, whole set at once. Staggering it kills the "the same thing
  was always this" reveal.
- **Nothing moves during the pip build.** The camera waits, then moves between phases. Stillness is
  used deliberately as contrast against the moves.

---

## 7. Measured motion — the chip diagram, beat by beat

Reel B, 24.7 → 28.0. The canonical *chain*.

| t | event | measured detail |
|---|---|---|
| 24.70–24.90 | channel page **blur-crossfades to white** | **6 frames ≈ 200 ms**, both layers blurring |
| ~25.00 | the single thumbnail artifact is alone on white | |
| 25.167 | **STRATEGY** (top-left) | seeds as a small coloured dot, then **expands horizontally ~167 ms** to reveal its label |
| 25.533 | **SCRIPTING** (top-right) | **+367 ms** |
| 26.167 | **EDITING** (bottom-left) | **+633 ms** — a real beat of dead air |
| 26.467 | **POSTING** (bottom-right) | **+300 ms** |
| | each chip's red arc draws toward the artifact as it lands | |
| 26.93–27.6 | `We Handle Everything!` lands **word by word** | **~200 ms per word** |
| 27.3–28.0 | red underline **draws left→right, trailing the words** | finishes after the last word |
| 28.0 | **hard cut** | |

**The chip entrance grammar is its own thing:** a coloured dot appears, then the pill *grows
sideways* out of it to expose the label. That is not scale-down-from-oversize. Use it for anything
tag-like; keep scale-down entrances for headline type.

Chip-to-chip intervals are **300–630 ms**, not 110–170 ms. These are causal chain links with
visible dead air between them, not a stagger group. The 110–170 ms band applies *within* a set of
peers (the calendar pips at 125 ms); it does not apply to chained beats.

---

## 8. The camera is a character

Reel B travels across its screenshots continuously: measured **7–16 % scale per second**, with
deliberate reframes mid-scene (push in on the sub count, pull back to reveal the video grid, push
into a single thumbnail). The screenshot is treated as **a large world the camera explores**, not
as a card that appears.

This is the biggest single difference between these reels and a card-based overlay build. If a
scene shows a long document (a payments list, a channel page), the move *is* the animation — you
scroll and push through it, and the annotations land where the camera stops.

---

## 8b. Multi-phase camera — how to fix a crowded scene

A scene with more than ~3 elements presented at once reads as a slide. The fix is not to shrink
the content, it is to **make the stage taller than the frame and travel through it**, so the layout
is only ever ~60% visible and is read in passes.

The recipe, as built on short4's funnel:

1. **Lay the content out past the frame.** Stage 2800px against a 1920px frame; keep every element
   inside the frame's *width* so no camera position ever crops horizontally.
2. **Hold zoom constant** and move only in Y. A pure pan means the blur is single-axis and can be
   derived exactly; mixing zoom in adds a radial component a directional blur can't represent.
3. **Ease every leg on the house bezier** — `cubic-bezier(0.65, 0, 0.35, 1)`, solved by bisection
   through a keyframe track so the pose stays a pure function of time and survives seeking.
4. **Blur with the real library — `lib/motion-blur.js` (`HFMotionBlur`). Never a Gaussian.**
   See § 8c. A `feGaussianBlur` driven off camera velocity *looks* like motion blur in a still and
   is wrong in motion: it is an isotropic smudge, not a trail along the per-pixel velocity field.

   ```js
   var blur = HFMotionBlur.createCameraBlur({
     canvas: glCanvas, world: bakedTextureImg,
     camera: { T: pose },              // pure function of local time -> {tx,ty,s}
     fps: 30, preset: "medium", bg: [0.031, 0.035, 0.043, 1]
   });
   // during a leg: hide the DOM stage, show the canvas, and blur.render(t) each frame
   ```

5. **Put every leg in a quiet gap** — nothing may animate inside a move window, or the smear
   fights the content.
6. **Land the incoming element INSIDE the tail of its own leg.** This is the one that is easy to
   get wrong: if the camera arrives before the content does, you get a dead frame of empty
   background at the end of every move. Overlap them by ~0.2s.

## 8c. Motion blur is ALWAYS the library — never a Gaussian

**Rule: any blur that represents movement uses `lib/motion-blur.js` (`HFMotionBlur`). A
`feGaussianBlur` or CSS `blur()` is never an acceptable stand-in for motion blur.**

`HFMotionBlur` marches samples along the **analytic per-pixel velocity** of the camera transform,
so a pan trails along the pan axis and a zoom trails radially outward from the centre — different
directions in different parts of the same frame. A Gaussian cannot do that: it is one isotropic
radius everywhere, so it reads as an out-of-focus smudge rather than a moving one, and the failure
is obvious the moment there is any zoom component.

### Wiring it up

1. **`cp lib/motion-blur.js videos/<slug>/public/lib/`** and load it after GSAP.
2. **Bake a world texture per leg.** The blur samples a *static* image, so each camera leg needs a
   still of the settled layout as it appears during that leg. Generate a standalone bake page that
   mounts the card's scoped `<style>` plus its stage subtree at 1:1, with the elements visible for
   that leg forced to `opacity:1`, then screenshot it.
3. **The texture must carry the canvas aspect ratio.** The shader maps it onto world rect
   `[0,uRes.x] × [0,uRes.y]`, so a texture of any other aspect is silently stretched. Pick a
   blow-up factor `K`, size the texture `1080K × 1920K`, place the stage origin at
   `PAD_X = 540(K-1)`, and scale the pose by `K`:

   ```js
   function pose(t) {                       // stage point (540, cy) -> canvas centre at zoom Z
     var Z = zOf(t), cy = cyOf(t);
     return { tx: 540 - Z * (540 + PAD_X), ty: 960 - Z * (cy + PAD_Y), s: Z * K };
   }
   ```

   Padding exists so a pulled-back or off-centre camera still samples real pixels instead of
   running off the texture edge.
4. **Bake OPAQUE.** The pass averages RGBA across samples; a straight-alpha PNG averages its
   transparent texels and blows the whole frame out to white. Paint the scene's ground into the
   texture and pass the matching `bg` for out-of-bounds samples.
5. **Hand off cleanly.** During a leg, `opacity:0` the DOM stage and show the canvas; restore on
   exit. Nothing may animate inside a leg window or the texture stops matching the DOM.

### The one place the library does not apply

`createCameraBlur` handles *camera motion over static content* — it cannot capture live, changing
DOM per frame (the DOM→texture path is async and a seeked renderer cannot wait on it). So an
element-level smear (a panel sliding in while its own content animates) still uses a directional
`feGaussianBlur`, as card-04's row slams do. That is a documented limitation of the technique, not
a licence to approximate a camera move.

## 9. Where `motion-craft.md` over-generalizes these reels

Recorded so future work doesn't inherit the wrong abstraction. `motion-craft.md` was derived partly
from these files but flattens three things:

| `motion-craft.md` says | These reels actually do |
|---|---|
| "The bed never stops — a slow scale/drift runs under every hold" | The calendar card is **dead still for 1.2s** during the pip build. Stillness is used as contrast; the camera moves *between* phases and during holds, not always. |
| "Every entrance scales DOWN from 1.6–2.5× oversize" | True for headline type. **Chips seed-and-expand horizontally**; pips fade/scale up; screenshots simply cut in at full size with no entrance at all. |
| "Stagger is 110–170 ms. Always." | True for **peer sets** (pips: 125 ms). **Chained beats run 300–630 ms apart.** Two different rhythms; the doc collapses them into one. |

Also: neither reel uses a caption corridor — the graphics own the frame, so the captions simply run
on top of them.

---

## 9b. Two render-only text traps

Both of these look perfect in a live browser and only appear in encoded frames, so **check text
in the rendered MP4, never only in `hyperframes snapshot`.**

**1. `background-clip: text` + GSAP-animated word spans + `text-align: center` = ghost text.**
Gradient-filled text paints a background and clips it to the glyphs. When such text is split into
per-word spans that GSAP transforms, and the block is centred, the renderer rasterises that
background layer at its *stale, left-aligned* position — so a flat-white duplicate of the label
appears at the left edge of the frame, on top of the correct centred one.

Left-aligned gradient text is fine. Centred gradient text with no per-word animation is fine. The
combination is not. For a centred, word-animated label, **use a solid colour**:

```css
/* was: background-image: linear-gradient(...); background-clip: text;
        color: transparent; -webkit-text-fill-color: transparent; */
color: #F4F6F8;
```

**2. `line-height` shorter than the glyphs crops gradient text.** `background-clip: text` paints
only inside the element's background box, so a box shorter than the ascenders leaves the tops of
the letters with nothing to show through — they look sliced off. Keep `line-height >= 1.3` on any
gradient-filled text; never set it below the font size (e.g. `56px` type on a `62px` line box).

## 10. Typography

Identified visually from compressed source, so treat the specific names as **best match**, not
certainty — but all three roles are unambiguous and all candidates are installed on this machine.

| Role | Character | Best match (installed) |
|---|---|---|
| **Graphic-scene titles** (`Meetings`, `From New Clients`, `Previous agency`) | neo-grotesque, bold, tight | **HelveticaNowDisplay Bold** (SF Pro Display Bold is the likely original) |
| **Burned-in captions** (`next to nothing`, `and film`) | rounded geometric, heavy, circular bowls, single-storey `g` | **Garet Heavy** (Poppins Bold is the same family of look) |
| **Marginalia / handwriting** (`$5,000/month → 4 videos`) | marker script | a handwriting face — `Caveat` ships with the recut skill; `NanumPenScript` is installed |
| **In-screenshot UI text** | whatever the real product uses | never restyled — it is a screenshot |

Titles carry a **soft outer glow** on the dark ground so they lift off the black.

Headline emphasis: **one word only** takes the accent colour (`From` dark + `New Clients` green).

---

## 11. Build checklist for a Contentporary graphic scene

- [ ] It is a **full-frame scene the edit cuts to**, not an overlay
- [ ] The artifact is a **real screenshot**, sourced before any animation was written
- [ ] The ground matches the screenshot's mode — `#0C0C0C` dark or `#ECECEC` light
- [ ] The background is **lit**: a blurred oversized brand mark, a coloured glow that tracks the
      argument, or a faint grid — never a flat fill
- [ ] The screenshot sits **rotated 1–3° with a soft shadow**
- [ ] Pass 1 builds plainly; **pass 2 annotates in red** using only the seven marks in § 5
- [ ] Peer sets stagger at **~125 ms**; chained beats sit **300–630 ms** apart with visible dead air
- [ ] A state change across a whole set is a **hard 130 ms swap**, not a stagger
- [ ] Type-on runs at **~67 ms/char**; word-by-word runs at **~200 ms/word**
- [ ] The camera **travels** across anything document-shaped (7–16 %/s), and holds still while a
      discrete set builds
- [ ] Exactly one accent word per headline
- [ ] Scene ends on a **hard cut** back to the speaker
