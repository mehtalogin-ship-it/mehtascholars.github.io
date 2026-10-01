# -*- coding: utf-8 -*-
import json, re, os, shutil

# GitHub Pages serves public/, so generated HTML and the assets it references go
# there. The source data stays at the repo root, alongside this script - it is input,
# not something to publish.
BASE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.join(BASE,'public')   # output: generated HTML + assets
CAP=os.path.join(BASE,'captured')+'/'  # input: captured/*.json
founders=json.load(open(CAP+'founders.json'))
companies=json.load(open(CAP+'companies.json'))
com=json.load(open(CAP+'committee.json'))
committee=com['members']; sections=com['sections']
try: PHOTOS=json.load(open(CAP+'photo_map.json'))
except Exception: PHOTOS={}

CATLABEL={'ai':'AI and Smart Tech','health':'Health Tech & Life Sciences','fintech':'Fintech'}

# ============================================================================
# TWO SITES, ONE GENERATOR
# ----------------------------------------------------------------------------
# mehtascholars.com is the Mehta Scholars program; harkervii.com is the Harker
# Venture Investment Initiative, the ecosystem as a whole. They share data
# (captured/), styles and assets, so both are built here, and every PAGES row
# says which site it belongs to. The two sites do not link to each other; the
# only crossings are redirect stubs on mehtascholars.com for pages that moved.
#
#   ms   -> public/      committed, deployed from this repo
#   vii  -> public-vii/  NOT committed (it would duplicate ~130 MB of assets);
#                        CI rebuilds it and pushes it to the harkervii repo
# ============================================================================
SITES={
 'ms':  dict(root=ROOT, url='https://www.mehtascholars.com/',
             brand='Harker<br>Mehta Scholars', name='Harker Mehta Scholars',
             blurb='Mehta Scholars serve as analysts for The Harker Venture Pool, researching, supporting, and investing in Harker alumni founders.'),
 'vii': dict(root=os.path.join(BASE,'public-vii'), url='https://www.harkervii.com/', cname='www.harkervii.com',
             brand='Harker Venture<br>Investment Initiative', name='Harker Venture Investment Initiative',
             blurb='Connecting Harker students, alumni, parents, and parents of alumni who are entrepreneurs, investors, and business &amp; technology professionals.'),
}
S=SITES['ms']   # the site being built; reassigned by the build loop at the bottom

def initials(name):
    # Names carry a class year ("Ravi Belani '90"), so drop any trailing year
    # token first - otherwise the fallback avatar reads "R'" instead of "RB".
    p=[x for x in re.split(r'\s+',name.strip()) if x]
    p=[x for x in p if not re.match(r"^[\u2018\u2019']?\d{2,4}$", x)] or p
    if not p: return '?'
    return (p[0][0]+(p[-1][0] if len(p)>1 else '')).upper()

def slug(s):
    s=re.sub(r"[^a-z0-9]+","-",s.lower()).strip('-')
    return s or 'company'

def esc(t): return (t or '').replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

FONTS='<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Questrial&family=Playfair+Display:wght@500;600&family=Montserrat:wght@400;500;600&display=swap" rel="stylesheet">'

SEAL='''<svg class="seal" viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="48" fill="#0a582a"/><circle cx="50" cy="50" r="40" fill="none" stroke="#d9c67a" stroke-width="2"/><text x="50" y="46" text-anchor="middle" fill="#fff" font-family="Questrial, sans-serif" font-size="15">THE</text><text x="50" y="62" text-anchor="middle" fill="#d9c67a" font-family="Questrial, sans-serif" font-size="15">MEHTA</text><text x="50" y="82" text-anchor="middle" fill="#fff" font-family="Questrial, sans-serif" font-size="7" letter-spacing="1">ENDOWMENT</text></svg>'''

# ============================================================================
# PAGE REGISTRY
# ----------------------------------------------------------------------------
# The single source of truth for "what pages exist and what is on them".
# nav(), footer(), the build loop and sitemap.xml all read PAGES, so adding a
# page, renaming one, regrouping the nav into tracks, or moving a section from
# one page to another is an edit HERE - not a rewrite of a page template.
#
#   slug   output filename minus .html, and the URL
#   key    nav "active" key (kept distinct from slug so the markup is stable)
#   label  nav/footer text
#   track  nav group; must be a key in TRACKS
#   drop   [(anchor, label)] -> hover dropdown under this nav item
#   hero   ('h1', 'sub', 'cls') for sec_hero(), or None to draw its own
#   body   ordered callables -> HTML fragments
#   foot   include in the footer Explore column
#
# The two-track restructure is: change some `track` values and swap TRACKS for
# its two-entry form. nav() itself does not change.
# ============================================================================

TRACKS=[('main',None)]

CTA=('Contact Us!','mailto:MehtaScholars@harker.org')

# The initiative's private LinkedIn group, and the interest form. The form is not
# built yet: while INTEREST_FORM is empty the button renders as a non-clickable
# "coming soon" placeholder, so nobody lands on a dead link. Paste the Google Form
# URL here and regenerate - every page that shows the button picks it up.
LINKEDIN_GROUP='https://www.linkedin.com/groups/14619102/'
INTEREST_FORM=''

_ICO_LI='<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9.75h4V21H3zM9.5 9.75h3.83v1.54h.06c.53-1 1.84-2.06 3.79-2.06 4.05 0 4.8 2.67 4.8 6.13V21h-4v-4.98c0-1.19-.02-2.72-1.66-2.72-1.66 0-1.92 1.3-1.92 2.63V21h-4z"/></svg>'

def join_buttons(cls=''):
    """'Join Now' (LinkedIn group) + 'Express Interest' (the form, or a placeholder)."""
    join=f'<a class="btn" href="{LINKEDIN_GROUP}" target="_blank" rel="noopener">{_ICO_LI}Join Now</a>'
    if INTEREST_FORM:
        form=f'<a class="btn outline" href="{INTEREST_FORM}" target="_blank" rel="noopener">Express Interest</a>'
    else:
        form='<span class="btn outline is-soon" aria-disabled="true">Express Interest<small>Form coming soon</small></span>'
    c=f' {cls}' if cls else ''
    return f'<div class="join-btns{c}">{join}{form}</div>'

def _href(h, p=''):
    """Leave mailto:/http(s)/#/tel alone; prefix internal links with the page's
    depth. Lets the nav CTA become a real contact page later without touching nav()."""
    return h if re.match(r'^(mailto:|https?:|#|tel:)', h) else p+h

def nav(active, p=''):
    def cls(k): return ' class="active"' if k==active else ''
    def link(pg): return f'<a href="{p}{pg["slug"]}.html"{cls(pg["key"])}>{pg["label"]}</a>'
    items=[]
    for tr,heading in TRACKS:
        grp=[pg for pg in site_pages() if pg.get('track')==tr and pg.get('label')]
        if not grp: continue
        if heading:
            # A named track renders as ONE nav item with a dropdown, reusing the
            # .has-drop component that already exists for Alumni Companies -
            # so a two-track nav needs no new CSS.
            on=' class="active"' if any(pg['key']==active for pg in grp) else ''
            sub=''.join(f'\n            <li>{link(pg)}</li>' for pg in grp)
            items.append(f'<li class="has-drop"><a href="{p}{grp[0]["slug"]}.html"{on}>{heading}</a>\n          <ul class="drop">{sub}\n          </ul></li>')
            continue
        for pg in grp:
            if pg.get('drop'):
                sub=''.join(f'\n            <li><a href="{p}{pg["slug"]}.html#{k}">{lbl}</a></li>' for k,lbl in pg['drop'])
                items.append(f'<li class="has-drop">{link(pg)}\n          <ul class="drop">{sub}\n          </ul></li>')
            else:
                items.append(f'<li>{link(pg)}</li>')
    items.append(f'<li><a class="nav-cta" href="{_href(CTA[1],p)}">{CTA[0]}</a></li>')
    lis='\n        '.join(items)
    return f'''  <header class="site-header">
    <nav class="nav">
      <a class="brand" href="{p}index.html"><img class="brand-logo" src="{p}assets/logo.png?v=1" alt="The Mehta Endowment seal" width="70" height="60"><span class="brand-name">{S['brand']}</span></a>
      <button class="nav-toggle" aria-label="Menu">&#9776;</button>
      <ul class="nav-links">
        {lis}
      </ul>
    </nav>
  </header>'''

