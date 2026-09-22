---
format: 1920x1080
fps: 30
duration: "~148s of graphics across 18 scene clips (zone A 8 · zone B 3 · zone C 7), cut into 6.5 min of talking head"
message: "YouTube search is where the buyers are — and the person who shows up there, once, gets the call."
arc: Search vs virality → intent proof → CTA #1 → the buyer's journey (scroll → search → click → trust → offer → call) → AI search → DIY cost vs proof → CTA #2
audience: online operators at $20–50K/mo — agency owners, coaches, SaaS founders
mode: collaborative
source_footage: "../../../Youtube Videos/09 How to do youtube seo to get high ticket clients/09 How to do youtube seo to get high ticket clients - basic edit.mp4"
deliverable: one MP4 per frame (silent, hard cut in/out) + TIMECODES.csv
cut_rule: "tl_out lands ≥0.05s AFTER a footage jump cut, or ≥1.0s before the next one — never inside the 1s before a cut (design-system §1 orphan-tail rule). Starts are free."
---

## Frame 1 — #2 search engine in the world

- zone: A
- tl_in: 96.50
- tl_out: 104.85
- duration: 8.35s
- ends_on_cut: 104.80
- status: animated
- src: compositions/frames/01-search-engine.html
- transition_in: cut
- poster: 5.5
- ground: light
- artifact: REAL proof of the claim — a Google AI Overview / featured answer or the research page (globalmediainsight.com / TAMU) stating YouTube is the second-largest search engine (capture in progress)
- material: capture (public) — per board comment: "find research or an AI overview that proves the point"
- marks: ghost numeral "2" · red solid highlight slab behind "second-largest search engine in the world" · handwriting "#2 in the world" with a curved arrow
- motion: viewport-change (single-axis pan, HFMotionBlur) · css-marker-patterns circle · handwriting svg-path-draw
- scene: The camera is already drifting over the noisy home feed (the "virality" everyone chases), then pans UP to the search bar and stops; a giant ghost "2" sits behind the glass; a red ring draws around the bar as he says "second most commonly used search engine".
- voiceover: "…every other YouTube growth guru has been chasing virality, I focused on a completely different game happening in the search bar — the second most commonly used search engine in the world."

Cut in mid-pan (no entrance — the card is already full size, per §6). The feed is deliberately busy and slightly out of focus (depth-of-field-blur) so the sharp, still search bar is the only quiet thing on screen. Ghost "2" is `#192012` on `#0C0C0C`. Ring lands at "second"; handwriting types at ~67ms/char right after, finishing before "in the world".

## Frame 2 — 10+ clients, showing up

- zone: A
- tl_in: 106.00
- tl_out: 114.85
- duration: 8.85s
- ends_on_cut: 114.80
- status: animated
- src: compositions/frames/02-clients-ranking.html
- transition_in: cut
- poster: 6
- ground: light
- artifact: SIX REAL client channel headers — assets/user/client-channels/ (Tim Yakubson 3.32K · Xavier Caffrey GTM 1.25K · Johnny/Yiannis 7.42K · Jonas Massie 6.68K · Jack Rossi · William Yu)
- material: user (supplied via board comment)
- marks: red underline under each channel name as it lands (125ms peer stagger) · handwriting "10+ clients · every niche · all ranking"
- motion: viewport-change vertical travel (7–16%/s, HFMotionBlur) · css-marker-patterns underline + circle · peer-set stagger 125ms on the two rings
- scene: The camera travels down a real results page — the query underlined in red as it passes, then the two client thumbnails get ringed one after the other (125ms apart) and "10+ clients" is scrawled in the margin.
- voiceover: "…the exact method we use for 10 plus other clients to start showing up for the searches with the highest intent leads."

Document-shaped screenshot → the move IS the animation (§8). Camera holds still only for the two rings + the handwriting, then a slow 3.4%/s push during the hold-out.

## Frame 3 — Proof: Yiannis, 30 calls, $16K/m

