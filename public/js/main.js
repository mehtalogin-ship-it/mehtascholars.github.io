/* ============================================================
   Mehta Scholars — shared site behaviour
   ============================================================ */

/* ---- Hosted live chat (replaces the old Wix Chat widget) ----
   Paste your Tawk.to (or Crisp) embed src below to enable it.
   Leave TAWK_SRC empty to keep chat disabled.
   Get the src at: dashboard.tawk.to → Administration → Chat Widget
   e.g. 'https://embed.tawk.to/PROPERTY_ID/WIDGET_ID'
*/
var TAWK_SRC = '';
(function loadChat() {
  if (!TAWK_SRC) return; // disabled until an ID is provided
  window.Tawk_API = window.Tawk_API || {};
  var s = document.createElement('script');
  s.async = true;
  s.src = TAWK_SRC;
  s.charset = 'UTF-8';
  s.setAttribute('crossorigin', '*');
  document.head.appendChild(s);
})();

/* ---- Mobile nav toggle ---- */
document.addEventListener('click', function (e) {
  if (e.target.closest('.nav-toggle')) {
    document.querySelector('.nav-links').classList.toggle('open');
  }
});

/* ---- Scroll-in reveal animations (rebuilt from Wix motion) ---- */
document.addEventListener('DOMContentLoaded', function () {
  var targets = document.querySelectorAll(
    '.card, .invest-card, .member, .founder, .step, .section-head, .pill, .class-block, .bio-card'
  );
  if (!('IntersectionObserver' in window) || !targets.length) return;

  targets.forEach(function (el, i) {
    el.classList.add('reveal');
    el.style.transitionDelay = (Math.min(i % 8, 6) * 0.05) + 's';
  });

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('in-view');
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

  targets.forEach(function (el) { io.observe(el); });
});

/* ---- Alumni companies stage / category filter ---- */
document.addEventListener('DOMContentLoaded', function () {
  var filterBar = document.querySelector('.filters');
  if (!filterBar) return;

  var buttons = filterBar.querySelectorAll('.filter-btn');
  var groups = document.querySelectorAll('[data-stage-group]');
  var items = document.querySelectorAll('[data-sector]');

  function apply(cat) {
    items.forEach(function (f) {
      var cats = (f.dataset.sector || 'all').split(' ');
      f.style.display = (cat === 'all' || cats.indexOf(cat) !== -1) ? '' : 'none';
    });
    groups.forEach(function (g) {
      var anyVisible = false;
      g.querySelectorAll('[data-sector]').forEach(function (f) {
        if (f.style.display !== 'none') anyVisible = true;
      });
      g.style.display = anyVisible ? '' : 'none';
    });
  }

  buttons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      buttons.forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
      apply(btn.dataset.filter);
    });
  });

  var hash = location.hash.replace('#', '');
  if (hash) {
    var match = Array.prototype.find.call(buttons, function (b) { return b.dataset.filter === hash; });
    if (match) match.click();
  }
});

/* ---- Cinematic intro + LED screen in one pinned scroll ----
   Phase A (scroll 0 .. FV): scrub the video frame sequence.
   Phase B (FV .. 1): hold the last frame; power on the LED screen and play the slides.
   Merged so there is no second section / no in-between scroll. */