def footer(p=''):
    ex=[f'<li><a href="{p}{pg["slug"]}.html">{pg["label"]}</a></li>' for pg in site_pages() if pg.get('foot') and pg.get('label')]
    rows='\n          '.join(''.join(ex[i:i+2]) for i in range(0,len(ex),2))
    return f'''  <footer class="site-footer">
    <div class="wrap">
      <div class="footer-grid">
        <div><img class="footer-logo" src="{p}assets/logo.png?v=1" alt="The Mehta Endowment" width="118" height="101"><span class="brand-name">{S['name']}</span>
          <p style="margin-top:14px;max-width:38ch">{S['blurb']}</p></div>
        <div><h4>Explore</h4><ul class="footer-links">
          {rows}</ul></div>
        <div><h4>Get in touch</h4><ul class="footer-links">
          <li><a href="mailto:MehtaScholars@harker.org">MehtaScholars@harker.org</a></li>
          <li style="color:var(--muted)">500 Saratoga Ave,<br>San Jose, CA 95129</li></ul></div>
      </div>
      <div class="footer-bottom"><span>&copy; 2026 The {S['name']}</span><span>The Harker School</span></div>
    </div>
  </footer>
  <script src="{p}js/main.js?v=25"></script>
</body>
</html>'''

def head(title, desc, p=''):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}">
  {FONTS}
  <link rel="icon" type="image/png" href="{p}assets/favicon.png?v=1">
  <link rel="apple-touch-icon" href="{p}assets/favicon.png?v=1">
  <link rel="stylesheet" href="{p}css/styles.css?v=40">
</head>
<body>
'''

# The same person is written differently on different pages - "Alexis Gauba" on her
# founder page, "Alexis Gauba '17" on the committee list - and photo_map is keyed by
# the exact string. That let one person end up with two different headshots. This
# index resolves any spelling that differs only by a trailing class year, so a single
# photo_map entry now covers every page that person appears on.
def _photo_key(name):
    n=re.sub(r"[\u2018\u2019']\s*\d{2,4}\s*$", '', name or '').strip()
    return re.sub(r'[^a-z]', '', n.lower())
PHOTOS_BY_PERSON={}
for _k, _v in PHOTOS.items():
    PHOTOS_BY_PERSON.setdefault(_photo_key(_k), _v)

def inner_photo(name, p=''):
    """Return <img> if a real photo exists, else initials text."""
    ph=PHOTOS.get(name) or PHOTOS_BY_PERSON.get(_photo_key(name))
    if ph: return f'<img src="{p}{ph}" alt="{esc(name)}" loading="lazy">'
    return initials(name)

def avatar(name, cls='avatar', p=''):
    return f'<div class="{cls}">{inner_photo(name, p)}</div>'

def sec_hero(h1, sub='', cls=''):
    """The .page-hero band, shared by every inner page. `h1`/`sub` are authored
    copy containing entities like &amp; - they are NOT run through esc()."""
    c=f' {cls}' if cls else ''
    s=f'<p>{sub}</p>' if sub else ''
    return f'\n  <section class="page-hero{c}"><div class="wrap"><h1>{h1}</h1>{s}</div></section>'

# ============ SECTION BUILDERS ============
# Each returns a complete HTML fragment and knows nothing about which page it
# lands on - that is the registry's job. Moving the process flow or the team
# grid to another page is a one-line edit in PAGES, not a rewrite.

def sec_home_intro():
    return '''
  <section class="intro-stage" id="introStage" data-frames="80" data-video-end="0.45">
    <div class="intro-pin">
      <canvas id="introCanvas" class="intro-canvas" width="1920" height="1080"></canvas>
      <div class="wall-screen">
        <div class="ws-power" aria-hidden="true"></div>
        <div class="ws-slide is-active" data-i="0">
          <div class="ws-head"><p class="eyebrow">What We Do</p><h2>A launchpad for founders and investors</h2></div>
          <div class="ws-cards">
            <div class="ws-card" data-c="0"><div class="ico"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="2.5"/><circle cx="4.5" cy="6" r="2"/><circle cx="19.5" cy="6" r="2"/><circle cx="12" cy="20.5" r="2"/><path d="M6.2 7.1l3.8 3.1M17.8 7.1 14 10.2M12 14.5v4"/></svg></div><div><p class="kicker"><span class="ws-num">01</span>Connect</p><h3>Bring the Harker community together</h3><p>Entrepreneurs, investors, and business, technology &amp; research professionals in one network.</p><p class="ws-chips"><span>Entrepreneurs</span><span>Investors</span><span>Business</span><span>Technology</span><span>Research</span></p></div></div>
            <div class="ws-card" data-c="1"><div class="ico"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/></svg></div><div><p class="kicker"><span class="ws-num">02</span>Support</p><h3>Help alumni companies grow</h3><p>Support with customer &amp; talent acquisition, strategic partnerships, and venture funding.</p><p class="ws-chips"><span>Customers</span><span>Talent</span><span>Partnerships</span><span>Funding</span></p></div></div>
            <div class="ws-card" data-c="2"><div class="ico"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11v5c0 1.5 2.7 3 6 3s6-1.5 6-3v-5"/><path d="M22 9v6"/></svg></div><div><p class="kicker"><span class="ws-num">03</span>Educate</p><h3>Real-world experience for students</h3><p>Real-world, hands-on experiences for our students.</p><p class="ws-chips"><span>Research</span><span>Founder meetings</span><span>Investing</span></p></div></div>
          </div>
        </div>
        <div class="ws-slide" data-i="1"><div class="ws-inner">
          <p class="eyebrow">Join Our Network</p>
          <h2>Explore collaboration, mentorship &amp; investment</h2>
          <p>Connect with a diverse network of entrepreneurs, industry experts, and investors to explore collaborations, mentorship, and investment opportunities.</p>
          '''+join_buttons()+'''
          <p class="ws-note">Join the Harker Venture Investment Initiative Strategic Ecosystem, a private group on LinkedIn.</p>
        </div></div>
      </div>
      <div class="wall-dots"><span class="wall-dot is-on"></span><span class="wall-dot"></span></div>
      <div class="intro-overlay">
        <div class="wrap">
          <div class="hero-box">
            <h1>The Harker Venture Investment Initiative</h1>
            <div class="hero-links">
              <a href="alumni-companies.html"><span>Explore the companies founded by Harker alumni</span><i aria-hidden="true">&rarr;</i></a>
              <a href="strategic-ecosystem.html"><span>Learn more about our Strategic Ecosystem</span><i aria-hidden="true">&rarr;</i></a>
            </div>
          </div>
        </div>
      </div>
      <div class="intro-cue" aria-hidden="true">Scroll to step inside</div>
    </div>
  </section>