- zone: A
- tl_in: 131.60
- tl_out: 140.20
- duration: 8.60s
- ends_on_cut: 140.13
- status: animated
- src: compositions/frames/03-proof-yiannis.html
- transition_in: cut
- poster: 5
- ground: dark
- artifact: assets/user/client-revenue-proof.mov PLAYS (8.6s carousel: Tim 20+ calls · $50,000 → Yiannis 30 calls · $16K/m → Jonas 60 calls · $80,000) — the recording itself, per board comment
- material: user (supplied)
- marks: red solid highlight block behind "30 qualified calls" · red ring on "$16K" · handwriting in pass 2: "1 client per niche · 5 max"
- motion: gentle push 1.00→1.10 sine.inOut · 133ms hard highlight swap · handwriting svg-path-draw
- scene: The proof card sits rotated 2° on black with the YouTube-red thumbnail throwing a red glow floor. Pass 1: "30 qualified calls" gets a red marker slab, "$16K" a ring. Pass 2, on "one person per niche": the marginalia "1 client per niche · 5 max" writes itself beside the card — the roster claim as Tymek's pen, no roster screenshot needed.
- voiceover: "…like our client Tim did, the fastest way is working with me one on one. We only accept one person per niche and limit our client base to five clients at a time."

Resolves the pending "roster" material without a mock: the cap is handwriting over real proof. If Tymek would rather have a real roster view, this frame still holds and Frame 18 takes the roster.
- build note (2026-09-06): red slab and ring removed at Tymek's request — the recording carries the proof, so the only graphic layer is the red marginalia, which now writes from local 2.5 (was 6.5, "appears too late") in the black strip left of the unmasked clip.

## Frame 4 — Book a call → or DM me