(function () {
  var stage = document.getElementById('introStage');
  var canvas = document.getElementById('introCanvas');
  if (!stage || !canvas) return;
  var ctx = canvas.getContext('2d');
  var N = parseInt(stage.getAttribute('data-frames'), 10) || 80;
  var FV = parseFloat(stage.getAttribute('data-video-end')) || 0.45; // share of scroll spent flying
  // Two encodes of the same 80 frames. Pick by the device pixels actually needed
  // across the viewport, not by DPR alone - a 375px phone at DPR 2 only needs 750px,
  // so it takes the 1280 set and downloads less than the old 720p JPEGs did.
  var need = window.innerWidth * Math.min(window.devicePixelRatio || 1, 2);
  var hd = need > 1280;
  var base = 'assets/intro/' + (hd ? 'hd/' : 'sd/');
  var SW = hd ? 1920 : 1280, SH = hd ? 1080 : 720;
  // Size the backing store to the device pixels actually on screen and do the cover
  // scale ourselves with a high-quality filter. Leaving the canvas at source size and
  // letting CSS stretch it means a second, cheaper resample on top of the first.
  function sizeCanvas() {
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var w = Math.round(canvas.clientWidth * dpr), h = Math.round(canvas.clientHeight * dpr);
    if (!w || !h) { w = SW; h = SH; }
    if (canvas.width !== w || canvas.height !== h) {
      canvas.width = w; canvas.height = h;
      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = 'high';
      current = -1;
    }
  }

  var imgs = new Array(N);
  var current = -1;
  var overlay = stage.querySelector('.intro-overlay');
  var heroBox = stage.querySelector('.hero-box');
  var cue = stage.querySelector('.intro-cue');
  var screen = stage.querySelector('.wall-screen');
  var slides = [].slice.call(stage.querySelectorAll('.ws-slide'));
  var cards = [].slice.call(stage.querySelectorAll('.ws-card'));
  var dotsWrap = stage.querySelector('.wall-dots');
  var dots = [].slice.call(stage.querySelectorAll('.wall-dot'));
  var th = [0.08, 0.26, 0.44];
  var glow = stage.querySelector('.ws-power');
  var POWER_AT = 0.10, POWER_OVER = 0.10;  // dark beat, then the screen comes up
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function clamp(x) { return x < 0 ? 0 : x > 1 ? 1 : x; }
  function smooth(t) { return t * t * (3 - 2 * t); }
  function pad(n) { return ('000' + n).slice(-3); }
  function ok(im) { return im && im.complete && im.naturalWidth > 0; }
  function pick(i) {
    if (ok(imgs[i])) return i;
    for (var d = 1; d < N; d++) {
      if (i - d >= 0 && ok(imgs[i - d])) return i - d;
      if (i + d < N && ok(imgs[i + d])) return i + d;
    }
    return -1;
  }
  function draw(i) {
    if (!ok(imgs[i])) return;
    // cover: fill the canvas, cropping the overflowing axis
    var cw = canvas.width, ch = canvas.height, s = Math.max(cw / SW, ch / SH);
    var dw = SW * s, dh = SH * s;
    ctx.drawImage(imgs[i], (cw - dw) / 2, (ch - dh) / 2, dw, dh);
    current = i;
  }

  // The hero panel is flown past the camera like a roadside sign. The perspective
  // parent puts the vanishing point at frame centre and the panel sits left of it,
  // so pushing translateZ carries it outward, off the left edge, accelerating on its
  // own the way real perspective does. rotateY turns it edge-on as it goes by.
  // The vanishing point is parked to the right of the panel (perspective-origin 72%)
  // so every corner diverges the same way and the panel sweeps clean off the left edge.
  // With the origin at frame centre the panel straddles it and just engulfs the screen.
  // Z ramps a little faster than linear so it looms; X ramps on a square so the exit
  // whips at the end, the way a sign does once it reaches the window.
  var FLY = 0.34; // fraction of the flight over which the sign passes
  function flyBy(vp) {
    if (!heroBox) return;
    var f = clamp(vp / FLY);
    if (reduce) { heroBox.style.transform = ''; heroBox.style.opacity = String(1 - f); return; }
    var e = Math.pow(f, 1.25);
    var z = 820 * e;                                 // looming toward the camera
    var x = -34 * f * f;                             // lateral exit, in vw, accelerating
    var rot = -20 * e;                               // turning edge-on as it goes by
    var drop = 3 * e;                                // settles just below the eye line
    heroBox.style.transform = 'translate3d(' + x.toFixed(2) + 'vw,' + drop.toFixed(2) + 'vh,' + z.toFixed(1) + 'px) rotateY(' + rot.toFixed(2) + 'deg)';
    // On wide screens it is geometrically gone before this matters; on narrow ones,
    // where there is less room to diverge, the fade finishes the job.
    heroBox.style.opacity = String(1 - smooth(clamp((f - 0.62) / 0.38)));
    heroBox.style.pointerEvents = f > 0.04 ? 'none' : 'auto';
  }

  function update() {
    var range = stage.offsetHeight - window.innerHeight;
    var p = clamp((window.scrollY - stage.offsetTop) / range);

    // Phase A - scrub the flight
    var vp = Math.min(1, p / FV);
    var frame = pick(Math.round(vp * (N - 1)));
    if (frame !== -1 && frame !== current) draw(frame);
    flyBy(vp);
    if (cue) cue.style.opacity = String(Math.max(0, 0.85 * (1 - vp / 0.3)));

    // The last frames of the flight are true black, so the wall content simply fades
    // up over them. No panel to place, no texture to swap, no bezel to align.
    var on = clamp((vp - 0.92) / 0.07);
    if (screen) screen.style.opacity = String(on);

    // Phase B - the wall's slides
    var q = Math.min(0.9999, Math.max(0, (p - FV) / (1 - FV)));
    // The wall sits dark for a beat after the flight lands, then powers on.
    var power = clamp((q - POWER_AT) / POWER_OVER);
    if (glow) glow.style.opacity = String(power);
    stage.classList.toggle('lit', power > 0.5);
    if (dotsWrap) dotsWrap.style.opacity = String(power);
    var idx = q < 0.62 ? 0 : 1;
    slides.forEach(function (s, i) { s.classList.toggle('is-active', i === idx); });
    dots.forEach(function (d, i) { d.classList.toggle('is-on', i === idx); });
    cards.forEach(function (c, i) { c.classList.toggle('show', idx > 0 || q >= th[i]); });
  }

  for (var i = 0; i < N; i++) {
    (function (i) {
      var im = new Image();
      im.onload = function () { if (current === -1) draw(pick(0)); else if (i === current) draw(i); };
      im.src = base + 'f_' + pad(i + 1) + '.webp?v=1';
      imgs[i] = im;
    })(i);
  }
  window.addEventListener('scroll', update, { passive: true });
  window.addEventListener('resize', function () { sizeCanvas(); update(); });
  sizeCanvas();
  update();
})();

