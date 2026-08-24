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
  var N = parseInt(stage.getAttribute('data-frames'), 10) || 140;
  var FV = parseFloat(stage.getAttribute('data-video-end')) || 0.34; // fraction of scroll spent on the video
  var base = 'assets/intro/';
  var imgs = new Array(N);
  var current = -1;
  var pin = stage.querySelector('.intro-pin');
  var overlay = stage.querySelector('.intro-overlay');
  var cue = stage.querySelector('.intro-cue');
  var screen = stage.querySelector('.wall-screen');
  var texhd = stage.querySelector('.wall-tex-hd');
  var slides = [].slice.call(stage.querySelectorAll('.ws-slide'));
  var cards = [].slice.call(stage.querySelectorAll('.ws-card'));
  var dotsWrap = stage.querySelector('.wall-dots');
  var dots = [].slice.call(stage.querySelectorAll('.wall-dot'));
  var th = [0.08, 0.26, 0.44];
  // Black-screen rectangle inside the final frame (assets/intro/f_140.jpg, 1280x720)
  var FW = 1280, FH = 720, RX0 = 206, RY0 = 132, RX1 = 1075, RY1 = 623;
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
    if (ok(imgs[i])) { ctx.drawImage(imgs[i], 0, 0, canvas.width, canvas.height); current = i; }
  }
  function place() {
    if (!pin || !screen) return;
    var pw = pin.clientWidth, ph = pin.clientHeight, scale, offX, offY;
    if (pw / ph > FW / FH) { scale = pw / FW; offX = 0; offY = (ph - FH * scale) / 2; }
    else { scale = ph / FH; offY = 0; offX = (pw - FW * scale) / 2; }
    screen.style.left = (offX + RX0 * scale) + 'px';
    screen.style.top = (offY + RY0 * scale) + 'px';
    screen.style.width = ((RX1 - RX0) * scale) + 'px';
    screen.style.height = ((RY1 - RY0) * scale) + 'px';
  }
  function update() {
    var range = stage.offsetHeight - window.innerHeight;
    var p = Math.min(1, Math.max(0, (window.scrollY - stage.offsetTop) / range));
    // Phase A — video scrub
    var vp = Math.min(1, p / FV);
    var frame = pick(Math.round(vp * (N - 1)));
    if (frame !== -1 && frame !== current) draw(frame);
    if (overlay) overlay.style.opacity = Math.max(0, 1 - vp / 0.5);
    if (cue) cue.style.opacity = Math.max(0, 0.85 * (1 - vp / 0.3));
    // Landing — as the flight's last frames lock the screen into full frame
    // (~frames 130-138), power the LED screen on FIRST (over the black screen, so a
    // screen is always present), THEN switch the wall to crisp travertine. Driven by
    // the video progress (vp) so the wall goes clean the moment the screen is framed,
    // not only once the flight formally ends.
    var q = Math.min(0.9999, Math.max(0, (p - FV) / (1 - FV)));
    var scr = Math.min(1, Math.max(0, (vp - 0.925) / 0.012));   // screen snaps on: ~frame 130 -> 132
    if (screen) screen.style.opacity = scr;
    if (dotsWrap) dotsWrap.style.opacity = scr;
    if (texhd) texhd.style.opacity = Math.min(1, Math.max(0, (vp - 0.940) / 0.014)); // clean wall: ~frame 132 -> 134
    var idx = q < 0.62 ? 0 : 1;
    slides.forEach(function (s, i) { s.classList.toggle('is-active', i === idx); });
    dots.forEach(function (d, i) { d.classList.toggle('is-on', i === idx); });
    cards.forEach(function (c, i) { c.classList.toggle('show', idx > 0 || q >= th[i]); });
  }
  for (var i = 0; i < N; i++) {
    (function (i) {
      var im = new Image();
      im.onload = function () { if (current === -1) draw(pick(0)); else if (i === current) draw(i); };
      im.src = base + 'f_' + pad(i + 1) + '.jpg?v=2';
      imgs[i] = im;
    })(i);
  }
  window.addEventListener('scroll', update, { passive: true });
  window.addEventListener('resize', function () { place(); update(); });
  place();
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
