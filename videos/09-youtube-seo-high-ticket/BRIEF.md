---
workflow: general-video
flow: automation
storyboard: yes
message: "YouTube search is where the buyers are — and the person who shows up there, once, gets the call."
destination: youtube
aspect: 1920x1080
fps: 30
language: en
audience: online operators at $20–50K/mo — agency owners, coaches, SaaS founders (profile.MD)
length: "18 graphic scenes of 4–9s, ≈2–2.5 min of graphics inside 6.5 min of talking head (≈40%)"
angle: full-frame graphic scenes cut into existing talking-head footage
deliverable: scene-clips
---

## Intent

Tymek's basic edit of video 09 ("How to do YouTube SEO to get high ticket clients") is
22:55 long and already carries slides (5:10–13:20) and screen demos. Three stretches are
pure talking head for longer than 30s. Each gets full-frame Contentporary graphic scenes
the edit cuts to — the house format from `context/design-system.md`: the speaker
disappears, a real screenshot is annotated in red, the scene hard-cuts back.

Source footage (NOT staged into the project — the deliverable is clips, not a re-render):
`/Users/tymek/Desktop/Contentporary/Content Team/Youtube Videos/09 How to do youtube seo to get high ticket clients/09 How to do youtube seo to get high ticket clients - basic edit.mp4`
(1920x1080, 30fps, 1374.8s).

Zones (talking-head boundaries measured from the footage's own hard cuts):

| Zone | In | Out | Length | Content |
|---|---|---|---|---|
| A | 91.03s (1:31.01) | 306.73s (5:06.73) | 215.7s | search-intent vs virality, "2nd largest search engine", Instagram/TikTok vs YouTube intent, search→click→trust→offer funnel, CTA #1 |
| B | 1167.07s (19:27.07) | ~1219s (20:19) | ~52s | LLM/AI search citations, chapters as hyper-specific queries, the third-party AI training setting |
| C | 1252.93s (20:52.93) | 1374.8s (22:54.8) | 121.9s | outro pitch: DIY 8–10 hrs/week in vidIQ vs working with Tymek, #1 rankings, $150K attributed, 10+ calls/month, one client per niche, capped at 5, book a call |

Scene ENDS land just after one of the footage's own jump cuts (`.hyperframes/scene-cuts-fine.txt`,
scores ≥0.04); starts are free. Scenes are 4–9s, hard cut in and out (standalone clips —
no footage in the composition, so no wipe from/to the speaker).

## Assets

- `assets/user/booking page.png` — real Cal.com booking page (2958x1762). CTA scenes (zone A 2:20, zone C 22:37).
- `assets/user/client-revenue-proof.mov` — 8.6s screen recording, 2958x1518 @120fps. The ONLY revenue proof; frames lifted from it for the "$150,000 attributed" scene (zone C 22:03).
- `assets/user/instagram-scroll.mov` — 60s phone recording of an Instagram feed scroll, 1052x1824 @120fps. Plays inside the "dumb scroll" contrast scene (zone A 3:00).
- Public captures Tymek approved me to take: YouTube search bar/homepage; live results for `clay tutorial` / `clay course` (Tim's + Xaver's videos ranking); a live search for `how to run ads for my B2B SaaS company`; a client video watch page; Tymek's Instagram profile; a ChatGPT/Claude/Gemini answer citing a YouTube video; a video's chapters as Key Moments in Google; a vidIQ frame lifted from the basic edit near 16:00.
- Design spec: `frame.md` (copied from `../../context/frame.md`); normative rules `../../context/design-system.md` (read first), `../../context/motion-craft.md`; libs copied from `../../lib/`.

## Customizations