/* ---- About: scroll-built process flowchart (connectors draw, nodes light,
        a 3x refinement loop draws out then is reabsorbed, and the tail splits & merges) ---- */
(function () {
  var proc = document.getElementById('procDiagram');
  if (!proc) return;
  var steps = [].slice.call(proc.querySelectorAll('.pf-step'));
  var segs = [].slice.call(proc.querySelectorAll('.pf-seg'));
  var tier1 = document.getElementById('pfTier1');
  var tier2 = document.getElementById('pfTier2');
  var split = document.getElementById('pfSplit');
  var sub = document.getElementById('pfSub');
  var merge3 = document.getElementById('pfMerge3');
  var review = document.getElementById('pfReview');
  var loop = review ? review.querySelector('.pf-loop') : null;
  var loopFill = loop ? loop.querySelector('.pf-loopwire > i') : null;
  proc.classList.add('armed');
  function clamp(x) { return Math.max(0, Math.min(1, x)); }
  function setX(el, left, width) { if (!el) return; el.style.left = left + 'px'; if (width != null) el.style.width = width + 'px'; }
  function geom() {
    // position every fork/merge bar + branch drop against measured box centres
    if (!tier1 || !tier2 || !split || !sub || !merge3) return;
    var t1r = tier1.getBoundingClientRect();
    var r1b = tier1.querySelector('.r1 .pf-box'), r2b = tier1.querySelector('.r2 .pf-box');
    if (!r1b || !r2b) return;
    var cx = function (el, ref) { var b = el.getBoundingClientRect(); return (b.left + b.width / 2) - ref.left; };
    var r1c = cx(r1b, t1r), r2c = cx(r2b, t1r);
    var terms = tier2.querySelectorAll('.pf-box');
    if (terms.length < 3) return;
    var t2r = tier2.getBoundingClientRect();
    var a = cx(terms[0], t2r), b = cx(terms[1], t2r), c = cx(terms[2], t2r); // $25K, $10K, no-inv centres
    var mid = t1r.width / 2;
    // split: decision(50%) -> R1 (r1c) + R2 (r2c)
    setX(split.querySelector('.downL'), r1c - 1.5);
    setX(split.querySelector('.downR'), r2c - 1.5);
    setX(split.querySelector('.barL'), r1c, mid - r1c);
    setX(split.querySelector('.barR'), mid, r2c - mid);
    // sub: R1 straight down to $25K (r1c==a); R2 (r2c) forks to $10K (b) + no-inv (c)
    setX(sub.querySelector('.r1down'), r1c - 1.5);
    setX(sub.querySelector('.r2stem'), r2c - 1.5);
    setX(sub.querySelector('.subdownL'), b - 1.5);
    setX(sub.querySelector('.subdownR'), c - 1.5);
    setX(sub.querySelector('.subbarL'), b, r2c - b);
    setX(sub.querySelector('.subbarR'), r2c, c - r2c);
    // merge: $25K(a) + $10K(b) + no-inv(c) -> final (50%)
    setX(merge3.querySelector('.up1'), a - 1.5);
    setX(merge3.querySelector('.up2'), b - 1.5);
    setX(merge3.querySelector('.up3'), c - 1.5);
    setX(merge3.querySelector('.m3barL'), a, mid - a);
    setX(merge3.querySelector('.m3barR'), mid, c - mid);
  }
  function build() {
    var line = window.innerHeight * 0.72;
    steps.forEach(function (s) {
      var m = s.querySelector('.pf-medal') || s;
      s.classList.toggle('pf-lit', m.getBoundingClientRect().top < line);
    });
    segs.forEach(function (sg) {
      var fi = sg.querySelector('i'); if (!fi) return;
      var r = sg.getBoundingClientRect();
      if (sg.classList.contains('horiz')) fi.style.transform = 'scaleX(' + clamp((line - r.top) / 26) + ')';
      else fi.style.transform = 'scaleY(' + clamp((line - r.top) / r.height) + ')';
    });
    // the 3x refinement loop: draw out to the right, hold, then get reabsorbed
    if (loop && loopFill && review) {
      var box = review.querySelector('.pf-box').getBoundingClientRect();
      var d = line - (box.top + box.height / 2); // px the reveal line is past the review box's centre
      var w = 0, drawn = false;
      if (d < 0) { w = 0; }
      else if (d < 70) { w = d / 70; drawn = d > 14; }
      else if (d < 175) { w = 1; drawn = true; }
      else if (d < 255) { w = 1 - (d - 175) / 80; drawn = false; }  // absorb
      else { w = 0; }
      loopFill.style.transform = 'scaleX(' + w + ')';
      loop.classList.toggle('draw', drawn);
    }
  }
  geom();
  build();
  window.addEventListener('scroll', build, { passive: true });
  window.addEventListener('resize', function () { geom(); build(); });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { geom(); build(); });
})();