'''

# --- mehtascholars.com home. Copy is drawn from the About text and the process
# chart, so it states nothing those pages don't already say. ---
_ICO_SEARCH='<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>'
_ICO_TREND='<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/></svg>'
_ICO_NET='<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="2.5"/><circle cx="4.5" cy="6" r="2"/><circle cx="19.5" cy="6" r="2"/><circle cx="12" cy="20.5" r="2"/><path d="M6.2 7.1l3.8 3.1M17.8 7.1 14 10.2M12 14.5v4"/></svg>'

def sec_ms_home():
    n_sch=sum(len(ppl) for _,ppl in TEAM)
    def card(ico, kicker, h, p, href=None):
        tag='a' if href else 'div'; at=f' href="{href}"' if href else ''
        return f'<{tag} class="card"{at}><div class="ico">{ico}</div><p class="kicker">{kicker}</p><h3>{h}</h3><p>{p}</p></{tag}>'
    what=''.join([
      card(_ICO_SEARCH,'01 &middot; Research','Find and study alumni founders','Scholars identify Harker alumni founders, meet with them, and write preliminary and in-depth reports on their companies.'),
      card(_ICO_TREND,'02 &middot; Invest','Decide with the committees','Reports are refined with the Venture Advisory Committee, and the Venture Investment Committee decides whether to invest from The Harker Venture Pool.'),
      card(_ICO_NET,'03 &middot; Support','Connect founders to help','Scholars promote alumni founders and connect them with VCs, angel investors, entrepreneurs, and business and technology professionals.')])
    explore=''.join([
      card(_ICO_NET,'About',f'Meet the {n_sch} scholars','Who the Mehta Scholars are, how they are selected, and the process from profile to investment.','about.html'),
      card(_ICO_SEARCH,'Committee List',f'{len(committee)} advisors and investors','The Venture Investment, Venture Advisory, and Entrepreneurship Advisory Committees.','committee-list.html'),
      card(_ICO_TREND,'Our Investments',f'{len(INV)} alumni companies backed','The Harker alumni startups the Mehta Scholars have invested in.','our-investments.html')])
    return f'''
  <section class="hero"><div class="hero-bg" style="background-image:linear-gradient(120deg, rgba(7,40,20,0.55), rgba(7,40,20,0.2)),url(assets/hero-patil.jpg);background-size:cover;background-position:center"></div>
    <div class="wrap"><div class="hero-box">
      <h1>The Mehta Scholars</h1>
      <p>Harker students who research, support, and invest in companies founded by Harker alumni.</p>
      <div class="hero-cta"><a class="btn" href="about.html">Meet the team</a><a class="btn ghost" href="our-investments.html">Our investments</a></div>
    </div></div>
  </section>
  <section><div class="wrap">
    <div class="section-head"><p class="eyebrow">What we do</p><h2>Student analysts for The Harker Venture Pool</h2>
      <p>Top Business &amp; Entrepreneurship students are selected as Mehta Scholars for their 12th-grade year.</p></div>
    <div class="grid grid-3">{what}</div>
  </div></section>
  <section class="section-tint"><div class="wrap">
    <div class="section-head"><p class="eyebrow">Explore</p><h2>The program</h2></div>
    <div class="grid grid-3">{explore}</div>
  </div></section>
  <section class="section-green cta-band"><div class="wrap">
    <h2>Get in touch</h2>
    <p>Founders, alumni, and partners can reach the Mehta Scholars by email.</p>
    <a class="btn" href="mailto:MehtaScholars@harker.org">MehtaScholars@harker.org</a>
  </div></section>