- Board decisions (sketch pass, 2026-09-05): Frame 10 dropped; F17 single-phase (recording only); F16 is a designed chart (exception #3); F02 uses the six real client channel headers; F01 proves the claim with a real AI Overview/research capture; real brand marks on F11; arrowheads follow curve tangents.

- **Deliverable = scene clips for Premiere**, not a full re-render: each scene rendered as its own
  1920x1080 @30fps MP4, silent, hard cut in/out, named with its timeline TC
  (`scene-07_02-15-12.mp4`), plus `TIMECODES.csv` (scene, timeline in/out, in-frame, out-frame, duration).
- **Rate-blurred count-ups** on `$150,000` and `10+ calls per month` in zone C (motion-craft §6,
  digits lock right-to-left). Offered and not declined.
- **Two user-confirmed exceptions to the real-screenshot rule (design-system §2):**
  1. "Calendar with booked calls" (10+ calls/month; converting them to a call) → **recreate the
     Google Calendar UI** at product fidelity (motion-craft §12) instead of a screenshot. Tymek's call.
  2. "Lead magnet" beat (zone A 4:02) → **render a mockup** of a lead-magnet page. No real URL exists.
- **Open (pending on the board):** the "capped at 5 / one client per niche" roster view (zone A 2:15,
  zone C 22:23). No real material supplied yet; not built until Tymek supplies one or confirms a mock.

- Build-pass deviations (2026-09-05, all honest to the material): F04 phase 2 rings the @tymek.bielinski handle — the logged-out Instagram capture shows no "Message" button; F11 rings ChatGPT's real source chips (Google Help / Search Engine Journal) — no YouTube video card appeared in the logged-out answer; F13 rewrites the real chapter "How to normalize data in Clay" as the buyer's question; F16 is the designed chart of Tim's real 14,374-view curve (exception #3); calendars (F09/F15/F18) use Google Calendar's own palette at product fidelity.

- **Design system (2026-09-05, applied after the build):** Tymek's Claude Design project `e51a414c-fb3c-43e0-960a-3ecd9c236cdb` ("Contentporary — Design System", readme.md + tokens/*.css) now governs the look, overriding `DESIGN-SYSTEM.md` where they disagree: true-black `#000` canvas on EVERY scene (no light grounds), atmospheric warmth = top-centre light-rays `rgb(255,166,102)` + protection fades, orange is the ONLY chromatic colour — glows, the highlighter/underline marks (`#ff8c42`, replacing the red pen), the emphasis word (Instrument Serif italic, orange-300 `#fdba74` with text glow); Satoshi for all type; cards = `#171717` + `#262626` hairline + radius 16 + long shadow + the signature glow-bar; chips = translucent sunken pills with hairline, dual shadow and a glowing orange dot, monochrome logos; no blurred product logos as light; no bounces. Tymek's own line: "I hate the red gradient background".

## Notes

- No music, no captions, no logo on the clips — the footage carries audio and captions
  (custom.md: never re-add captions).
- Type scaled ~1/1.3 from the 9:16 tokens for 16:9 (frame.md).
- Ground per scene follows the screenshot's own mode: dark `#0C0C0C` or light `#ECECEC`, never
  mixed within a scene. Background always lit (blurred oversized brand mark + story-tracking glow
  on dark; radial + faint blueprint grid on light). Screenshots rotated 1–3° with soft shadow.
- Only the seven annotation marks in design-system §5, all `#EE4B4A`; exactly one `#57A22F`/`#A6FF69`
  accent word per headline.
- Motion: 125ms peer stagger, 300–630ms chained beats, 133ms hard set-swaps, ~67ms/char type-on,
  ~200ms/word reveals, 7–16%/s camera travel across document-shaped screenshots, still while a
  set builds. Every camera-move blur is `lib/motion-blur.js` (HFMotionBlur), never Gaussian.
- Standing feedback (memory `feedback_hyperframes_motion_style`): vignette every white ground,
  drop-shadow icons themselves, punch-ins ≤1.5x with sine.inOut and light blur, never a static
  opening — the first frames must already move.
- If Tymek re-trims the basic edit after delivery, re-slice the clips from the new cut list;
  don't nudge by eye.