- zone: A
- tl_in: 140.60
- tl_out: 151.45
- duration: 10.85s (two phases — flagged, see note)
- ends_on_cut: 151.37
- status: animated
- src: compositions/frames/04-booking-and-dm.html
- transition_in: cut
- poster: 3
- ground: dark
- artifact: phase 1 — the real Cal.com booking page (assets/user/booking page.png; Tymek's booking-page RECORDING replaces it if supplied — not found in the folder). phase 2 — real Instagram profile @tymek.bielinski (capture)
- material: user + capture
- marks: red hand-drawn arrow → "Book time with me now" · red underline under "30 min · Google Meet" · phase 2: red ring on the @tymek.bielinski handle (the logged-out capture shows no Message button), handwriting "DM me"
- motion: push-in 1.0→1.28 on the form (sine.inOut, HFMotionBlur) · house bezier motion-blurred wipe between phases (0.42s in / 0.36s out, cubic-bezier(.65,0,.35,1)) · css-marker-patterns
- scene: Cut to the booking page already framed wide; the camera eases in on the form as a red arc draws to the title. On "or you can just DM me on Instagram" the page wipes off along a blurred soft edge and his real profile slides in; the Message button gets ringed, "DM me" is scrawled.
- voiceover: "So use the first link in the description to schedule a call with me… or you can just DM me on Instagram if you have any questions."

Length flag: no footage cut falls between 140.13 and 151.37, and the two CTAs are one breath, so this runs 10.85s as a two-phase scene rather than two clips with a 0.5s talking-head flash between them. Cut it to phase 1 only (140.6→146.3, ends 5s before the cut) if 10.85s feels long on the board.

## Frame 5 — Dumb scroll

- zone: A
- tl_in: 182.00
- tl_out: 190.00
- duration: 8.00s
- ends_on_cut: none (next cut 200.07 is 10s later — safe)
- status: animated
- src: compositions/frames/05-dumb-scroll.html
- transition_in: cut
- poster: 4
- ground: light
- artifact: assets/user/instagram-scroll.mov playing inside a phone frame (real footage — the Porsche reel etc.)
- material: user (supplied)
- marks: red hand-drawn X over the feed · handwriting "no problem · no search" · red arrow pointing down with the scroll
- motion: footage-in-card (content motion blur is the footage's own) · card rotated 2° with soft shadow · slow lateral drift bed · css-marker-patterns
- scene: A real phone, 2° off-axis on the soft grey ground with the faint blueprint grid, endlessly scrolling reels. Nothing is being searched for. A red X is struck through the feed at "dumb scroll", then "no problem · no search" written beside it.
- voiceover: "…people usually go on Instagram to dumb scroll a little bit, maybe watch some stories, but they're never actually looking for solutions."

The footage supplies the motion; the graphic layer stays sparse so the contrast with Frame 6 (a deliberate, typed search) is the whole point.

## Frame 6 — "how to run ads for my B2B SaaS company"

- zone: A
- tl_in: 192.30
- tl_out: 200.15
- duration: 7.85s
- ends_on_cut: 200.07
- status: animated
- src: compositions/frames/06-typed-search.html
- transition_in: cut
- poster: 5
- ground: dark
- artifact: real YouTube search results page for "how to run ads for my B2B SaaS company" (dark mode capture)
- material: capture (public)
- marks: red underline drawing under the query as it types · red ring on the first result
- motion: gsap-effects typewriter at 67ms/char + context-sensitive-cursor · underline trails the caret (design-system §7 word/underline coupling) · push 1.0→1.08 during the hold
- scene: An empty YouTube search bar, then the exact phrase types itself in — someone doing this right now — with a red underline chasing the caret; on Enter the results are already there (hard swap) and the top result gets ringed.
- voiceover: "So they're never typing into the search bar 'how to run ads for my B2B SaaS company'. This is what happens only on YouTube."

Type-on is the "system doing work" register (motion-craft §9); the results swap is a 133ms hard cut, not a fade.

## Frame 7 — The click: a clear promise

- zone: A
- tl_in: 214.50
- tl_out: 222.50
- duration: 8.00s
- ends_on_cut: none (next cut 228.77 — safe)
- status: animated
- src: compositions/frames/07-title-promise.html
- transition_in: cut
- poster: 4.5
- ground: dark
- artifact: real watch page of a client video (Tim — dark mode capture), title + thumbnail-grade first frame
- material: capture (public)
- marks: red ring around the title · red underline under the view count · handwriting "clear promise"
- motion: viewport-change (title → player, single-axis travel, HFMotionBlur) · css-marker-patterns · hold push 3.4%/s
- scene: The camera is tight on the title, rings it on "resonate with the title", then pulls down to the player as "clear promise" is written in the margin — the thing they were promised is right there.
- voiceover: "…what happens if they click your video and they resonate with the title — there's a clear promise, there's something they're getting out of this video."

## Frame 8 — Drive them to your offers (chip chain)

- zone: A
- tl_in: 241.50
- tl_out: 250.45
- duration: 8.95s
- ends_on_cut: 250.40
- status: animated
- src: compositions/frames/08-offer-chips.html
- transition_in: cut
- poster: 7
- ground: dark
- artifact: the client watch page (small, centre) + four tinted tool chips with REAL product icons — Cal.com, a rendered lead-magnet page thumbnail (USER EXCEPTION: mockup), Instagram, YouTube Subscribe
- material: capture + mock (lead-magnet page, per Tymek)
- marks: four tinted chips (BOOKING · LEAD MAGNET · INSTAGRAM · SUBSCRIBE) each connected to the artifact by a thin red arc · handwriting "high-intent leads →"
- motion: design-system §7 chip grammar — dot seeds, pill grows sideways (anchored-layout-expand), 300–630ms chained gaps landing on each spoken word · svg-path-draw arcs · spring-pop-entrance for the dots
- scene: The watch page sits alone in the middle. On "booking call funnel" a Cal.com dot seeds top-left and expands into its pill, a red arc draws to the artifact; "lead magnet" — top-right; "following you on Instagram" — bottom-left; "subscription on YouTube" — bottom-right. Real dead air between each. Held on the completed diagram.
- voiceover: "…you can start driving these high-intent search leads to your offers — whether that's a booking call funnel, a lead magnet, following you on Instagram, or a subscription on YouTube."

Canonical chain from reel B (§7). Chip intervals follow his words (≈ 242.5 / 244.5 / 247.0 / 249.0), not a fixed stagger.

## Frame 9 — Converting them to a call

- zone: A
- tl_in: 265.00
- tl_out: 273.50
- duration: 8.50s
- ends_on_cut: none (next cut 279.77 — safe)
- status: animated
- src: compositions/frames/09-calendar-week.html
- transition_in: cut
- poster: 5
- ground: light
- artifact: RECREATED Google Calendar week view at product fidelity (USER EXCEPTION #1 — Tymek asked for a recreation, not a screenshot)
- material: mock (Google Calendar UI)
- marks: booked "YouTube Growth Call" events fill the week as blue pips → hard 133ms recolour to red · handwriting "from search →" with a curved arrow into Monday
- motion: design-system §6 calendar build — peer stagger 125ms, card dead still during the build, then push 1.0→1.10, then the 133ms global swap · css-marker-patterns
- scene: A real-looking Google Calendar week, empty. Calls populate slot by slot — Tue 10:00, Wed 14:30, Thu 11:00… — eight of them at 125ms apart while the camera holds still. Then the camera pushes in and, on "converting them to a call", every event flips red at once and "from search →" is scrawled in.
- voiceover: "…educating them, nurturing them, and then converting them to a call or a free offer or a low ticket offer — whatever funnel we run, this works exceptionally well."

Product fidelity per motion-craft §12: correct Google Calendar chrome (day headers, hour rail, today pill, the mini-month). One micro-detail: the Google Meet icon inside each event.

## Frame 11 — Cited by ChatGPT, Claude, Gemini

- zone: B
- tl_in: 1170.30
- tl_out: 1178.05
- duration: 7.75s
- ends_on_cut: 1178.00
- status: animated
- src: compositions/frames/11-llm-citation.html
- transition_in: cut
- poster: 5
- ground: dark
- artifact: real ChatGPT answer (dark) to a YouTube-SEO question with a YouTube video citation card in the response (capture)
- material: capture (public)
- marks: three chips — CHATGPT · CLAUDE · GEMINI — carrying the REAL brand marks (assets/logos/openai.svg, claude.svg, gemini.svg, resolved via media-use) · red ring on the YouTube citation card
- motion: viewport-change travel down the answer (HFMotionBlur) · chips seed-and-expand on each spoken name (300–630ms) · css-marker-patterns circle
- scene: The camera scrolls a real ChatGPT answer until a YouTube citation card slides into frame and stops; the card gets ringed. As he names them, three chips pop along the top: ChatGPT, Claude, Gemini.
- voiceover: "…it's probably because you want to appear high in the searches from all the LLMs like ChatGPT, Claude, Gemini."

## Frame 12 — Authoritative source in AI results

- zone: B
- tl_in: 1190.00
- tl_out: 1198.55
- duration: 8.55s
- ends_on_cut: 1198.50
- status: animated
- src: compositions/frames/12-ai-overview.html
- transition_in: cut
- poster: 5
- ground: light
- artifact: real Google SERP with an AI Overview that cites a YouTube video (capture, light) — rebuilt in the sketch with the real AI Overview chrome (sparkle header, inline citation chips, source cards, Show more), per board comment
- material: capture (public)
- marks: red solid highlight block behind the cited YouTube line · red hand-drawn arrow from the AI Overview to the video card · handwriting "structured tutorial → cited"
- motion: viewport-change (single-axis pan, HFMotionBlur) · 133ms highlight slab · svg-path-draw arrow
- scene: Light ground, faint blueprint grid. The camera pans across a real Google AI Overview to where it cites a YouTube video; a red slab stamps behind the citation and an arrow connects it to the video card.
- voiceover: "…your YouTube videos are likely to be cited as authoritative sources in AI-driven generated results across both Google search engines and other LLMs."

## Frame 13 — Chapters as hyper-specific queries

- zone: B
- tl_in: 1206.00
- tl_out: 1214.00
- duration: 8.00s
- ends_on_cut: 1213.93
- status: animated
- src: compositions/frames/13-chapters-queries.html
- transition_in: cut
- poster: 5
- ground: dark
- artifact: real YouTube watch page (dark) with its chapter list open in the description (capture)
- material: capture (public)
- marks: red underline under each chapter title (125ms peer stagger) · handwriting rewrites one chapter as a question: "→ why are my google ads not converting?"
- motion: viewport-change travel down the chapter list · css-marker-patterns underline set · handwriting svg-path-draw (~67ms/char pacing)
- scene: The camera travels down a real chapter list; each chapter gets underlined as it passes. It stops on one, and Tymek's pen rewrites it in the margin as the exact question a buyer would type.
- voiceover: "…format your chapters as if they were hyper-specific queries that your high-intent leads might search for."

## Frame 14 — Months in vidIQ

- zone: C
- tl_in: 1264.50
- tl_out: 1273.00
- duration: 8.50s
- ends_on_cut: none (next cut 1282.03 — safe)
- status: animated
- src: compositions/frames/14-vidiq-grind.html
- transition_in: cut
- poster: 5
- ground: dark
- artifact: vidIQ keyword-research screen, lifted from the basic edit near 16:00 (his own footage, dark UI)
- material: lift from footage
- marks: red hand-drawn outline grouping the keyword table · handwriting "next few months…" · red arrow scrolling down
- motion: viewport-change vertical travel across the table (7–16%/s, HFMotionBlur) · css-marker-patterns sketchout · handwriting
- scene: The camera grinds slowly down a real vidIQ keyword table — row after row — while a rough red outline boxes the whole thing and "next few months…" is scrawled beside it. The pace is deliberately tedious.
- voiceover: "You could spend the next few months in vidIQ trying to look for the keywords, seeing what works, what doesn't — pulling keyword lists, writing and rewriting titles."

## Frame 15 — 8–10 hours every week

- zone: C
- tl_in: 1277.50
- tl_out: 1286.20
- duration: 8.70s
- ends_on_cut: 1286.17
- status: animated
- src: compositions/frames/15-calendar-hours.html
- transition_in: cut
- poster: 6
- ground: light
- artifact: RECREATED Google Calendar week view (USER EXCEPTION #1), same component as Frame 9
- material: mock (Google Calendar UI)
- marks: blocks labelled Keyword research · Titles · Scripting · Editing · Thumbnails · Posting fill the week (125ms) · count-up "8–10 h" with rate-proportional blur · 133ms swap to red on "you still have to run your business"
- motion: design-system §6 build → counting-dynamic-scale count-up (motion-craft §6 blur) → 133ms global recolour · push 1.0→1.10 between phases
- scene: The same calendar, now his: YouTube chores stack into the week block by block until it's full; a counter races to "8–10 h / week". Then, on "you still have to run your business", every block flips red at once — the week is gone.
- voiceover: "…that's around 8 to 10 hours every week on just optimizing titles, keywords… research, editing, scripting, thumbnails, posting. And on top of it, you still have to run your business."

## Frame 16 — YouTube takes 3–6 months

- zone: C
- tl_in: 1300.00
- tl_out: 1308.00
- duration: 8.00s
- ends_on_cut: none (next cut 1311.37 — safe)
- status: animated
- src: compositions/frames/16-three-six-months.html
- transition_in: cut
- poster: 5
- ground: light
- artifact: a DESIGNED chart of Tim's real view curve (numbers from his Studio analytics in the footage: 14,374 views) — USER EXCEPTION #3 per board comment "make this a more beautiful graph"; green accent line + area, month axis, red bracket under the flat 3–6 months
- material: lift from footage
- marks: red hand-drawn arrow along the curve · red ring on the 14.4K · handwriting "3–6 months"
- motion: viewport-change lateral travel along the curve (HFMotionBlur) · svg-path-draw arrow trailing the camera · css-marker-patterns circle
- scene: The camera rides along a real view-count curve from the flat months on the left to the climb on the right; a red arrow trails behind it; "3–6 months" is written under the flat part.
- voiceover: "…YouTube takes around three to six months to start bringing results, and most people don't even stay consistent for three to six months."

## Frame 17 — $150,000 attributed

- zone: C
- tl_in: 1322.80
- tl_out: 1329.50
- duration: 6.70s (single phase — rankings phase dropped per board comment)
- ends_on_cut: none (next cut 1340.07 — safe)
- status: animated
- src: compositions/frames/17-rank-revenue.html
- transition_in: cut
- poster: 11
- ground: dark
- artifact: assets/media/proof-1080.mp4 PLAYS unmasked on the solid dark bed ("just use the original video I filmed and place it on a dark background")
- material: capture + user
- marks: rate-blurred odometer count-up to "$150,000", digits locking right-to-left; red marker underline drawn under the locked number; red Caveat marginalia "attributed in new revenue" handwritten beside it
- motion: three-phase camera (`H.camera`, HFMotionBlur, never a Gaussian): punch-in at 1.30x on the recording (0.00-1.50) -> blurred dolly right onto the hero title region (1.50-2.30, leg, 0.8s, shutter 0.5) -> hold while $150,000 lands (enter 2.50), the odometer rolls 2.60-3.70 and locks right-to-left, and the underline draws 3.75-4.05 (2.30-4.20) -> blurred pull-wide to the exact, pixel-identical full composition (4.20-4.95, leg, 0.75s) -> settled hold with the marginalia writing itself from 4.98, 67ms/char (4.95-6.70); a small continuous sine drift rides under all three holds so nothing ever freezes; the leg-2 bake paints "$150,000" glyph-by-glyph straight from the DOM's own odometer character spans (getBoundingClientRect + computed font, not a separate fillText string) so there is no font swap at the DOM/canvas handoff; counting-dynamic-scale + motion-craft §6 rate blur, right-to-left lock; svg-path-draw underline; type-on marginalia
- scene: Open punched in on the recording card; the camera dollies right (blurred, directional) to frame the hero title as $150,000 tears up and locks digit by digit from the right, then gets underlined; the camera pulls wide (blurred) to reveal the full, uncrowded composition as the marginalia writes itself.
- voiceover: "We've ranked multiple client videos number one in high-intent search results. And across those clients, we've attributed $150,000 in new revenue."

Length flag: rankings and revenue are one sentence with 0.2s between them, so this is one two-phase clip (14.5s) rather than two clips separated by a 0.2s flash of talking head. Alternatives on the board: drop phase 1 (the rankings claim is already covered by Frames 2/10) → 1323.0→1329.5, 6.5s.
- build note (2026-09-06): both blurred legs bake the recording from pre-extracted frames `assets/media/proof-legs/l1-*.jpg` (video frames 81–105) and `l2-*.jpg` (162–185) — the live `<video>` cannot be sampled during capture. Stage is never hidden during legs (the opaque blur canvas covers it).

## Frame 18 — 10+ qualified calls a month

- zone: C
- tl_in: 1335.00
- tl_out: 1343.60
- duration: 8.60s
- ends_on_cut: 1343.53
- status: animated
- src: compositions/frames/18-calendar-month.html
- transition_in: cut
- poster: 6
- ground: light
- artifact: RECREATED Google Calendar MONTH view (USER EXCEPTION #1)
- material: mock (Google Calendar UI)
- marks: "YouTube Growth Call" pips populate the month at 125ms · odometer count-up "10+" with rate blur · red ring around the count
- motion: design-system §6 build (still camera) → counting-dynamic-scale → push 1.0→1.10 → css-marker-patterns circle
- scene: A month grid, empty. Calls land day after day — a blue pip each — while a counter in the corner keeps pace; it locks on "10+" and gets ringed as he says the number.
- voiceover: "…the fastest way to get you to 10 plus qualified calls per month from YouTube is by working with me one-on-one as your dedicated growth partner."

## Frame 19 — Book a call

- zone: C
- tl_in: 1358.00
- tl_out: 1366.50
- duration: 8.50s
- ends_on_cut: none (next cut 1368.50 — safe)
- status: animated
- src: compositions/frames/19-book-a-call.html
- transition_in: cut
- poster: 5
- ground: dark
- artifact: the real Cal.com booking page (assets/user/booking page.png; Tymek's booking-page RECORDING replaces it if supplied — not found in the folder)
- material: user (supplied)
- marks: red hand-drawn arrow → "Continue" · red ring around the calendar's next open day · handwriting "first link in the description"
- motion: push 1.0→1.30 into the form (sine.inOut, light blur, HFMotionBlur) · the "fill out the form" tooltip fades and the greyed dates un-grey (micro-detail) · css-marker-patterns
- scene: The booking page again — same treatment as Frame 4 for recognition (narrative.md: CTA gets the same visual both times). The camera eases into the form; the calendar's dates light up as the tooltip clears; a red arrow lands on Continue.
- voiceover: "…just use the first link in the description to book a call with me. I'll check where you're currently standing with your YouTube channel, your offer, and see what we can do for you."

## Pending

- **Roster / "capped at five, one per niche" (C, 1344.5→1352.5)** — no real material. Proposed resolution: carried as handwriting over Frame 3's proof card (already in the plan), so no separate frame. If Tymek supplies a real roster view (Notion / ClickUp / Cal.com capacity), it becomes Frame 20 here.