'''

# --- Our Process: animated, scroll-built flowchart (loop + split/merge) ---
_ICO_DIAMOND='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M12 3l9 9-9 9-9-9z"/></svg>'
_ICO_CHECK='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>'
_ICO_BRANCH='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 4v6a3 3 0 0 0 3 3h8"/><path d="M15 9l4 4-4 4"/></svg>'
_ICO_FLAG='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 22V4"/><path d="M5 4h12l-2.2 4L17 12H5"/></svg>'
_ICO_LOOP='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9a6 6 0 0 1 10-4l3 3"/><path d="M16 3v5h-5"/><path d="M21 15a6 6 0 0 1-10 4l-3-3"/><path d="M8 21v-5h5"/></svg>'
def _vseg():
    return '<div class="pf-seg vert"><i></i></div>'
def _step(medal_cls, medal_inner, box_cls, inner, extra=''):
    return f'<div class="pf-step {extra}"><span class="pf-medal {medal_cls}">{medal_inner}</span><div class="pf-box {box_cls}">{inner}</div></div>'
# the refinement loop that hangs off the Advisory-review step
_LOOP=(f'<div class="pf-loop" aria-hidden="true"><span class="pf-loopwire"><i></i><span class="pf-3x">3&times;</span></span>'
       f'<div class="pf-loopnode"><span class="pf-medal loop">{_ICO_LOOP}</span><div class="pf-loopcard"><strong>Report refined</strong><span>&amp; presented again</span></div></div></div>')
_review=(f'<div class="pf-step has-loop" id="pfReview"><span class="pf-medal num">5</span>'
         f'<div class="pf-box"><h4>Advisory Committee review</h4><p>The report is presented to member(s) of the Venture Advisory Committee for feedback.</p>'
         f'<span class="proc-badge pf-loopfb">Refined &amp; re-presented ~3&times;</span>{_LOOP}</div>'
         f'</div>')

def _proc(stop_at='full'):
    """Build the flowchart.

    stop_at='full'      the original chart: decision -> Result 1 / Result 2 ->
                        $25K / $10K / no-investment terminals -> merge -> close.
    stop_at='decision'  stops at "Investment Committee decides" and runs straight
                        into the closing node. Removes the two-option/pricing
                        presentation. The branch stays in code, so it is
                        recoverable - do not delete it.
    """
    _parts=[]
    _parts.append(_step('num','1','','<h4>Profile created</h4><p>A promotional profile is created and the founder &amp; company are added to the website.</p>'))
    _parts.append(_vseg())
    _parts.append(_step('num','2','','<h4>Preliminary report</h4><p>A preliminary report is put together on the company.</p>'))
    _parts.append(_vseg())
    _parts.append(_step('num','3','','<h4>Founder meeting</h4><p>A Mehta Scholar meets with the founder to discuss the company.</p>'))
    _parts.append(_vseg())
    _parts.append(_step('num','4','','<h4>In-depth report</h4><p>A full, in-depth report on the company is written.</p>'))
    _parts.append(_vseg())
    _parts.append(_review)
    _parts.append(_vseg())
    _parts.append(_step('num','6','','<h4>Report approved</h4><p>Once refined, the polished report is approved.</p>'))
    _parts.append(_vseg())
    _parts.append(_step('dec',_ICO_DIAMOND,'dec','<h4>Investment Committee decides</h4><p>The Venture Investment Committee reviews the finalized report and decides whether to invest.</p>'))
    if stop_at=='full':
        # split: decision -> Result 1 / Result 2
        _parts.append('<div class="pf-split" id="pfSplit"><span class="pf-seg vert stem"><i></i></span><span class="pf-seg horiz barL"><i></i></span><span class="pf-seg horiz barR"><i></i></span><span class="pf-seg vert downL"><i></i></span><span class="pf-seg vert downR"><i></i></span></div>')
        # tier 1 : Result 1 (left) | Result 2 (spans right two columns)
        _r1=f'<div class="pf-step res r1"><span class="pf-medal ok">{_ICO_CHECK}</span><div class="pf-box"><span class="proc-tag ok">Result 1 &middot; Approved</span><p>The committee approves the investment.</p></div></div>'
        _r2=f'<div class="pf-step res r2"><span class="pf-medal no">{_ICO_BRANCH}</span><div class="pf-box"><span class="proc-tag no">Result 2 &middot; Not approved</span><p>The committee does not approve the investment &mdash; what happens next depends on the scholars&rsquo; conviction.</p></div></div>'
        _parts.append(f'<div class="pf-tier1" id="pfTier1">{_r1}{_r2}</div>')
        # sub : Result 1 continues straight down; Result 2 forks into two
        _parts.append('<div class="pf-sub" id="pfSub"><span class="pf-seg vert r1down"><i></i></span><span class="pf-seg vert r2stem"><i></i></span><span class="pf-seg horiz subbarL"><i></i></span><span class="pf-seg horiz subbarR"><i></i></span><span class="pf-seg vert subdownL"><i></i></span><span class="pf-seg vert subdownR"><i></i></span></div>')
        # tier 2 : three terminal outcomes
        _t1='<div class="pf-step term"><div class="pf-box term fund"><strong>$25K SAFE</strong><span>toward the next round</span></div></div>'
        _t2='<div class="pf-step term"><div class="pf-box term fund"><strong>$10K SAFE</strong><span>scholars still believe strongly</span></div></div>'
        _t3='<div class="pf-step term"><div class="pf-box term none"><strong>No investment</strong><span>the round is passed on</span></div></div>'
        _parts.append(f'<div class="pf-tier2" id="pfTier2">{_t1}{_t2}{_t3}</div>')
        # merge : all three outcomes -> final
        _parts.append('<div class="pf-merge3" id="pfMerge3"><span class="pf-seg vert up1"><i></i></span><span class="pf-seg vert up2"><i></i></span><span class="pf-seg vert up3"><i></i></span><span class="pf-seg horiz m3barL"><i></i></span><span class="pf-seg horiz m3barR"><i></i></span><span class="pf-seg vert m3stem"><i></i></span></div>')
        _parts.append(_step('fin',_ICO_FLAG,'final','<h4>Founder works with the committee</h4><p>In every case, the founder works with committee members &mdash; especially the Entrepreneurship Advisory Committee.</p>'))
    else:
        _parts.append(_vseg())
        _parts.append(_step('fin',_ICO_FLAG,'final',PROC_CLOSE))
    return f'''<div class="process" id="procDiagram">
      <div class="pf">{''.join(_parts)}</div>
    </div>'''

# The note the whole process now ends on. Whatever the committee decides, the
# founder gets access to the ecosystem and the advisors.
PROC_CLOSE=('<h4>Access to the Harker Strategic Ecosystem</h4>'
            '<p>Whatever the committee decides, the founder gains access to the Harker Strategic Ecosystem '
            '&mdash; our alumni VCs, angel investors and operators &mdash; and to the Entrepreneurship '
            'Advisory Committee, who work with founders to develop and solidify their companies.</p>')

PROC_STOP='decision'

def sec_process():
    return ('\n  <section class="section-tint"><div class="wrap"><div class="section-head">'
            '<p class="eyebrow">Our Process</p><h2>From profile to investment</h2></div>\n    '
            + _proc(PROC_STOP) + '</div></section>')

ABOUT_P1='Mehta Scholars serve as analysts for The Harker Venture Pool. This real-world, hands-on experience provides a unique opportunity to our advanced-level Business &amp; Entrepreneurship students who take Honors Corporate Finance &amp; Honors Venture Capital in their 11th-grade year. Top performers are then selected to be Mehta Scholars during their 12th-grade year.'
ABOUT_P2='Mehta Scholars identify, research, promote, and support alumni founders and their companies as they look to invest in their companies from the Harker Venture Pool. They also connect alumni founders with other VCs, Angel Investors, Entrepreneurs, and other Business and Technology Professionals in the Harker Strategic Ecosystem as needed.'

def sec_about_prose():
    return ('\n  <section><div class="wrap" style="max-width:900px">'
            f'\n    <p style="font-size:1.15rem">{ABOUT_P1}</p>'
            f'\n    <p style="font-size:1.15rem">{ABOUT_P2}</p>'
            '\n  </div></section>')

# The scholar roster lives in captured/scholars.json so it can be updated without
# touching the generator. Falls back to nothing rather than crashing the build.
try: TEAM=[(c['class'],c['names']) for c in json.load(open(CAP+'scholars.json'))]
except Exception: TEAM=[]
try: SCHOLAR_LI=json.load(open(CAP+'scholar_linkedin.json'))
except Exception: SCHOLAR_LI={}

def sec_team():
    teamhtml=''
    for cls,ppl in TEAM:
        teamhtml+=f'<div class="class-block"><h3>{cls}</h3><div class="people">'
        for n in ppl:
            av=avatar(n); li=SCHOLAR_LI.get(n)
            if li: av=f'<a href="{li}" target="_blank" rel="noopener" class="scholar-link" aria-label="{esc(n)} on LinkedIn">{av}</a>'
            teamhtml+=f'<div class="person">{av}<div class="name">{n}</div></div>'
        teamhtml+='</div></div>'
    return ('\n  <section><div class="wrap"><div class="section-head"><p class="eyebrow">Our Team</p>'
            f'<h2>Meet the scholars</h2></div>{teamhtml}</div></section>\n')

# ============ ALUMNI COMPANIES ============
STAGE_ORDER=["Acquired / IPO'd",'Pre-Seed','Seed','Series A and Later','Bootstrapped']
_bad=sorted({f.get('stage_group') for f in companies}-set(STAGE_ORDER))
if _bad: raise SystemExit(f'Unknown stage_group {_bad}: add it to STAGE_ORDER or fix companies.json. Unlisted stages drop the company from Alumni Companies.')
SECTORS=[('all','All'),('ai','AI'),('health','Health &amp; Bio'),('fintech','Fintech'),('security','Security'),
 ('enterprise','Enterprise/SaaS'),('commerce','Commerce/Consumer'),('energy','Energy/Climate'),('media','Media/Gaming'),('hardware','Hardware/Deep-Tech')]

def sec_alumni_grid():
    out='\n  <section class="co-section"><div class="wrap">\n    <div class="filters">'
    out+=''.join(f'<button class="filter-btn{" active" if k=="all" else ""}" data-filter="{k}" id="{k}">{lbl}</button>' for k,lbl in SECTORS)
    out+='</div>'
    for stage in STAGE_ORDER:
        grp=[f for f in companies if f.get('stage_group')==stage]
        if not grp: continue
        out+=f'<div data-stage-group><h2 class="stage-label">{esc(stage)}</h2><div class="co-grid">'
        for f in grp:
            if f.get('tile'):
                thumb=f'<div class="co-thumb"><img src="{f["tile"]}?v=13" alt="{esc(f["company"])}" loading="lazy"></div>'
            else:
                thumb=f'<div class="co-thumb ph" style="--tc:{f.get("color","#2f6d3a")}"><span>{esc(f["company"])}</span></div>'
            out+=f'<a class="co-tile" data-sector="{f["sector_key"]}" href="companies/{f["page"]}.html">{thumb}<div class="co-name">{esc(f["name"])} {esc(f.get("year",""))}</div></a>'
        out+='</div></div>'
    return out+'</div></section>'

# ============ OUR INVESTMENTS ============
# Each entry is (founder, class year, company, category tag, description, page).
# `page` is the record's page slug from companies.json - NOT slug(company_name).
# Founders with more than one company are paged under their own name, so deriving
# the href from the display name produced a 404 for Kos.ai.
INV=[('Namrata Anand','\'10','Diffuse Bio','Health Tech & Life Sciences','Diffuse Bio is a biotechnology company specializing in generative AI for protein design. Their mission is to create AI systems that engineer novel, useful proteins with exceptional precision.','diffuse-bio'),
('Barrett Glasauer','\'09','Rejigg','Fintech','Rejigg connects quality small business owners with vetted buyers, minimizing fees, eliminating brokers, and streamlining the acquisition process.','rejigg'),
('Surbhi Sarna','\'03','Collate','Health Tech & Life Sciences','Collate uses AI to create and streamline accurate documentation for diagnostic, medical device, and drug development companies, thereby reducing time to market and expediting the creation of life-saving innovations.','collate'),
('Aumesh Misra','\'16','Tivara','Health Tech & Life Sciences','Tivara is an AI company that automates insurance approval (prior authorization) for healthcare clinics, helping doctors deliver care to patients faster.','tivara'),
('Anita Modi','\'04','Peer AI','Health Tech & Life Sciences','Peer AI is an agentic AI platform that provides support for regulatory documentation for life sciences and biotech companies with strong security and compliance.','peer-ai'),
('Drew Goldstein','\'13','Ephemeral Technologies','Health Tech & Life Sciences','Ephemeral Technologies works to accelerate end-to-end drug development and delivery using an integrated AI, software, and robotics platform.','ephemeral-technologies'),
('Tanuj Thapliyal','\'06','Kos.ai','Fintech','Kos.ai is a virtual finance employee that autonomously completes critical financial workflows - invoice reviews, purchase orders and custom finance processes - for capital-intensive industries such as datacenters, defense, energy and construction.','tanuj-thapliyal'),
('Ravi Mishra','\'04','Ample','AI and Smart Tech','Ample is building cloud infrastructure that deploys a full application from a single prompt to a coding agent, handling hosting, configuration and scaling behind the scenes. It folds existing infrastructure products into one assembled system, taking an app live in around 30 seconds.','ample'),
('Rajiv Sancheti','\'16','Caddy','AI and Smart Tech','Caddy is a personal AI for everyday work that lives in your text messages. It surfaces what matters from your email, calendar and apps, and acts on it when you reply.','caddy')]

def _co_website(page, co):
    """The company's own site, for the Our Investments button. Founder pages now
    live on harkervii.com, and the two sites don't link to each other."""
    recs=[c for c in companies if c['page']==page]
    rec=next((c for c in recs if c['company']==co), recs[0] if recs else {})
    return rec.get('website','')

def sec_investments():
    out='\n  <section><div class="wrap"><div class="invest">'
    for nm,yr,co,tag,desc,page in INV:
        sl=slug(co); web=_co_website(page, co)
        more=f'<a class="btn small" href="{web}" target="_blank" rel="noopener">Visit {esc(co)} &#8599;</a>' if web else ''
        logo=f'<div class="invest-logo"><img src="assets/invest-logos/{sl}.png?v=2" alt="{esc(co)} logo" loading="lazy"></div>' if os.path.exists(f'{ROOT}/assets/invest-logos/{sl}.png') else ''
        out+=f'''<div class="invest-card">
      <div class="invest-top">
        <div class="invest-co-block">{logo}<div class="co">{esc(co)}</div></div>
        <div class="invest-founder">{esc(nm)}{(" " + esc(yr)) if yr else ""}</div>
      </div>
      <div class="invest-body">
        <div class="invest-headshot">{inner_photo(nm)}</div>
        <span class="tag">{esc(tag)}</span>
        <p>{esc(desc)}</p>
        {more}
      </div></div>'''
    return out+'</div></div></section>'

# ============ COMMITTEE ============
ORDER=['Venture Investment Committee','Venture Advisory Committee','Entrepreneurship Advisory Committee']
def linklabel(u): return 'Instagram' if 'instagram.com' in (u or '') else 'LinkedIn'

def sec_committee(groups=None):
    """Rosters + the profile modal. cdata/idx are LOCAL to this call: if the
    rosters are ever split across two pages, page-global indices would make every
    tile on the second page open the wrong person's modal, silently."""
    groups=groups or ORDER
    out=''; cdata=[]; idx=0; tint=False
    for grp in groups:
        mem=[m for m in committee if m['committee']==grp]
        if not mem: continue
        seccls=' section-tint' if tint else ''; tint=not tint
        out+=f'<section class="{seccls.strip()}"><div class="wrap"><div class="section-head"><p class="eyebrow">{grp}</p></div><p class="committee-intro">{esc(sections.get(grp,""))}</p><div class="members-grid">'
        for m in mem:
            cdata.append({'name':m['name'],'org':m['org'],'bio':m.get('bio',''),
              'linkedin':m.get('linkedin',''),'linklabel':linklabel(m.get('linkedin','')),
              'company':m.get('company_url',''),'photo':PHOTOS.get(m['name'],''),'initials':initials(m['name'])})
            out+=f'''<button class="member-tile" data-idx="{idx}"><div class="photo">{inner_photo(m['name'])}</div><div class="m-head"><h3>{esc(m['name'])}</h3><div class="org">{esc(m['org'])}</div><p class="tile-bio">{esc(m.get('bio',''))}</p></div><span class="tile-more">View profile &rarr;</span></button>'''
            idx+=1
        out+='</div></div></section>'
    out+='''
  <div class="modal-overlay" id="memberModal" hidden>
    <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="mName">
      <button class="modal-close" aria-label="Close">&times;</button>
      <div class="modal-photo" id="mPhoto"></div>
      <div class="modal-info">
        <h3 id="mName"></h3>
        <div class="org" id="mOrg"></div>
        <p id="mBio"></p>
        <div class="modal-links" id="mLinks"></div>
      </div>
    </div>
  </div>
  <script>
  window.COMMITTEE=''' + json.dumps(cdata) + ''';
  (function(){
    var modal=document.getElementById('memberModal');
    var mPhoto=document.getElementById('mPhoto'),mName=document.getElementById('mName'),mOrg=document.getElementById('mOrg'),mBio=document.getElementById('mBio'),mLinks=document.getElementById('mLinks');
    function openModal(i){var d=window.COMMITTEE[i];if(!d)return;
      mPhoto.innerHTML=d.photo?'<img src="'+d.photo+'" alt="'+d.name+'">':d.initials;
      mName.textContent=d.name;mOrg.textContent=d.org;mBio.textContent=d.bio||'';
      var l='';
      if(d.linkedin)l+='<a class="btn outline" target="_blank" rel="noopener" href="'+d.linkedin+'">'+d.linklabel+' \\u2197</a>';
      if(d.company)l+='<a class="btn outline" target="_blank" rel="noopener" href="'+d.company+'">Company \\u2197</a>';
      mLinks.innerHTML=l;modal.hidden=false;document.body.style.overflow='hidden';}
    function closeModal(){modal.hidden=true;document.body.style.overflow='';}
    document.addEventListener('click',function(e){
      var t=e.target.closest('.member-tile');
      if(t){openModal(+t.getAttribute('data-idx'));return;}
      if(e.target===modal||e.target.classList.contains('modal-close'))closeModal();
    });
    document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!modal.hidden)closeModal();});
  })();
  </script>'''
    return out

# ============ UPDATES ============
# Posts live in captured/updates.json, each tagged with the site(s) it belongs to.
POSTS=json.load(open(CAP+'updates.json'))['posts']

def sec_updates():
    mine=[x for x in POSTS if S['key'] in x.get('sites',[])]
    if not mine:
        return f'''
  <section><div class="wrap"><div class="section-head"><p class="eyebrow">Coming soon</p><h2>News from the initiative</h2>
    <p>Updates from across the Harker Strategic Ecosystem will appear here. In the meantime, join the conversation on LinkedIn.</p></div>
    {join_buttons('center')}
  </div></section>'''
    arts=''.join(f'''
    <article class="post"><div class="post-cover"><h2>{esc(x['title'])}</h2></div>
      <div class="post-body"><div class="post-meta">{''.join(f'<span>{esc(x[k])}</span>' for k in ('author','date','read') if x.get(k))}</div>
      <p>{esc(x['body'])}</p></div></article>''' for x in mine)
    return f'\n  <section><div class="wrap"><div class="posts">{arts}\n  </div></div></section>'

# ============ STRATEGIC ECOSYSTEM ============
# The map is one SVG on a 640x600 board: a hub, an orbit track, and three
# community nodes. The two green arcs are the cascade from the team's slide
# (Parents -> Alumni -> Students). main.js draws them as the map scrolls in;
# without JS (or with reduced motion) everything is simply shown.
_ECO_NODES=[  # (id, cx, cy, lines)
 ('par', 320, 100, ['Parents &amp;','Parents of','Alumni']),
 ('alu', 493.2, 400, ['Alumni']),
 ('stu', 146.8, 400, ['Business &amp;','Entrepreneurship','Students']),
]
def _eco_node(nid, cx, cy, lines):
    lh=22; y0=cy-(len(lines)-1)*lh/2
    t=''.join(f'<tspan x="{cx}" y="{y0+i*lh:.1f}">{l}</tspan>' for i,l in enumerate(lines))
    return (f'<g class="eco-node" data-k="{nid}"><circle class="eco-halo" cx="{cx}" cy="{cy}" r="94"/>'
            f'<circle class="eco-dot" cx="{cx}" cy="{cy}" r="82"/><text class="eco-label" text-anchor="middle" dominant-baseline="central">{t}</text></g>')

def sec_eco_map():
    nodes=''.join(_eco_node(*n) for n in _ECO_NODES)
    svg=f'''<svg class="eco-svg" viewBox="48 2 544 588" role="img" aria-labelledby="ecoT ecoD">
        <title id="ecoT">The Harker Strategic Ecosystem</title>
        <desc id="ecoD">Three connected groups around the ecosystem: parents and parents of alumni, alumni, and Business and Entrepreneurship students. Arrows run from parents to alumni, and from alumni to students.</desc>
        <defs><linearGradient id="ecoG" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#038112"/><stop offset="1" stop-color="#073d1e"/></linearGradient></defs>
        <circle class="eco-track" cx="320" cy="300" r="200"/>
        <g class="eco-hub"><circle class="eco-pulse" cx="320" cy="300" r="88"/><circle cx="320" cy="300" r="88" fill="url(#ecoG)"/>
          <text class="eco-hubtext" text-anchor="middle"><tspan x="320" y="276">Harker</tspan><tspan x="320" y="304">Strategic</tspan><tspan x="320" y="332">Ecosystem</tspan></text></g>
        <path class="eco-arc" data-k="a1" pathLength="1" d="M412.3,122.6 A200,200 0 0 1 519.8,308.7"/>
        <polygon class="eco-head" data-k="a1" points="0,0 -16,-9 -16,9" transform="translate(519.8,308.7) rotate(92.5)"/>
        <path class="eco-arc" data-k="a2" pathLength="1" d="M427.5,468.7 A200,200 0 0 1 212.5,468.7"/>
        <polygon class="eco-head" data-k="a2" points="0,0 -16,-9 -16,9" transform="translate(212.5,468.7) rotate(212.5)"/>
        {nodes}
      </svg>'''
    return f'''
  <section><div class="wrap eco-map-wrap">
    <div class="eco-map" id="ecoMap">{svg}</div>
    <div class="eco-side">
      <p class="eyebrow">One connected network</p>
      <h2>Every part of the Harker community, in one place</h2>
      <p>The Strategic Ecosystem links the Harker community across generations. Parents and parents of alumni, alumni, and today&rsquo;s Business &amp; Entrepreneurship students each bring something to the people coming up behind them.</p>
      <ul class="eco-roles">
        <li><span class="eco-ico">{_ECO_ICO['ent']}</span>Entrepreneurs</li>
        <li><span class="eco-ico">{_ECO_ICO['inv']}</span>Investors</li>
        <li><span class="eco-ico">{_ECO_ICO['pro']}</span>Business &amp; Technology Professionals</li>
      </ul>
    </div>
  </div></section>'''

_ECO_ICO={
 'ent':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 15c-1.5 1.3-2 5-2 5s3.7-.5 5-2c.7-.8.7-2.1-.1-2.9a2.1 2.1 0 0 0-2.9-.1z"/><path d="M12 15l-3-3a22 22 0 0 1 2-3.9A12.9 12.9 0 0 1 22 2c0 2.7-.8 7.5-6 11a22.4 22.4 0 0 1-4 2z"/><path d="M9 12H4s.6-3 2-4c1.6-1.1 5 0 5 0M12 15v5s3-.6 4-2c1.1-1.6 0-5 0-5"/></svg>',
 'inv':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/></svg>',
 'pro':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 13h18"/></svg>',
 'stu':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11v5c0 1.5 2.7 3 6 3s6-1.5 6-3v-5"/></svg>',
 'alu':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-7 8-7s8 3 8 7"/></svg>',
 'par':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="7" r="3.5"/><path d="M2 21c0-3.6 3.1-6.5 7-6.5s7 2.9 7 6.5"/><circle cx="17.5" cy="9" r="2.5"/><path d="M17 14.6c2.9.3 5 2.5 5 5.4"/></svg>',
 'exp':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6M10 22h4"/><path d="M12 2a7 7 0 0 0-4 12.7c.6.5 1 1.3 1 2.1V17h6v-.2c0-.8.4-1.6 1-2.1A7 7 0 0 0 12 2z"/></svg>',
 'exx':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="6"/><path d="M8.2 12.7 7 22l5-3 5 3-1.2-9.3"/></svg>',
 'sup':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21.2l8.8-8.8a5.5 5.5 0 0 0 0-7.8z"/></svg>',
 'ene':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2 3 14h9l-1 8 10-12h-9z"/></svg>',
}

def _eco_col(n, title, items):
    lis=''.join(f'<li><span class="eco-ico">{_ECO_ICO[k]}</span>{lbl}</li>' for k,lbl in items)
    return f'<div class="eco-col"><p class="eco-step">{n}</p><h3>{title}</h3><ul>{lis}</ul></div>'

def sec_eco_members():
    who=_eco_col('01','Who is in it',[('stu','Students'),('alu','Alumni'),('par','Parents'),('par','Parents of Alumni')])
    are=_eco_col('02','Who are',[('ent','Entrepreneurs'),('inv','Investors'),('pro','Business professionals'),('pro','Technology professionals')])
    lev=_eco_col('03','Able to leverage',[('exp','Expertise'),('exx','Experience'),('sup','Support'),('ene','Energy')])
    j='<span class="eco-join" aria-hidden="true">&rarr;</span>'
    return f'''
  <section class="section-tint"><div class="wrap">
    <div class="section-head"><p class="eyebrow">What it is</p><h2>Who makes up the ecosystem</h2></div>
    <div class="eco-cols">{who}{j}{are}{j}{lev}</div>
    <p class="eco-summary">The Harker Venture Investment Initiative Strategic Ecosystem consists of <strong>students, alumni, parents, and parents of alumni</strong> who are <strong>entrepreneurs, investors, and business &amp; technology professionals</strong>, and who are able to leverage the <strong>expertise, experience, support, and energy</strong> of this distinguished group.</p>
  </div></section>'''

def sec_eco_scholars():
    return f'''
  <section><div class="wrap"><div class="eco-note">
    <div>
      <p class="eyebrow">Where the Mehta Scholars fit</p>
      <h3>Students at the heart of the network</h3>
      <p>Mehta Scholars identify, research, promote, and support alumni founders and their companies. They also connect alumni founders with VCs, angel investors, entrepreneurs, and business and technology professionals across the Harker Strategic Ecosystem.</p>
    </div>
  </div></div></section>
  <section class="section-green eco-cta"><div class="wrap">
    <div class="section-head"><p class="eyebrow">Join our network</p><h2>Become part of the ecosystem</h2>
      <p>Join the Harker Venture Investment Initiative Strategic Ecosystem, a private group on LinkedIn.</p></div>
    {join_buttons('center')}
  </div></section>'''

# ============ THE REGISTRY ============
# `site` is 'ms' (mehtascholars.com) or 'vii' (harkervii.com). Both sites have an
# index and an updates page, so slugs are unique per site, not globally.
PAGES=[
 # ---- harkervii.com: the initiative and the ecosystem as a whole ----
 dict(site='vii', slug='index', key='home', label='Home', track='main', foot=True,
      title='Harker Venture Investment Initiative',
      desc='The Harker Venture Investment Initiative connects Harker students, alumni, parents, and parents of alumni who are entrepreneurs, investors, and business &amp; technology professionals.',
      hero=None, body=[sec_home_intro]),

 dict(site='vii', slug='strategic-ecosystem', key='ecosystem', label='Strategic Ecosystem', track='main', foot=True,
      title='Strategic Ecosystem | Harker Venture Investment Initiative',
      desc='The Harker Strategic Ecosystem: students, alumni, parents, and parents of alumni who are entrepreneurs, investors, and business &amp; technology professionals.',
      hero=('The Harker Strategic Ecosystem','Students, alumni, parents, and parents of alumni, working together as entrepreneurs, investors, and business &amp; technology professionals.','serif'),
      body=[sec_eco_map, sec_eco_members, sec_eco_scholars]),

 dict(site='vii', slug='alumni-companies', key='alumni', label='Alumni Companies', track='main', foot=True,
      title='Alumni Companies | Harker Venture Investment Initiative',
      desc='Companies founded by Harker alumni across AI, health &amp; bio, fintech, security, enterprise, commerce, energy, media, and deep tech.',
      drop=[('ai','AI'),('health','Health &amp; Bio'),('fintech','Fintech'),
            ('security','Security'),('enterprise','Enterprise'),('commerce','Commerce')],
      hero=('Harker fosters the best.','The companies founded by Harker alumni, across every sector and stage.','serif'),
      body=[sec_alumni_grid]),

 dict(site='vii', slug='updates', key='updates', label='Updates', track='main', foot=True,
      title='Updates | Harker Venture Investment Initiative',
      desc='News and updates from The Harker Venture Investment Initiative.',
      hero=('Updates','News, events, and announcements from across the Harker Strategic Ecosystem.'),
      body=[sec_updates]),

 # ---- mehtascholars.com: the Mehta Scholars program ----
 dict(site='ms', slug='index', key='home', label='Home', track='main', foot=True,
      title='Home | Mehta Scholars',
      desc='Mehta Scholars are Harker students who research, support, and invest in companies founded by Harker alumni.',
      hero=None, body=[sec_ms_home]),

 dict(site='ms', slug='about', key='about', label='About', track='main', foot=True,
      title='About | Mehta Scholars',
      desc='Meet the Mehta Scholar team and learn how our analysts research and invest in Harker alumni founders.',
      hero=('The Mehta Scholar Team','Student analysts for The Harker Venture Pool.'),
      body=[sec_about_prose, sec_process, sec_team]),

 dict(site='ms', slug='committee-list', key='committee', label='Committee List', track='main', foot=True,
      title='Committee List | Mehta Scholars',
      desc='The Venture Investment, Venture Advisory, and Entrepreneurship Advisory Committees supporting the Mehta Scholars.',
      hero=('Harker connects you with the best.','The committees of experienced investors and founders who guide, review, and support our work.','serif'),
      body=[sec_committee]),

 dict(site='ms', slug='our-investments', key='invest', label='Our Investments', track='main', foot=True,
      title='Our Investments | Mehta Scholars',
      desc="Harker's Mehta Scholars invest in Harker alumni startups. See a selection of our past investments.",
      hero=('Our Investments',"Harker's Mehta Scholars invest in Harker alumni startups. We review reports with the Venture Advisory Committee and the Venture Investment Committee, then decide together. Here are a few of our past investments."),
      body=[sec_investments]),

 dict(site='ms', slug='updates', key='updates', label='Updates', track='main', foot=True,
      title='Updates | Mehta Scholars',
      desc='News and updates from the Harker Mehta Scholars.',
      hero=('Updates','News, milestones, and announcements from the Mehta Scholars.'),
      body=[sec_updates]),
]
for _k,_v in SITES.items(): _v['key']=_k
_badsite={pg['site'] for pg in PAGES}-set(SITES)
if _badsite: raise SystemExit(f'Unknown site {_badsite} in PAGES')

def site_pages(): return [pg for pg in PAGES if pg['site']==S['key']]

# Where each page lives, so a link or redirect can be pointed at the right domain.
HOME_OF={pg['slug']+'.html':pg['site'] for pg in PAGES if pg['slug'] not in ('index','updates')}

def render(pg, p=''):
    doc=head(pg['title'], pg['desc'], p)
    doc+=nav(pg['key'], p)
    if pg.get('hero'): doc+=sec_hero(*pg['hero'])
    for s in pg['body']: doc+=s()
    doc+=footer(p)
    return doc

# ============ COMPANY / FOUNDER DETAIL PAGES (harkervii.com) ============
pages={}
for f in companies: pages.setdefault(f['page'],[]).append(f)
def fact(label,val): return f'<div class="fact"><span class="fact-l">{label}</span><span class="fact-v">{esc(val)}</span></div>' if val else ''
def write_company_pages(out):
    os.makedirs(out+'/companies',exist_ok=True)
    for pgslug,cos in pages.items():
        f0=cos[0]
        li=f0.get('linkedin',''); links=''
        if li: links+=f'<a class="btn outline" href="{li}" target="_blank" rel="noopener">Founder&#39;s LinkedIn &#8599;</a>'
        multi=len(cos)>1
        for c in cos:
            if c.get('website'):
                lbl=(f'{esc(c["company"])} website' if multi else 'Visit Website')
                links+=f'<a class="btn outline" href="{c["website"]}" target="_blank" rel="noopener">{lbl} &#8599;</a>'
        bio=f0.get('bio','') or 'Full profile coming soon — our Mehta Scholars are researching this founder and their companies.'
        conames=' &middot; '.join(c['company'] for c in cos)
        doc=head(f"{f0['name']} | {S['name']}", f"{f0['name']} — {', '.join(c['company'] for c in cos)}.", p='../')
        doc+=nav('alumni', p='../')
        doc+=f'''
  <section class="company-hero" style="--pg:{f0.get('color','#0a582a')}"><div class="wrap"><div class="company-card">
    <div class="photo">{inner_photo(f0['name'], '../')}</div>
    <div>
      <div class="founder-name">{esc(f0['name'])} {esc(f0.get('year',''))}</div>
      <div class="co-name">{conames}</div>
      <div class="bio">{esc(bio)}</div>
      {('<div class="company-links">'+links+'</div>') if links else ''}
    </div>
  </div></div></section>
