/*
 * HFDeepGlow — physically-inspired multi-scale bloom ("Deep Glow") for HyperFrames.
 * ----------------------------------------------------------------------------
 * NOT a single Gaussian blur. It reproduces the AE "Deep Glow" look with a real
 * bloom pipeline, expressed as a static, seek-safe SVG <filter>:
 *
 *   Source → bright-pass (luminance threshold) → N blurs at growing radii,
 *   each weighted (small=crisp core, large=atmosphere) → ADDITIVE composite
 *   (feComposite arithmetic k2=k3=1) → intensity + gentle tone compression →
 *   glow rendered UNDER the crisp source.
 *
 * Deterministic (no JS per frame) — the filter is pure. Animate the bloom by
 * tweening a {v} proxy through `setIntensity(id, v)` from your GSAP timeline
 * (e.g. bloom up on a slam, settle after) — including motion-aware use: raise
 * spread / lower intensity as velocity rises for that premium-UI "energy".
 *
 * USAGE
 *   // 1. inject once into the composition (adds a hidden <svg><defs>)
 *   var id = HFDeepGlow.inject({ threshold: 0.5, intensity: 1.2, tint: "source" });
 *   el.style.filter = "url(#" + id + ")";        // apply to any DOM/text element
 *   // 2. (optional) animate the bloom from the timeline
 *   var g = { v: 0.5 };
 *   tl.to(g, { v: 1.7, duration: 0.4, ease: "expo.out",
 *              onUpdate: function(){ HFDeepGlow.setIntensity(id, g.v); } }, T);
 *
 * Glow brightens toward the tint — use on darker backgrounds (bright text on a
 * dark band). On white it has little to brighten.
 * ==========================================================================*/
(function (root) {
  "use strict";

  var _n = 0;
  var DEFAULTS = {
    threshold: 0.5,                       // luminance (0..1) below which nothing glows
    intensity: 1.2,                       // overall gain on the summed glow (animatable)
    levels: [4, 12, 28, 64, 120],        // blur radii (px) — small=core, large=atmosphere
    weights: [1, 0.85, 0.6, 0.4, 0.22],   // per-level contribution (falloff)
    tint: "source",                       // "source" keeps text colour; or a CSS colour for a coloured bloom
    region: 130                           // filter padding, % (must exceed the largest radius)
  };

  // Build the <filter> markup for a given id + options.
  function filterMarkup(id, opts) {
    opts = opts || {};
    var threshold = opts.threshold == null ? DEFAULTS.threshold : opts.threshold;
    var intensity = opts.intensity == null ? DEFAULTS.intensity : opts.intensity;
    var levels = opts.levels || DEFAULTS.levels;
    var weights = opts.weights || DEFAULTS.weights;
    var tint = opts.tint || DEFAULTS.tint;
    var region = opts.region == null ? DEFAULTS.region : opts.region;

    var p = [];
    // --- bright-pass: keep only pixels above the luminance threshold ---
    p.push('<feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0.2126 0.7152 0.0722 0 0" result="dg-luma"/>');
    // linear ramp approximates a soft step at `threshold`
    var slope = 10, intercept = -(slope * threshold);
    p.push('<feComponentTransfer in="dg-luma" result="dg-mask"><feFuncA type="linear" slope="' + slope + '" intercept="' + intercept + '"/></feComponentTransfer>');
    if (tint === "source") {
      p.push('<feComposite in="SourceGraphic" in2="dg-mask" operator="in" result="dg-bright"/>');
    } else {
      p.push('<feFlood flood-color="' + tint + '" result="dg-flood"/>');
      p.push('<feComposite in="dg-flood" in2="dg-mask" operator="in" result="dg-bright"/>');
    }
    // --- multi-scale blur + per-level weighting ---
    var layers = [];
    for (var i = 0; i < levels.length; i++) {
      var w = weights[i] == null ? 0.3 : weights[i];
      p.push('<feGaussianBlur in="dg-bright" stdDeviation="' + levels[i] + '" result="dg-b' + i + '"/>');
      p.push('<feComponentTransfer in="dg-b' + i + '" result="dg-w' + i + '">' +
        '<feFuncR type="linear" slope="' + w + '"/><feFuncG type="linear" slope="' + w + '"/>' +
        '<feFuncB type="linear" slope="' + w + '"/><feFuncA type="linear" slope="' + w + '"/></feComponentTransfer>');
      layers.push('dg-w' + i);
    }
    // --- additive composite of all levels ---
    var prev = layers[0];
    for (var j = 1; j < layers.length; j++) {
      var out = (j === layers.length - 1) ? 'dg-glowraw' : 'dg-sum' + j;
      p.push('<feComposite in="' + prev + '" in2="' + layers[j] + '" operator="arithmetic" k1="0" k2="1" k3="1" k4="0" result="' + out + '"/>');
      prev = out;
    }
    var glowIn = layers.length > 1 ? 'dg-glowraw' : layers[0];
    // --- intensity (animatable via id-tagged funcs) + gentle highlight tone compression ---
    p.push('<feComponentTransfer in="' + glowIn + '" result="dg-glow">' +
      '<feFuncR id="' + id + '-r" type="linear" slope="' + intensity + '"/>' +
      '<feFuncG id="' + id + '-g" type="linear" slope="' + intensity + '"/>' +
      '<feFuncB id="' + id + '-b" type="linear" slope="' + intensity + '"/>' +
      '<feFuncA type="gamma" amplitude="1" exponent="0.9" offset="0"/></feComponentTransfer>');
    // --- glow under the crisp source ---
    p.push('<feMerge><feMergeNode in="dg-glow"/><feMergeNode in="SourceGraphic"/></feMerge>');

    return '<filter id="' + id + '" x="-' + region + '%" y="-' + region + '%" width="' + (100 + region * 2) + '%" height="' + (100 + region * 2) + '%" color-interpolation-filters="sRGB">' + p.join('') + '</filter>';
  }

  // Inject a filter into the document; returns its id. Reuses one hidden <svg> host.
  function inject(opts) {
    opts = opts || {};
    var id = opts.id || ('hf-deepglow-' + (++_n));
    var host = document.getElementById('hf-deepglow-host');
    if (!host) {
      host = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      host.setAttribute('id', 'hf-deepglow-host');
      host.setAttribute('width', '0'); host.setAttribute('height', '0');
      host.setAttribute('aria-hidden', 'true');
      host.style.position = 'absolute';
      (document.body || document.documentElement).appendChild(host);
    }
    var defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    defs.innerHTML = filterMarkup(id, opts);
    host.appendChild(defs);
    return id;
  }

  // Animate the bloom gain (call from a GSAP onUpdate). Tweak spread separately if needed.
  function setIntensity(id, v) {
    var ch = ['r', 'g', 'b'];
    for (var i = 0; i < 3; i++) {
      var f = document.getElementById(id + '-' + ch[i]);
      if (f) f.setAttribute('slope', v);
    }
  }

  root.HFDeepGlow = { filterMarkup: filterMarkup, inject: inject, setIntensity: setIntensity, DEFAULTS: DEFAULTS };
  if (typeof module !== "undefined" && module.exports) module.exports = root.HFDeepGlow;
})(typeof window !== "undefined" ? window : this);
