/* ============================================================================
 * HFHouse — Contentporary house-style engine for the 09 scene clips
 * ----------------------------------------------------------------------------
 * Everything here is a pure function of timeline time (seek-safe, deterministic):
 * no clocks, no Math.random, no CSS transitions. Loaded ONCE from index.html
 * (after gsap + lib/motion-blur.js); every scene sub-composition calls into it.
 * Scenes must guard: `var H = window.HFHouse;` and degrade if absent (posters).
 *
 * Normative sources: DESIGN-SYSTEM.md (§1 wipe, §5 marks, §6/§7 timings, §8 camera),
 * MOTION-CRAFT.md (§6 rate blur, odometer), frame.md tokens.
 * ==========================================================================*/
(function (root) {
  "use strict";
  var RED = "#EE4B4A";

  /* ---------- 1. House easing: cubic-bezier(0.65, 0, 0.35, 1), solved by bisection ---------- */
  function bezierY(p) {
    // x(t) = 3(1-t)^2 t x1 + 3(1-t) t^2 x2 + t^3 ; x1=.65 x2=.35 ; y1=0 y2=1
    if (p <= 0) return 0; if (p >= 1) return 1;
    var lo = 0, hi = 1, t = p;
    for (var i = 0; i < 24; i++) {
      t = (lo + hi) / 2;
      var mt = 1 - t, x = 3 * mt * mt * t * 0.65 + 3 * mt * t * t * 0.35 + t * t * t;
      if (x < p) lo = t; else hi = t;
    }
    var m = 1 - t;
    return 3 * m * t * t * 1 + t * t * t; // y1 = 0 term vanishes
  }
  function lerp(a, b, f) { return a + (b - a) * f; }
  function clamp01(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }

  /* ---------- 2. The scene wipe (§1): travelling soft-edged mask + directional smear ----------
   * hostEl : element to reveal/hide (the whole scene phase or card)
   * feEl   : an <feGaussianBlur> inside an SVG filter applied to hostEl (filter: url(#id))
   * dir    : "left" | "right" | "up" | "down"  (direction the reveal edge travels)
   * Blur and feather ride the wipe's SPEED (4q(1-q)), not its position.               */
  var GRAD = { left: "to left", right: "to right", down: "to bottom", up: "to top" };
  function wipeApply(hostEl, feEl, q, blurMax, dir) {
    var horiz = dir === "left" || dir === "right";
    var speed = 4 * q * (1 - q);
    var v = blurMax * speed;
    if (feEl) feEl.setAttribute("stdDeviation", horiz ? v.toFixed(2) + " 0" : "0 " + v.toFixed(2));
    if (q >= 1) { hostEl.style.webkitMaskImage = hostEl.style.maskImage = "none"; return; }
    if (q <= 0) { hostEl.style.webkitMaskImage = hostEl.style.maskImage = "linear-gradient(" + GRAD[dir] + ", rgba(0,0,0,0) 0%, rgba(0,0,0,0) 100%)"; return; }
    var F = 8 + 34 * speed;                       // feather % — softest mid-travel, tight at rest
    var a = q * (100 + F) - F, b = a + F;
    var g = "linear-gradient(" + GRAD[dir] + ", rgba(0,0,0,1) " + a.toFixed(2) + "%, rgba(0,0,0,0) " + b.toFixed(2) + "%)";
    hostEl.style.webkitMaskImage = g; hostEl.style.maskImage = g;
  }
  function wipeIn(tl, hostEl, feEl, T, dir, dur) {
    dur = dur || 0.42; var d = { p: 0 };
    tl.set(hostEl, { autoAlpha: 1 }, T);
    tl.fromTo(d, { p: 0 }, { p: 1, duration: dur, ease: "none", immediateRender: false,
      onUpdate: function () { wipeApply(hostEl, feEl, bezierY(d.p), 14, dir); } }, T);
  }
  function wipeOut(tl, hostEl, feEl, T, dir, dur) {
    dur = dur || 0.36; var d = { p: 0 };
    tl.fromTo(d, { p: 0 }, { p: 1, duration: dur, ease: "none", immediateRender: false,
      onUpdate: function () { wipeApply(hostEl, feEl, 1 - bezierY(d.p), 12, dir); } }, T);
    tl.set(hostEl, { autoAlpha: 0 }, T + dur);
  }
  /* phase handoff inside one scene: A wipes out while B wipes in along the same axis */
  function phaseWipe(tl, outEl, outFe, inEl, inFe, T, dir) {
    wipeOut(tl, outEl, outFe, T, dir, 0.36);
    wipeIn(tl, inEl, inFe, T + 0.10, dir, 0.42);
  }

  /* ---------- 3. Hand-drawn marks (§5) — SVG paths that DRAW (svg-path-draw) ----------
   * All generators return a path `d` string in the scene's 1920x1080 coordinate space.
   * Wobble is deterministic (index-seeded), never Math.random.                          */
  function wob(i, amp) { return Math.sin(i * 12.9898) * amp; }
  function ringPath(cx, cy, rx, ry, seed) {
    seed = seed || 1; var pts = [], N = 22;
    for (var i = 0; i <= N; i++) {
      var a = -0.6 + (i / N) * Math.PI * 2.08;     // starts left-top, overshoots the join (marker style)
      var r1 = rx * (1 + wob(i + seed, 0.035)), r2 = ry * (1 + wob(i * 3 + seed, 0.045));
      pts.push([cx + r1 * Math.cos(a), cy + r2 * Math.sin(a)]);
    }
    // Smooth through the wobbled points (Catmull-Rom → cubic Béziers): a pen ring, not a 14-gon.
    // Straight L-segments read as a "blocky circle" once the camera scales the stage (Tymek, scenes 16/18).
    function P(i) { return pts[Math.max(0, Math.min(pts.length - 1, i))]; }
    var d = "M" + pts[0][0].toFixed(1) + " " + pts[0][1].toFixed(1);
    for (var j = 0; j < pts.length - 1; j++) {
      var p0 = P(j - 1), p1 = P(j), p2 = P(j + 1), p3 = P(j + 2);
      var c1x = p1[0] + (p2[0] - p0[0]) / 6, c1y = p1[1] + (p2[1] - p0[1]) / 6, c2x = p2[0] - (p3[0] - p1[0]) / 6, c2y = p2[1] - (p3[1] - p1[1]) / 6;
      d += " C" + c1x.toFixed(1) + " " + c1y.toFixed(1) + " " + c2x.toFixed(1) + " " + c2y.toFixed(1) + " " + p2[0].toFixed(1) + " " + p2[1].toFixed(1);
    }
    return d;
  }
  function underlinePath(x, y, w, seed) {
    seed = seed || 1; var d = "M" + x + " " + y, n = Math.max(3, Math.round(w / 90));
    for (var i = 1; i <= n; i++) d += " L" + (x + (w * i) / n).toFixed(1) + " " + (y + wob(i + seed, 3.5) + i * 0.6).toFixed(1);
    return d;
  }
  function arrowPath(x1, y1, x2, y2, curve) {
    // curve: signed bulge in px perpendicular to the chord (hand-drawn arc)
    curve = curve == null ? 120 : curve;
    var mx = (x1 + x2) / 2, my = (y1 + y2) / 2, dx = x2 - x1, dy = y2 - y1, L = Math.hypot(dx, dy) || 1;
    var nx = -dy / L, ny = dx / L, cx = mx + nx * curve, cy = my + ny * curve;
    var ang = Math.atan2(y2 - cy, x2 - cx), hl = 30;
    var h1x = x2 + hl * Math.cos(ang + 2.65), h1y = y2 + hl * Math.sin(ang + 2.65);
    var h2x = x2 + hl * Math.cos(ang - 2.65), h2y = y2 + hl * Math.sin(ang - 2.65);
    return { shaft: "M" + x1 + " " + y1 + " Q " + cx.toFixed(1) + " " + cy.toFixed(1) + " " + x2 + " " + y2,
             head: "M" + h1x.toFixed(1) + " " + h1y.toFixed(1) + " L" + x2 + " " + y2 + " L" + h2x.toFixed(1) + " " + h2y.toFixed(1) };
  }
  function outlinePath(x, y, w, h, seed) {
    seed = seed || 1; var k = function (i, a) { return wob(i + seed, a); };
    return "M" + (x + k(1, 6)) + " " + (y + k(2, 6)) + " L" + (x + w + k(3, 6)) + " " + (y + k(4, 5)) +
           " L" + (x + w + k(5, 6)) + " " + (y + h + k(6, 6)) + " L" + (x + k(7, 6)) + " " + (y + h + k(8, 5)) +
           " L" + (x + k(9, 4)) + " " + (y - 4 + k(10, 3));
  }
  /* Draw any stroked SVG path/paths over `dur` seconds starting at T (pen lifts at the end). */
  function draw(tl, pathEls, T, dur, ease) {
    var els = [].concat(pathEls); ease = ease || "power2.out";
    els.forEach(function (p) {
      var len = p.getTotalLength() * 1.03;
      p.style.strokeDasharray = len; p.style.strokeDashoffset = len; p.style.opacity = 1;
      tl.fromTo(p, { strokeDashoffset: len }, { strokeDashoffset: 0, duration: dur, ease: ease, immediateRender: false }, T);
    });
  }
  /* A red marker slab behind text: hard 133ms swap (a marker, not a fade). */
  function slab(tl, el, T) {
    tl.fromTo(el, { scaleX: 0, transformOrigin: "0% 50%", opacity: 1 }, { scaleX: 1, duration: 0.133, ease: "power3.out", immediateRender: false }, T);
  }
  /* Hard global state swap (§6): every element in `els` flips at once in 133ms. */
  function swap(tl, els, T, toVars) {
    var v = Object.assign({ duration: 0.133, ease: "none" }, toVars);
    tl.to(els, v, T);
  }

  /* ---------- 4. Handwriting (§5 mark 6): the text writes itself at ~67 ms/char ----------
   * Splits el's text into per-character spans at build time; reveal is stepped (tl.set),
   * so a seek lands on an exact character count. Returns the total write duration.     */
  function handwrite(tl, el, T, msPerChar) {
    msPerChar = msPerChar || 67;
    var text = el.textContent; el.textContent = "";
    var spans = [];
    for (var i = 0; i < text.length; i++) {
      var s = document.createElement("span"); s.textContent = text[i]; s.style.opacity = "0"; s.style.display = "inline"; s.setAttribute("data-layout-allow-overlap", ""); s.setAttribute("data-layout-allow-occlusion", "");
      el.appendChild(s); spans.push(s);
    }
    el.style.opacity = "1"; el.setAttribute("data-layout-allow-overlap", ""); el.setAttribute("data-layout-allow-occlusion", "");
    spans.forEach(function (s, i) { tl.set(s, { opacity: 1 }, T + (i * msPerChar) / 1000); });
    return (text.length * msPerChar) / 1000;
  }
  /* Typewriter: hard per-character steps (no fade) with a solid caret riding the last typed glyph; a longer beat after
   * each word; when the line is done the caret blinks `blinks` times (0.5 s period) and disappears. Everything is tl.set,
   * so a seek lands on an exact character count. Returns the total time until the caret is gone. */
  function typewrite(tl, el, T, msPerChar, opts) {
    msPerChar = msPerChar || 67; opts = opts || {};
    var wordPause = (opts.wordPauseMs == null ? 90 : opts.wordPauseMs) / 1000, blinks = opts.blinks == null ? 3 : opts.blinks, blinkS = 0.5;
    var text = el.textContent; el.textContent = "";
    var spans = [], carets = [];
    for (var i = 0; i < text.length; i++) {
      var sp = document.createElement("span"); sp.textContent = text[i];
      sp.style.display = "inline-block"; sp.style.position = "relative"; sp.style.whiteSpace = "pre"; sp.style.visibility = "hidden";
      sp.setAttribute("data-layout-allow-overlap", ""); sp.setAttribute("data-layout-allow-occlusion", "");
      var c = document.createElement("span"); c.setAttribute("aria-hidden", "true"); c.setAttribute("data-layout-ignore", "");
      c.style.cssText = "position:absolute;left:100%;top:6%;width:0.07em;height:0.86em;margin-left:0.04em;background:currentColor;visibility:hidden;";
      sp.appendChild(c); el.appendChild(sp); spans.push(sp); carets.push(c);
    }
    el.style.opacity = "1"; el.setAttribute("data-layout-allow-overlap", ""); el.setAttribute("data-layout-allow-occlusion", "");
    var t = T;
    spans.forEach(function (sp, i) {
      tl.set(sp, { visibility: "visible" }, t);
      tl.set(carets[i], { visibility: "visible" }, t);
      if (i > 0) tl.set(carets[i - 1], { visibility: "hidden" }, t);
      t += msPerChar / 1000 + (text[i] === " " ? wordPause : 0);
    });
    var last = carets[carets.length - 1];
    for (var b = 0; b < blinks; b++) {
      tl.set(last, { visibility: "hidden" }, t + b * blinkS + blinkS / 2);
      if (b < blinks - 1) tl.set(last, { visibility: "visible" }, t + (b + 1) * blinkS);
    }
    return t + (blinks - 0.5) * blinkS - T;
  }
  /* rasterText(el, {pad}) — EXACT bake parity for DOM text. Canvas fillText cannot reach OpenType tabular figures
   * (the Satoshi tabular "1" has a foot the proportional glyph lacks) nor the DOM's exact tracking, so instead the
   * element is rasterised ONCE through the browser's own layout engine: an SVG <foreignObject> carrying the element's
   * computed CSS (weight, size, tracking, line-height, colour, shadow, tabular-nums), child spans reproduced with their
   * own computed colour/weight, and Satoshi embedded as a data URI (an SVG image may not load external resources).
   * Returns a handle {img, x, y, pad}: img is null until decoded (fall back to a glyph painter meanwhile) — build it at
   * init, well before any leg. Draw with ctx.drawImage(h.img, h.x - h.pad, h.y - h.pad) in the stage's design space
   * (x/y = offsetLeft/offsetTop, i.e. the element's landed, untransformed position). Satoshi-only. */
  var _satoshiP = null;
  function satoshiB64() {
    if (!_satoshiP) _satoshiP = fetch("assets/fonts/Satoshi-Variable.ttf").then(function (r) { return r.arrayBuffer(); }).then(function (buf) {
      var bytes = new Uint8Array(buf), bin = ""; for (var i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
      return btoa(bin);
    });
    return _satoshiP;
  }
  function rasterText(el, opts) {
    opts = opts || {}; var pad = opts.pad || 48;
    var h = { img: null, x: opts.x != null ? opts.x : el.offsetLeft, y: opts.y != null ? opts.y : el.offsetTop, pad: pad };
    function esc(t) { return t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
    function spanStyle(n) { var c = getComputedStyle(n); return "display:" + (c.display === "inline" ? "inline" : "inline-block") + ";color:" + c.color + ";font-weight:" + c.fontWeight + ";font-style:" + c.fontStyle + ";font-variant-numeric:" + c.fontVariantNumeric + ";letter-spacing:" + c.letterSpacing + ";white-space:pre;opacity:1"; }
    function walk(node) {
      var out = "";
      for (var i = 0; i < node.childNodes.length; i++) {
        var n = node.childNodes[i];
        if (n.nodeType === 3) out += esc(n.textContent);
        else if (n.nodeType === 1 && n.tagName !== "CANVAS") out += '<span style="' + spanStyle(n) + '">' + walk(n) + "</span>";
      }
      return out;
    }
    function body() {   // resolved lazily (after fonts are ready): H.odometer may restructure the element after rasterText() was called
      var plain = el.getAttribute("data-hf-text");
      if (plain == null) return walk(el);
      return plain.split("").map(function (ch) { return '<span style="display:inline-block;vertical-align:top;font-variant-numeric:tabular-nums;line-height:1;white-space:pre">' + esc(ch) + "</span>"; }).join("");
    }
    Promise.all([satoshiB64(), document.fonts.ready]).then(function (res) {
      var b64 = res[0], cs = getComputedStyle(el), fs = parseFloat(cs.fontSize) || 16;
      var W = Math.ceil(Math.max(el.offsetWidth * 1.3, el.textContent.length * fs) + 2 * pad), Hh = Math.ceil(Math.max(el.offsetHeight, fs * 1.4) + 2 * pad);
      var css = "margin:0;padding:" + pad + "px 0 0 " + pad + "px;font-family:SatoshiBake;font-weight:" + cs.fontWeight + ";font-style:" + cs.fontStyle + ";font-size:" + cs.fontSize +
        ";letter-spacing:" + cs.letterSpacing + ";line-height:" + cs.lineHeight + ";font-variant-numeric:" + cs.fontVariantNumeric + ";white-space:nowrap;color:" + cs.color + ";text-shadow:" + cs.textShadow + ";text-align:" + cs.textAlign;
      var svg = '<svg xmlns="http://www.w3.org/2000/svg" width="' + W + '" height="' + Hh + '"><style>@font-face{font-family:"SatoshiBake";src:url(data:font/ttf;base64,' + b64 + ') format("truetype");font-weight:300 900;font-style:normal;}</style>' +
        '<foreignObject x="0" y="0" width="' + W + '" height="' + Hh + '"><div xmlns="http://www.w3.org/1999/xhtml" style="' + css + '">' + body() + "</div></foreignObject></svg>";
      var img = new Image(); img.onload = function () { h.img = img; }; img.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
    }).catch(function () {});
    return h;
  }
  /* Word-by-word landing (~200ms/word) for headline copy. */
  function words(tl, el, T, msPerWord) {
    msPerWord = msPerWord || 200;
    var parts = el.textContent.split(" "); el.textContent = "";
    parts.forEach(function (w, i) {
      var s = document.createElement("span"); s.textContent = w + (i < parts.length - 1 ? " " : ""); s.style.display = "inline-block"; s.style.whiteSpace = "pre"; s.setAttribute("data-layout-allow-overlap", ""); s.setAttribute("data-layout-allow-occlusion", "");
      el.appendChild(s);
      tl.fromTo(s, { opacity: 0, y: 14, scale: 1.6, filter: "blur(10px)" }, { opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.14, ease: "power4.out", immediateRender: false }, T + (i * msPerWord) / 1000);
    });
    return (parts.length * msPerWord) / 1000;
  }

  /* ---------- 5. Odometer count-up (MOTION-CRAFT §6): rate-proportional blur, digits lock right→left ----------
   * el shows `final` (a string like "$150,000" or "10+"). Every digit column rolls through
   * deterministic digits while unlocked and blurs with its roll rate; columns lock from the
   * rightmost to the leftmost across [T + dur*0.55, T + dur]. Non-digit glyphs are static.  */
  /* Odometer — a real COUNT-UP, blurred by the library.
   * The value climbs 0 -> final on a decelerating ease, so every frame shows a REAL number lower than the final
   * (Tymek: "the starting number should always be lower than the final number" — the old version rolled through
   * arbitrary digits, which meant nothing). Each digit is a window on a 0-9 strip parked at that digit's true
   * odometer position ((v / 10^place) mod 10), so units race while the leading digits barely move, exactly like a
   * mechanical counter. The smear is HFMotionBlur marching each column along its own analytic velocity
   * (renderRegions), capped so a racing digit reads as a streak instead of clamping. Leading zeros — and any
   * thousands separator ahead of the value — stay hidden until the number reaches them, so it formats correctly the
   * whole way up ($0 -> $12,847 -> $150,000). opts.hold keeps it static at the start value before the climb.
   * The window is taller than the digit row and fades at both edges, so nothing is ever sliced by a hard box edge. */
  function odometer(tl, el, T, dur, final, opts) {
    opts = opts || {};
    var hold = Math.max(0, Math.min(opts.hold == null ? 0 : opts.hold, dur * 0.85)), spinT = T + hold, spinDur = Math.max(0.001, dur - hold);
    // Shutter and smear cap: the trail is |velocity| * EXP cells, so a racing digit reads as a streak about one line
    // tall instead of dissolving into a grey band (a 3-cell cap smeared over three line heights — far too strong).
    var CELLS = 24, RES = 2, SHUTTER = 0.4, EXP = SHUTTER / 30, MAX_CELLS = 0.8, CAP = MAX_CELLS / EXP;
    el.setAttribute("data-hf-text", final);
    el.setAttribute("data-layout-allow-overlap", ""); el.setAttribute("data-layout-allow-occlusion", "");
    el.textContent = "";
    // --- parse the label into runs of digits (a "," or "." between digits stays inside the run)
    var chars = final.split(""), spansAll = [], cols = [], seps = [], runs = [], i;
    function isD(c) { return c >= "0" && c <= "9"; }
    var runOf = new Array(chars.length), cur = null;
    for (i = 0; i < chars.length; i++) {
      var c = chars[i];
      if (isD(c)) { if (!cur) { cur = { digits: [], seps: [], text: "" }; runs.push(cur); } cur.digits.push(i); cur.text += c; runOf[i] = cur; }
      else if (cur && (c === "," || c === ".") && i + 1 < chars.length && isD(chars[i + 1])) { cur.seps.push({ index: i, kind: c }); cur.text += c; runOf[i] = cur; }
      else cur = null;
    }
    // Where the climb STARTS: the largest single-significant-figure value below the final (150,000 -> 100,000;
    // 14.4 -> 10.0), or 70% of it when the final already is one significant figure (10 -> 7, 8 -> 5). Counting all the
    // way from zero raced through tens of thousands of values (Tymek: "we go through too many numbers"); from here only
    // a handful of readable numbers pass, and it is still always lower than the final.
    function startValue(f, decimals) {
      if (!(f > 0)) return 0;
      var mag = Math.pow(10, Math.floor(Math.log(f) / Math.LN10)), s = Math.floor(f / mag) * mag;
      if (s >= f - 1e-9) s = f * 0.7;
      var q = Math.pow(10, decimals);
      return Math.max(0, Math.floor(s * q) / q);
    }
    runs.forEach(function (r) {
      var dot = r.text.indexOf("."), clean = r.text.replace(/,/g, "");
      r.final = parseFloat(clean) || 0;
      r.decimals = dot === -1 ? 0 : (r.text.length - dot - 1);
      // Optional explicit start override (additive, backward compatible: omitted -> old auto behaviour
      // unchanged). Rounded to the run's own decimal precision so the wheel math (which keys off exact
      // digit places) stays consistent; falls back to the automatic start if the override isn't a real
      // number lower than the final (the count-up's one hard rule).
      if (opts.start != null && isFinite(opts.start)) {
        var q0 = Math.pow(10, r.decimals), s0 = Math.max(0, Math.round(opts.start * q0) / q0);
        r.start = (s0 < r.final) ? s0 : startValue(r.final, r.decimals);
      } else {
        r.start = startValue(r.final, r.decimals);
      }
      var intCount = r.digits.length - r.decimals, k = 0;
      r.places = {};
      r.digits.forEach(function (idx, n) { r.places[idx] = n < intCount ? (intCount - 1 - n) : -(n - intCount + 1); });
      r.seps.forEach(function (sp) {
        if (sp.kind !== ",") { sp.threshold = 0; return; }
        var right = 0; r.digits.forEach(function (idx) { if (idx > sp.index && r.places[idx] >= 0) right++; });
        sp.threshold = Math.pow(10, right);
      });
    });
    // --- DOM: one span per character (digits are what the reel replaces while it runs)
    chars.forEach(function (ch, idx) {
      var sp = document.createElement("span");
      sp.style.cssText = "display:inline-block;vertical-align:top;font-variant-numeric:tabular-nums;line-height:1;";
      sp.setAttribute("data-layout-allow-overlap", ""); sp.setAttribute("data-layout-allow-occlusion", "");
      sp.textContent = ch; el.appendChild(sp); spansAll.push(sp);
      var r = runOf[idx];
      if (r && isD(ch)) cols.push({ el: sp, run: r, place: r.places[idx], p10: Math.pow(10, r.places[idx]) });
      else if (r) seps.push({ el: sp, run: r, threshold: (function () { for (var k = 0; k < r.seps.length; k++) if (r.seps[k].index === idx) return r.seps[k].threshold; return 0; })() });
    });
    var digits = cols;
    runs.forEach(function (r) { r.minPlace = Math.min.apply(null, r.digits.map(function (idx) { return r.places[idx]; })); });
    // Wheel position for a value: the lowest place rolls continuously (it is the one actually counting); every place
    // above it rests on its own integer and only turns during the carry from the place below. Without this the units
    // wheel of "14.4" sat 40% of a cell past "4" on the last reel frame and snapped at the lock — a visible cut.
    // Same curve without the mod, so a central difference across a 9->0 wrap gives the real speed, not a spike.
    function wheelUnwrapped(c, v) {
      var d = v / c.p10;
      if (c.place === c.run.minPlace) return d;
      var whole = Math.floor(d), frac = d - whole;
      return whole + Math.max(0, Math.min(1, (frac - 0.9) * 10));
    }
    function wheelPos(c, v) {
      var d = v / c.p10;
      if (c.place === c.run.minPlace) return d % 10;
      var whole = Math.floor(d), frac = d - whole, carry = Math.max(0, Math.min(1, (frac - 0.9) * 10));
      return (whole % 10 + 10) % 10 + carry;
    }
    // --- the reel's own window: taller than the digit row, fading at both edges (never a hard cut)
    var win = document.createElement("div"); win.setAttribute("data-layout-ignore", ""); win.setAttribute("aria-hidden", "true");
    win.style.cssText = "position:absolute;left:0;pointer-events:none;overflow:hidden;visibility:hidden;";
    var cv = document.createElement("canvas"); cv.setAttribute("data-layout-ignore", ""); cv.setAttribute("aria-hidden", "true");
    cv.style.cssText = "position:absolute;left:0;pointer-events:none;";
    win.appendChild(cv); el.appendChild(win);
    var ease = gsap.parseEase("power1.out"), geo = null, world = null, blur = null, glFailed = false;
    function measure() {
      var cs = getComputedStyle(el), em = parseFloat(cs.fontSize);
      geo = { em: em, W: el.offsetWidth, H: CELLS * em, pad: em * 0.34,
              cols: cols.map(function (c) { var ls = parseFloat(getComputedStyle(c.el).letterSpacing) || 0; return { x: c.el.offsetLeft, w: c.el.offsetWidth, ls: ls }; }) };
      var winH = em + 2 * geo.pad, a = geo.pad / winH * 100, b = (geo.pad + em) / winH * 100;
      var fade = "linear-gradient(to bottom, rgba(0,0,0,0) 0%, rgba(0,0,0,0.10) " + (a * 0.62).toFixed(1) + "%, #000 " + a.toFixed(1) + "%, #000 " +
        b.toFixed(1) + "%, rgba(0,0,0,0.10) " + (b + (100 - b) * 0.38).toFixed(1) + "%, rgba(0,0,0,0) 100%)";
      win.style.width = geo.W + "px"; win.style.height = winH + "px"; win.style.top = (-geo.pad) + "px";
      win.style.webkitMaskImage = fade; win.style.maskImage = fade;
      cv.style.width = geo.W + "px"; cv.style.height = geo.H + "px"; cv.style.top = geo.pad + "px";
      // strip sheet:each column carries 0-9 cycles; the reel only ever shows a moving digit, so plain canvas text is
      // fine here (the LOCKED number is the DOM's own glyphs, which is what the bakes raster).
      var cs2 = getComputedStyle(el);
      world = document.createElement("canvas"); world.width = Math.ceil(geo.W * RES); world.height = Math.ceil(geo.H * RES);
      var x = world.getContext("2d"); x.scale(RES, RES);
      x.font = cs2.fontStyle + " " + cs2.fontWeight + " " + cs2.fontSize + " " + cs2.fontFamily;
      x.fillStyle = cs2.color; x.textAlign = "center"; x.textBaseline = "alphabetic";
      var m = x.measureText("0"), asc = m.fontBoundingBoxAscent || em * 0.8, desc = m.fontBoundingBoxDescent || em * 0.2;
      var baseline = asc + (em - (asc + desc)) / 2;
      geo.cols.forEach(function (g) {
        var cx = g.x + (g.w - g.ls) / 2;
        for (var k = 0; k < CELLS; k++) x.fillText(String(k % 10), cx, k * em + baseline);
      });
      buildExactWorld(cs2, em);
    }
    function buildExactWorld(cs, em) {
      Promise.all([satoshiB64(), document.fonts.ready]).then(function (res) {
        var b64 = res[0], colsHtml = geo.cols.map(function (g) {
          var cells = "";
          for (var k = 0; k < CELLS; k++) cells += '<div style="height:' + em + "px;line-height:" + em + 'px">' + (k % 10) + "</div>";
          return '<div style="position:absolute;left:' + g.x + "px;top:0;width:" + (g.w - g.ls) + 'px;text-align:center">' + cells + "</div>";
        }).join("");
        var svg = '<svg xmlns="http://www.w3.org/2000/svg" width="' + Math.ceil(geo.W * RES) + '" height="' + Math.ceil(geo.H * RES) + '" viewBox="0 0 ' + geo.W + " " + geo.H + '">' +
          '<style>@font-face{font-family:"SatoshiBake";src:url(data:font/ttf;base64,' + b64 + ') format("truetype");font-weight:300 900;font-style:normal;}</style>' +
          '<foreignObject x="0" y="0" width="' + geo.W + '" height="' + geo.H + '"><div xmlns="http://www.w3.org/1999/xhtml" style="position:relative;width:' + geo.W + "px;height:" + geo.H +
          "px;margin:0;font-family:SatoshiBake;font-weight:" + cs.fontWeight + ";font-style:" + cs.fontStyle + ";font-size:" + cs.fontSize +
          ";font-variant-numeric:tabular-nums;letter-spacing:0;color:" + cs.color + ';white-space:nowrap">' + colsHtml + "</div></foreignObject></svg>";
        var img = new Image();
        img.onload = function () { world = img; if (blur) { try { blur.updateWorld(img); } catch (e) {} } };
        img.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
      }).catch(function () {});
    }
    function ensure() {
      if (blur || glFailed || !root.HFMotionBlur || !geo) return;
      if (cv.__hfLost) { var fresh = cv.cloneNode(false); fresh.style.cssText = cv.style.cssText; win.replaceChild(fresh, cv); cv = fresh; cv.__hfLost = false; }
      var CW = Math.ceil(geo.W * RES), CH = Math.ceil(geo.H * RES);
      cv.width = CW; cv.height = CH;
      try { blur = root.HFMotionBlur.createCameraBlur({ canvas: cv, res: [CW, CH], world: world, preset: { shutter: SHUTTER, spacing: 1.25, maxN: 48 }, bg: null }); }
      catch (e) { glFailed = true; blur = null; if (root.console) console.warn("HFHouse odometer: blur unavailable, digits shown locked (" + (e && e.message) + ")"); }
    }
    function release() { if (blur) { try { blur.dispose(); } catch (e) {} blur = null; cv.__hfLost = true; } }
    // Which layer shows is decided per frame by whether the GPU pass actually painted — never by a timeline `set`.
    function show(reelPainting) {
      win.style.visibility = reelPainting ? "visible" : "hidden";
      digits.forEach(function (c) { c.el.style.visibility = reelPainting ? "hidden" : "inherit"; });
      if (!reelPainting) seps.forEach(function (sp) { sp.el.style.visibility = "inherit"; });
    }
    show(false);
    Promise.resolve(document.fonts ? document.fonts.ready : null).then(function () { measure(); }).catch(function () {});
    var prog = function (tt) { return ease(Math.max(0, Math.min(1, (tt - spinT) / spinDur))); }, h = 1 / 60;
    var drv = { t: T };
    tl.fromTo(drv, { t: T }, { t: T + dur, duration: dur, ease: "none", immediateRender: false, onUpdate: function () {
      var t = drv.t, painted = false, locked = t >= T + dur - 1e-6;
      if (!geo) measure();
      if (geo && !locked) {
        ensure();
        if (blur) {
          // Progress as a function of TIME, so the derivative is honest at the clamp boundaries: dead still through the
          // hold (a one-sided difference there invented a velocity and smeared the static number), and dead still at the lock.
          var e = prog(t);
          runs.forEach(function (r) { var span = r.final - r.start; r.v = r.start + span * e; });
          var regions = [];
          cols.forEach(function (c, i) {
            var g = geo.cols[i], rv = c.run.v;
            // A leading slot stays empty only while its wheel is still at rest on zero — once the carry from the digit
            // below starts turning it, it has to be on screen (otherwise 9 -> 10 flashed a bare "0" before the 1 landed).
            if (c.place > 0 && wheelUnwrapped(c, rv) < 1e-6) return;
            var d = wheelPos(c, rv); if (!(d >= 0)) d = 0;
            var vBack = c.run.start + (c.run.final - c.run.start) * prog(t - h), vFwd = c.run.start + (c.run.final - c.run.start) * prog(t + h);
            var vel = (wheelUnwrapped(c, vFwd) - wheelUnwrapped(c, vBack)) / (2 * h);
            vel = Math.max(-CAP, Math.min(CAP, vel));
            var pos = 10 + d, em = geo.em;
            regions.push({ x: g.x * RES, y: 0, w: g.w * RES, h: em * RES, T: function (tt) {
              return { tx: 0, ty: -(pos + vel * (tt - t)) * em * RES, s: 1 };
            } });
          });
          try { blur.renderRegions(t, regions); painted = true; } catch (e2) { painted = false; }
          if (painted) seps.forEach(function (sp) { sp.el.style.visibility = (sp.run.v >= sp.threshold) ? "inherit" : "hidden"; });
        }
      }
      if (locked) release();
      show(painted);
    } }, T);
    tl.set(el, { opacity: 1 }, T);
    return dur;
  }

  /* Word-by-word landing (~200ms/word) for headline copy. */
  function words(tl, el, T, msPerWord) {
    msPerWord = msPerWord || 200;
    var parts = el.textContent.split(" "); el.textContent = "";
    parts.forEach(function (w, i) {
      var s = document.createElement("span"); s.textContent = w + (i < parts.length - 1 ? " " : ""); s.style.display = "inline-block"; s.style.whiteSpace = "pre"; s.setAttribute("data-layout-allow-overlap", ""); s.setAttribute("data-layout-allow-occlusion", "");
      el.appendChild(s);
      tl.fromTo(s, { opacity: 0, y: 14, scale: 1.6, filter: "blur(10px)" }, { opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.14, ease: "power4.out", immediateRender: false }, T + (i * msPerWord) / 1000);
    });
    return (parts.length * msPerWord) / 1000;
  }

  /* ---------- 5. Odometer count-up (MOTION-CRAFT §6): rate-proportional blur, digits lock right→left ----------
   * el shows `final` (a string like "$150,000" or "10+"). Every digit column rolls through
   * deterministic digits while unlocked and blurs with its roll rate; columns lock from the
   * rightmost to the leftmost across [T + dur*0.55, T + dur]. Non-digit glyphs are static.  */



  /* ---------- 6. Chip grammar (§7): a dot seeds, the pill grows SIDEWAYS to expose its label ----------
   * el = the pill (final size authored in CSS, overflow hidden, border-radius = height/2).   */
  function chip(tl, el, T) {
    var h = el.offsetHeight || 78;
    tl.fromTo(el, { scale: 0, opacity: 0, transformOrigin: h / 2 + "px 50%", clipPath: "inset(0 calc(100% - " + h + "px) 0 0 round " + h / 2 + "px)" },
                  { scale: 1, opacity: 1, duration: 0.10, ease: "power3.out", immediateRender: false }, T);
    tl.to(el, { clipPath: "inset(0 0% 0 0 round " + h / 2 + "px)", duration: 0.167, ease: "power2.out" }, T + 0.10);
  }

  /* ---------- 7. Camera rig (§8, §8b, §8c): DOM during holds, HFMotionBlur during legs ----------
   * cfg = {
   *   stage:  the DOM camera wrapper (1920x1080 design coords, transform-origin 0 0)
   *   canvas: a <canvas> sibling covering the frame (hidden during holds)
   *   bake:   function(ctx, K) — draws the WORLD (ground + artifact + any marks that exist during legs)
   *           onto a 2D context of size (1920K x 1080K); design point (x,y) → canvas (PADX+x, PADY+y).
   *           MUST paint an OPAQUE ground (§8c point 4).
   *   bg:     [r,g,b,1] out-of-bounds colour (the ground)
   *   keys:   [{t, cx, cy, z}, ...] — at time t the design point (cx,cy) sits at screen centre at zoom z.
   *           Between keys the pose eases on the house bezier; equal poses = a hold.
   *   legs:   [[t0,t1], ...] windows where the canvas (blurred) shows instead of the DOM.
   *   dur:    scene duration.  K: texture blow-up (default 1.5).  preset: HFMotionBlur preset (default "medium")
   * }
   * Returns { pose(t), driver installed on tl }. Nothing else may animate inside a leg window. */
  function camera(tl, cfg) {
    var K = cfg.K || 1.5, W = 1920, Hh = 1080, PADX = (K - 1) / 2 * W, PADY = (K - 1) / 2 * Hh;
    var keys = cfg.keys.slice().sort(function (a, b) { return a.t - b.t; });
    function poseRaw(t) {
      if (t <= keys[0].t) return keys[0];
      for (var i = 0; i < keys.length - 1; i++) {
        var a = keys[i], b = keys[i + 1];
        if (t >= a.t && t <= b.t) {
          var f = b.t === a.t ? 1 : bezierY((t - a.t) / (b.t - a.t));
          return { cx: lerp(a.cx, b.cx, f), cy: lerp(a.cy, b.cy, f), z: lerp(a.z, b.z, f) };
        }
      }
      return keys[keys.length - 1];
    }
    // Optional deterministic jitter (e.g. a slow sine drift) added on top of the keyframed pose,
    // so a "hold" never truly freezes. cfg.drift(t) -> {dx,dy} in design px. Backward compatible:
    // scenes that don't pass cfg.drift get exactly the old poseRaw() behaviour.
    function poseDesign(t) {
      var p = poseRaw(t);
      if (!cfg.drift) return p;
      var j = cfg.drift(t) || {};
      return { cx: p.cx + (j.dx || 0), cy: p.cy + (j.dy || 0), z: p.z };
    }
    function domTransform(t) {            // design point (cx,cy) → screen centre at zoom z
      var p = poseDesign(t);
      return { dx: W / 2 - p.z * p.cx, dy: Hh / 2 - p.z * p.cy, z: p.z };
    }
    function glPose(t) {                  // see DESIGN-SYSTEM §8c: s = Z*K, tx = dx - Z*PADX
      var d = domTransform(t);
      return { tx: d.dx - d.z * PADX, ty: d.dy - d.z * PADY, s: d.z * K };
    }
    var stage = cfg.stage, canvas = cfg.canvas, blur = null, world = null, worldCtx = null;
    stage.style.transformOrigin = "0 0"; stage.style.willChange = "transform";
    // The stage is NEVER hidden during a leg (no opacity 0 / visibility hidden on it): HyperFrames skips
    // media seeks for invisible clips, so a <video> inside a hidden stage stays parked at the last visible
    // frame and a liveBake paints a stale card. The blur canvas is opaque (cfg.bg alpha 1), full-frame and
    // stacked above the stage, so it simply covers the DOM while a leg is showing.
    canvas.style.position = "absolute"; canvas.style.left = "0"; canvas.style.top = "0"; canvas.style.width = "1920px"; canvas.style.height = "1080px";
    canvas.style.zIndex = "40"; canvas.style.pointerEvents = "none"; canvas.style.opacity = "0"; canvas.style.visibility = "hidden";
    // Paint the world texture for time t. Called once (legacy behaviour) unless cfg.liveBake is
    // set, in which case it is re-run on every tick of a leg — lets cfg.bake(ctx,K,t) sample a
    // live <video> element (ctx.drawImage(videoEl,...) is synchronous, unlike rasterising an
    // arbitrary animating DOM subtree) and/or paint whatever marks have already landed by time t.
    function paintWorld(t) {
      if (!cfg.bgCss || cfg.bgCss === "transparent") worldCtx.clearRect(0, 0, world.width, world.height);   // transparent world: the DOM ground shows through the blur canvas
      else { worldCtx.fillStyle = cfg.bgCss; worldCtx.fillRect(0, 0, world.width, world.height); }
      worldCtx.save(); worldCtx.translate(PADX, PADY); cfg.bake(worldCtx, K, t); worldCtx.restore();
    }
    var glFailed = false;
    function ensure() {
      if (blur || glFailed || !root.HFMotionBlur) return;
      if (!world) { world = document.createElement("canvas"); world.width = Math.round(W * K); world.height = Math.round(Hh * K); worldCtx = world.getContext("2d"); paintWorld(0); }
      // A lost context leaves the old <canvas> unusable: swap in a fresh element (same id/class/style) before re-creating.
      if (canvas.__hfLost) { var fresh = canvas.cloneNode(false); fresh.__hfLost = false; canvas.parentNode.replaceChild(fresh, canvas); canvas = fresh; }
      canvas.width = W; canvas.height = Hh;
      try {
        blur = root.HFMotionBlur.createCameraBlur({ canvas: canvas, world: world, camera: { T: glPose }, fps: cfg.fps || 30, preset: cfg.preset || "medium", bg: ("bg" in cfg) ? cfg.bg : [0.047, 0.047, 0.047, 1] });   // bg: null = transparent (HFMotionBlur blends)
      } catch (e) { glFailed = true; blur = null; if (root.console) console.warn("HFHouse camera: blur unavailable, showing the DOM pose (" + (e && e.message) + ")"); }
    }
    // The context lives only while a leg is showing (Chrome keeps ~16 live WebGL contexts per page; the reel has many
    // camera scenes plus the odometer reels — an evicted context surfaces as "Uncaught Error: null" in the preview).
    function release() { if (blur) { try { blur.dispose(); } catch (e) {} blur = null; canvas.__hfLost = true; } }
    function inLeg(t) { for (var i = 0; i < cfg.legs.length; i++) if (t >= cfg.legs[i][0] && t < cfg.legs[i][1]) return true; return false; }
    var drv = { t: 0 }, lastT = 0;
    function tick(t) {
      var d = domTransform(t);
      stage.style.transform = "translate(" + d.dx.toFixed(2) + "px," + d.dy.toFixed(2) + "px) scale(" + d.z.toFixed(4) + ")";
      if (inLeg(t) && root.HFMotionBlur) {
        ensure(); if (blur) { if (cfg.liveBake) { paintWorld(t); blur.updateWorld(world); } blur.render(t); canvas.style.opacity = "1"; canvas.style.visibility = "visible"; return; }
      }
      canvas.style.opacity = "0"; canvas.style.visibility = "hidden";
      release();
    }
    tl.fromTo(drv, { t: 0 }, { t: cfg.dur, duration: cfg.dur, ease: "none", immediateRender: false, onUpdate: function () { lastT = drv.t; tick(drv.t); } }, 0);
    // liveBake + a <video>: the tick paints the video SYNCHRONOUSLY, but a seek on the element is async — at
    // the tick the frame is still the previously decoded one (stale card during a leg). cfg.liveMedia lists
    // the media elements the bake samples; when one finishes seeking (or decodes new data) while a leg is
    // showing, the leg is re-painted for the same t, so whatever is captured after readiness is the true frame.
    // Deterministic: the repaint is a pure function of (t, decoded frame at t).
    (cfg.liveMedia || []).forEach(function (m) {
      var lastVt = -1;
      function repaint() { if (inLeg(lastT) && m.currentTime !== lastVt) { lastVt = m.currentTime; tick(lastT); } }
      ["seeked", "loadeddata", "canplay", "timeupdate", "playing", "pause"].forEach(function (ev) { m.addEventListener(ev, repaint); });
      // requestVideoFrameCallback fires when a NEW decoded frame is presented — the one signal that covers every
      // way the runtime can advance the element (seek, play/pause nudge, fastSeek). Re-armed on each callback.
      if (m.requestVideoFrameCallback) { (function arm() { m.requestVideoFrameCallback(function () { repaint(); arm(); }); })(); }
    });
    // seed frame 0
    var d0 = domTransform(0); stage.style.transform = "translate(" + d0.dx + "px," + d0.dy + "px) scale(" + d0.z + ")";
    return { pose: poseDesign, dom: domTransform, gl: glPose, refresh: function () { tick(lastT); } };
  }
  /* Slow push for holds (≤1.5x, sine.inOut) when no leg/blur is wanted (§6 "slow push").
   * ANALYTIC and seek-safe: two `fromTo` tweens on one element resolve differently depending on the order the playhead
   * visited them, and the renderer splits frames across parallel workers with different seek histories — so a scene with
   * two pushes on the same stage rendered ALTERNATE FRAMES IN DIFFERENT POSITIONS (a hard flicker that never showed in
   * the Studio, which only ever plays forward). Every push on an element is therefore collected into one segment list
   * driven by a single tween that recomputes the scale from the time alone. */
  var _pushReg = [];
  function _pushEntry(node) {
    for (var i = 0; i < _pushReg.length; i++) if (_pushReg[i].node === node) return _pushReg[i];
    var e = { node: node, segs: [], drv: { t: 0 }, tween: null };
    _pushReg.push(e); return e;
  }
  function push(tl, el, T, dur, from, to, origin) {
    var node = (typeof el === "string") ? document.querySelector(el) : el;
    if (!node) return;
    var e = _pushEntry(node);
    node.style.transformOrigin = origin || "50% 50%";
    e.segs.push({ T: T, dur: dur, from: from, to: to });
    e.segs.sort(function (a, b) { return a.T - b.T; });
    var start = e.segs[0].T, end = start;
    e.segs.forEach(function (s) { if (s.T + s.dur > end) end = s.T + s.dur; });
    function scaleAt(t) {
      var segs = e.segs;
      if (t <= segs[0].T) return segs[0].from;
      for (var i = 0; i < segs.length; i++) {
        var s = segs[i];
        if (t < s.T) return segs[i - 1].to;                       // resting between two pushes
        if (t <= s.T + s.dur) return s.from + (s.to - s.from) * (-(Math.cos(Math.PI * ((t - s.T) / s.dur)) - 1) / 2);
      }
      return segs[segs.length - 1].to;
    }
    function apply() { node.style.transform = "scale(" + scaleAt(e.drv.t).toFixed(5) + ")"; }
    node.style.transform = "scale(" + e.segs[0].from + ")";
    if (e.tween) { e.tween.kill(); tl.remove(e.tween); }
    e.tween = gsap.fromTo(e.drv, { t: start }, { t: end, duration: end - start, ease: "none", immediateRender: false, onUpdate: apply });
    tl.add(e.tween, start);
  }
  /* Draw a rotated image (the artifact) into a 2D bake context in design coords. */
  function bakeImage(ctx, img, x, y, w, h, rotDeg, radius, opts) {
    var chrome = !(opts && opts.chrome === false);   // hairline + glow-bar; pass {chrome:false} when the DOM shot has none
    ctx.save(); ctx.translate(x + w / 2, y + h / 2); ctx.rotate((rotDeg || 0) * Math.PI / 180);
    if (radius) { ctx.beginPath(); var r = radius, X = -w / 2, Y = -h / 2;
      ctx.moveTo(X + r, Y); ctx.arcTo(X + w, Y, X + w, Y + h, r); ctx.arcTo(X + w, Y + h, X, Y + h, r); ctx.arcTo(X, Y + h, X, Y, r); ctx.arcTo(X, Y, X + w, Y, r); ctx.closePath(); ctx.clip(); }
    ctx.drawImage(img, -w / 2, -h / 2, w, h);
    // DS card chrome: hairline + the signature glow-bar on the top edge (matches .hf-shot::before/::after)
    if (chrome) {
    ctx.save(); ctx.lineWidth = 1; ctx.strokeStyle = "#262626"; ctx.strokeRect(-w / 2 + 0.5, -h / 2 + 0.5, w - 1, h - 1); ctx.restore();
    var g1 = ctx.createLinearGradient(-w / 4, 0, w / 4, 0); g1.addColorStop(0, "rgba(249,115,22,0)"); g1.addColorStop(0.5, "rgba(249,115,22,0.5)"); g1.addColorStop(1, "rgba(249,115,22,0)");
    ctx.save(); ctx.filter = "blur(8px)"; ctx.fillStyle = g1; ctx.fillRect(-w / 4, -h / 2 - 1, w / 2, 8); ctx.restore();
    var g2 = ctx.createLinearGradient(-w / 4, 0, w / 4, 0); g2.addColorStop(0, "rgba(251,146,60,0)"); g2.addColorStop(0.5, "rgba(251,146,60,0.9)"); g2.addColorStop(1, "rgba(251,146,60,0)");
    ctx.save(); ctx.fillStyle = g2; ctx.fillRect(-w / 4, -h / 2, w / 2, 1); ctx.restore();
    }
    ctx.restore();
  }

  root.HFHouse = { RED: RED, bezierY: bezierY, wipeIn: wipeIn, wipeOut: wipeOut, phaseWipe: phaseWipe,
    ringPath: ringPath, underlinePath: underlinePath, arrowPath: arrowPath, outlinePath: outlinePath, draw: draw, slab: slab, swap: swap,
    handwrite: handwrite, typewrite: typewrite, rasterText: rasterText, words: words, odometer: odometer, chip: chip, camera: camera, push: push, bakeImage: bakeImage };
})(typeof window !== "undefined" ? window : this);