'''
        doc+='  <section style="padding:40px 0"><div class="wrap" style="text-align:center"><a class="btn" href="../alumni-companies.html">&larr; Back to Alumni Companies</a></div></section>\n'
        doc+=footer(p='../')
        open(f'{out}/companies/{pgslug}.html','w').write(doc)

# ============ SITEMAP ============
# Generated from the registry so an IA change cannot leave it stale. It used to be
# hand-maintained inside public/ - the one directory contributors are told never to
# edit - and had drifted (it listed pages that no longer existed and missed two new ones).
def write_sitemap(out):
    u=S['url']
    locs=[u]+[u+pg['slug']+'.html' for pg in site_pages() if pg['slug']!='index']
    if S['key']=='vii': locs+=[u+'companies/'+s+'.html' for s in sorted(pages)]
    open(out+'/sitemap.xml','w',encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + ''.join(f'  <url><loc>{x}</loc></url>\n' for x in locs) + '</urlset>\n')
    return locs

# ============ REDIRECT STUBS ============
# GitHub Pages serves static files and nothing else - no _redirects, no rewrite rules -
# so every old URL needs a real file sitting at that path. A meta refresh plus a
# rel=canonical is the most a static host can do: it is not a 301, but search engines
# honour the canonical. Source of truth is captured/redirects.txt.
def redirect_stub(target):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url={target}">
  <meta name="robots" content="noindex">
  <link rel="canonical" href="{target}">
  <title>Redirecting&hellip;</title>
</head>
<body>
  <p>This page has moved. <a href="{target}">Continue to {target}</a>.</p>
</body>
</html>
"""

REDIRECTS=[]
for line in open(os.path.join(BASE,'captured','redirects.txt'), encoding='utf-8'):
    line=line.strip()
    if not line or line.startswith('#'): continue
    parts=line.split()
    if len(parts) >= 2: REDIRECTS.append((parts[0], parts[1]))

def site_of(target):
    """Which site serves a path like '/companies/x.html' or '/alumni-companies.html#ai'."""
    path=target.split('#')[0].lstrip('/')
    return 'vii' if path.startswith('companies/') else HOME_OF.get(path,'ms')

def write_redirects(out):
    stubs=[]; skipped=[]; written=set()
    def stub(old, target):
        dest=os.path.join(out, old) if old.endswith('.html') else os.path.join(out, old, 'index.html')
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest,'w',encoding='utf-8').write(redirect_stub(target))
        written.add(os.path.normpath(dest)); stubs.append(('/'+old, target))
    vii=SITES['vii']['url']
    if S['key']=='ms':
        # Pages that moved to harkervii.com keep working at their old addresses.
        for path,site in HOME_OF.items():
            if site=='vii': stub(path, vii+path)
        for s in pages: stub(f'companies/{s}.html', f'{vii}companies/{s}.html')
    for old,new in REDIRECTS:
        if '*' in old:
            skipped.append((old,'wildcard - needs a 404 page')); continue
        old=old.lstrip('/')
        if not old: continue
        # harkervii.com is a new domain with no old URLs, except renamed company pages.
        if S['key']=='vii' and not old.startswith('companies/'): continue
        if site_of(new)!=S['key']: new=SITES[site_of(new)]['url']+new.lstrip('/')
        # Pages already resolves /foo to foo.html, so an identity mapping needs no stub
        # (and a stub there would add a pointless extra hop).
        if new.lstrip('/') == old + '.html':
            skipped.append(('/'+old,'Pages resolves this already')); continue
        stub(old, new)
    if S['key']=='ms':
        # Any older company page still in public/ (from a past rename) goes to the roster.
        d=os.path.join(out,'companies')
        for fn in sorted(os.listdir(d)):
            if fn.endswith('.html') and os.path.normpath(os.path.join(d,fn)) not in written:
                stub(f'companies/{fn}', vii+'alumni-companies.html')
    return stubs, skipped

def sync_tree(src, dst, skip=()):
    """Mirror src into dst, copying only changed files, and delete what src no longer has."""
    seen=set()
    for dp,dns,fns in os.walk(src):
        dns[:]=[d for d in dns if d not in skip]
        rel=os.path.relpath(dp, src); os.makedirs(os.path.join(dst,rel), exist_ok=True)
        for fn in fns:
            if fn=='.DS_Store': continue
            s=os.path.join(dp,fn); d=os.path.normpath(os.path.join(dst,rel,fn)); seen.add(d)
            a=os.stat(s); b=os.stat(d) if os.path.exists(d) else None
            if not b or b.st_size!=a.st_size or int(b.st_mtime)!=int(a.st_mtime): shutil.copy2(s,d)
    for dp,dns,fns in os.walk(dst):
        for fn in fns:
            d=os.path.normpath(os.path.join(dp,fn))
            if d not in seen: os.remove(d)

# ============ BUILD BOTH SITES ============
for key in ('ms','vii'):
    S=SITES[key]; out=S['root']; os.makedirs(out, exist_ok=True)
    if key=='vii':
        # public-vii/ is pure output: wipe it, then mirror the shared hand-written files.
        for n in os.listdir(out):
            if n in ('assets','css','js'): continue
            pth=os.path.join(out,n); shutil.rmtree(pth) if os.path.isdir(pth) else os.remove(pth)
        for d,skip in (('css',()),('js',()),('assets',('_source','invest-logos'))):
            sync_tree(os.path.join(ROOT,d), os.path.join(out,d), skip)
        open(out+'/CNAME','w').write(S['cname']+'\n')
        open(out+'/.nojekyll','w').write('')
        open(out+'/robots.txt','w').write(f"User-agent: *\nAllow: /\nSitemap: {S['url']}sitemap.xml\n")
    for pg in site_pages():
        open(os.path.join(out, pg['slug']+'.html'),'w').write(render(pg))
    if key=='vii': write_company_pages(out)
    locs=write_sitemap(out)
    stubs,skipped=write_redirects(out)
    print(f"[{key}] {S['url']}  ->  {os.path.relpath(out, BASE)}/")
    print("  Pages:", ", ".join(pg['slug'] for pg in site_pages()))
    if key=='vii': print("  Company pages:", len(pages), f"(from {len(companies)} company records, {len(founders)} founder records)")
    print("  Sitemap URLs:", len(locs))
    print("  Redirect stubs:", len(stubs))
    for o,n in stubs:
        if not o.startswith('/companies/') or not n.endswith(o.lstrip('/')): print(f"      {o}  ->  {n}")
    if skipped:
        print("  Not stubbed:", len(skipped))
        for o,why in skipped: print(f"      {o}  ({why})")
