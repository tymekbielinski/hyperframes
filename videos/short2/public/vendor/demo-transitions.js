/*
 * HFDemoTransitions — transition + camera kit for product-demo shorts.
 * Implements context/product-demo-style.md §2 (camera rig) and §6 (transitions).
 *
 * Plain, dependency-free (GSAP must already be on the page). Seek-safe:
 * every helper only ADDS tweens to a caller-owned paused timeline at explicit
 * times — no wall-clock, no infinite repeats, no tween-time DOM measurement.
 *
 * Scene contract (from hyperframes-animation transitions catalog):
 *  - scene 1 visible by default; scenes 2+ start with `opacity: 0` in CSS
 *  - outgoing + incoming animate at the SAME time T (the transition IS the exit)
 *  - colors come from the caller's stylesheet / frame.md tokens, never from here
 */
(function (global) {
  "use strict";

  var PLATEAU_SVG = "M0,0 C0.12,0 0.10,1 1,1";

  /** Register the plateau ease. Returns the ease name to use ("plateau",
   *  or "expo.inOut" when CustomEase isn't loaded). Call once at setup. */
  function registerPlateau() {
    if (global.CustomEase && !gsap.parseEase("plateau")) {
      global.CustomEase.create("plateau", PLATEAU_SVG);
    }
    return gsap.parseEase("plateau") ? "plateau" : "expo.inOut";
  }

  /* ------------------------------------------------------------------ */
  /* Tier 0 — camera                                                     */
  /* ------------------------------------------------------------------ */

  /** One camera leg: fly the `.cam` wrapper to a pre-computed pose.
   *  pose = { x, y, scale } — constants computed at setup, never measured
   *  at tween time. dur defaults to 0.75s per the spec's 0.6–0.9s band. */
  function cameraLeg(tl, camEl, pose, T, dur) {
    tl.to(camEl, {
      x: pose.x, y: pose.y, scale: pose.scale == null ? 1 : pose.scale,
      duration: dur == null ? 0.75 : dur,
      ease: registerPlateau(),
    }, T);
    return tl;
  }

  /** Handheld micro-drift on a dedicated sub-wrapper (NOT the leg wrapper,
   *  so drift composes with legs). Deterministic: pattern derives from `seed`.
   *  Fills [T, T + total] with finite sine yoyo tweens.
   *  opts: { amp: 8, rot: 0.15, breathe: 0.008, period: 5.5, seed: 1 } */
  function microDrift(tl, driftEl, T, total, opts) {
    opts = opts || {};
    var amp = opts.amp == null ? 8 : opts.amp;
    var rot = opts.rot == null ? 0.15 : opts.rot;
    var br = opts.breathe == null ? 0.008 : opts.breathe;
    var period = opts.period == null ? 5.5 : opts.period;
    var seed = opts.seed == null ? 1 : opts.seed;
    // Deterministic pseudo-random direction pattern from the seed.
    function rnd(i) { var v = Math.sin(seed * 127.1 + i * 311.7) * 43758.5453; return v - Math.floor(v); }
    var n = Math.max(1, Math.ceil(total / period));
    for (var i = 0; i < n; i++) {
      var t0 = T + i * period;
      var d = Math.min(period, T + total - t0);
      tl.to(driftEl, {
        x: (rnd(i) * 2 - 1) * amp,
        y: (rnd(i + 50) * 2 - 1) * amp,
        rotation: (rnd(i + 100) * 2 - 1) * rot,
        scale: 1 + rnd(i + 150) * br,
        duration: d,
        ease: "sine.inOut",
      }, t0);
    }
    return tl;
  }

  /* ------------------------------------------------------------------ */
  /* Tier 1 — primary: blur crossfade / focus pull                       */
  /* ------------------------------------------------------------------ */

  /** opts: { duration: 0.5, blur: 12, lag: 0.1 } */
  function blurCrossfade(tl, oldEl, newEl, T, opts) {
    opts = opts || {};
    var dur = opts.duration == null ? 0.5 : opts.duration;
    var blur = opts.blur == null ? 12 : opts.blur;
    var lag = opts.lag == null ? 0.1 : opts.lag;
    tl.to(oldEl, {
      opacity: 0, filter: "blur(" + blur + "px)", scale: 1.03,
      duration: dur, ease: "power2.inOut",
    }, T);
    tl.fromTo(newEl,
      { opacity: 0, filter: "blur(" + blur + "px)", scale: 0.97 },
      { opacity: 1, filter: "blur(0px)", scale: 1, duration: dur, ease: "power2.out" },
      T + lag);
    // Rewind safety: restore outgoing state when scrubbed back is handled by
    // GSAP fromTo/to pairs themselves — no onComplete hides.
    return tl;
  }

  /* ------------------------------------------------------------------ */
  /* Tier 2 — accents (use each at most once per video)                  */
  /* ------------------------------------------------------------------ */

  /** Zoom through: camera pushes INTO the outgoing scene; incoming resolves
   *  from inside the zoom. opts: { duration: 0.6, push: 2.6, blur: 8 } */
  function zoomThrough(tl, oldEl, newEl, T, opts) {
    opts = opts || {};
    var dur = opts.duration == null ? 0.6 : opts.duration;
    var push = opts.push == null ? 2.6 : opts.push;
    var blur = opts.blur == null ? 8 : opts.blur;
    tl.to(oldEl, {
      scale: push, opacity: 0, filter: "blur(" + blur + "px)",
      duration: dur, ease: "power3.in",
    }, T);
    tl.fromTo(newEl,
      { scale: 0.8, opacity: 0, filter: "blur(" + blur + "px)" },
      { scale: 1, opacity: 1, filter: "blur(0px)", duration: dur, ease: "power3.out" },
      T + dur * 0.55);
    return tl;
  }

  /** Color dip: dip through a caller-styled full-frame overlay (give it the
   *  primary brand color in CSS; it must start `opacity: 0`).
   *  opts: { duration: 0.6, hold: 0.1 } — duration is the full dip. */
  function colorDip(tl, oldEl, newEl, dipEl, T, opts) {
    opts = opts || {};
    var dur = opts.duration == null ? 0.6 : opts.duration;
    var hold = opts.hold == null ? 0.1 : opts.hold;
    var half = (dur - hold) / 2;
    tl.fromTo(dipEl, { opacity: 0 }, { opacity: 1, duration: half, ease: "power2.in" }, T);
    tl.set(oldEl, { opacity: 0 }, T + half);
    tl.set(newEl, { opacity: 1 }, T + half);
    tl.to(dipEl, { opacity: 0, duration: half, ease: "power2.out" }, T + half + hold);
    return tl;
  }

  global.HFDemoTransitions = {
    PLATEAU_SVG: PLATEAU_SVG,
    registerPlateau: registerPlateau,
    cameraLeg: cameraLeg,
    microDrift: microDrift,
    blurCrossfade: blurCrossfade,
    zoomThrough: zoomThrough,
    colorDip: colorDip,
  };
})(typeof window !== "undefined" ? window : globalThis);
