# -*- coding: utf-8 -*-
import json, re, os

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

def _href(h, p=''):
    """Leave mailto:/http(s)/#/tel alone; prefix internal links with the page's
    depth. Lets the nav CTA become a real contact page later without touching nav()."""
    return h if re.match(r'^(mailto:|https?:|#|tel:)', h) else p+h

def nav(active, p=''):
    def cls(k): return ' class="active"' if k==active else ''
    def link(pg): return f'<a href="{p}{pg["slug"]}.html"{cls(pg["key"])}>{pg["label"]}</a>'
    items=[]
    for tr,heading in TRACKS:
        grp=[pg for pg in PAGES if pg.get('track')==tr and pg.get('label')]
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
      <a class="brand" href="{p}index.html"><img class="brand-logo" src="{p}assets/logo.png?v=1" alt="The Mehta Endowment seal" width="70" height="60"><span class="brand-name">Harker Venture<br>Investment Initiative</span></a>
      <button class="nav-toggle" aria-label="Menu">&#9776;</button>
      <ul class="nav-links">
        {lis}
      </ul>
    </nav>
  </header>'''

def footer(p=''):
    ex=[f'<li><a href="{p}{pg["slug"]}.html">{pg["label"]}</a></li>' for pg in PAGES if pg.get('foot') and pg.get('label')]
    rows='\n          '.join(''.join(ex[i:i+2]) for i in range(0,len(ex),2))
    return f'''  <footer class="site-footer">
    <div class="wrap">
      <div class="footer-grid">
        <div><img class="footer-logo" src="{p}assets/logo.png?v=1" alt="The Mehta Endowment" width="118" height="101"><span class="brand-name">Harker Venture Investment Initiative</span>
          <p style="margin-top:14px;max-width:38ch">Mehta Scholars serve as analysts for The Harker Venture Pool, investing in and supporting Harker alumni founders.</p></div>
        <div><h4>Explore</h4><ul class="footer-links">
          {rows}</ul></div>
        <div><h4>Get in touch</h4><ul class="footer-links">
          <li><a href="mailto:MehtaScholars@harker.org">MehtaScholars@harker.org</a></li>
          <li style="color:var(--muted)">500 Saratoga Ave,<br>San Jose, CA 95129</li></ul></div>
      </div>
      <div class="footer-bottom"><span>&copy; 2026 The Harker Venture Investment Initiative &middot; Mehta Scholars</span><span>The Harker School</span></div>
    </div>
  </footer>
  <script src="{p}js/main.js?v=24"></script>
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
  <link rel="stylesheet" href="{p}css/styles.css?v=39">
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
            <div class="ws-card" data-c="0"><div class="ico"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20v-6M6 20v-4M18 20v-9"/><circle cx="12" cy="8" r="3"/></svg></div><div><p class="kicker">Exceptional Mentorship</p><h3>Industry Insights</h3><p>Industry insights and guidance from experienced mentors within Harker's network.</p></div></div>
            <div class="ws-card" data-c="1"><div class="ico"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/></svg></div><div><p class="kicker">Strategic Partnerships</p><h3>Forge Connections</h3><p>Partnerships with forward-thinking people and organizations to drive mutual success.</p></div></div>
            <div class="ws-card" data-c="2"><div class="ico"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v10M9 10h4a2 2 0 0 1 0 4H9"/></svg></div><div><p class="kicker">Access to Funding</p><h3>Fuel Your Growth</h3><p>Access to funding sources through our extensive network to fuel your growth.</p></div></div>
          </div>
        </div>
        <div class="ws-slide" data-i="1"><div class="ws-inner">
          <p class="eyebrow">Join Our Network</p>
          <h2>Explore collaboration, mentorship &amp; investment</h2>
          <p>Connect with a diverse network of entrepreneurs, industry experts, and investors to explore collaborations, mentorship, and investment opportunities.</p>
          <a class="btn" href="mailto:MehtaScholars@harker.org">Join Now</a>
        </div></div>
      </div>
      <div class="wall-dots"><span class="wall-dot is-on"></span><span class="wall-dot"></span></div>
      <div class="intro-overlay">
        <div class="wrap">
          <div class="hero-box">
            <h1>The Harker Venture Investment Initiative</h1>
            <p>Student analysts investing in — and championing — the next generation of Harker alumni founders.</p>
            <p class="hero-cta"><a class="btn" href="our-investments.html">See our investments</a> <a class="btn ghost" href="about.html">Meet the scholars</a></p>
          </div>
        </div>
      </div>
      <div class="intro-cue" aria-hidden="true">Scroll to step inside</div>
    </div>
  </section>
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
STAGE_ORDER=["Acquired / IPO'd",'Pre-Seed','Seed','Series A and Later']
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
                thumb=f'<div class="co-thumb"><img src="{f["tile"]}?v=10" alt="{esc(f["company"])}" loading="lazy"></div>'
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
('Surhbi Sarna','\'03','Collate','Health Tech & Life Sciences','Collate uses AI to create and streamline accurate documentation for diagnostic, medical device, and drug development companies, thereby reducing time to market and expediting the creation of life-saving innovations.','collate'),
('Aumesh Mishra','\'16','Tivara','Health Tech & Life Sciences','Tivara is an AI company that automates insurance approval (prior authorization) for healthcare clinics, helping doctors deliver care to patients faster.','tivara'),
('Anita Modi','\'04','Peer AI','Health Tech & Life Sciences','Peer AI is an agentic AI platform that provides support for regulatory documentation for life sciences and biotech companies with strong security and compliance.','peer-ai'),
('Drew Goldstein','\'13','Ephemeral Technologies','Health Tech & Life Sciences','Ephemeral Technologies works to accelerate end-to-end drug development and delivery using an integrated AI, software, and robotics platform.','ephemeral-technologies'),
('Tanuj Thapliyal','\'06','Kos.ai','Fintech','Kos.ai is a virtual finance employee that autonomously completes critical financial workflows - invoice reviews, purchase orders and custom finance processes - for capital-intensive industries such as datacenters, defense, energy and construction.','tanuj-thapliyal'),
('Ravi Mishra','\'04','Ample','AI and Smart Tech','Ample is building cloud infrastructure that deploys a full application from a single prompt to a coding agent, handling hosting, configuration and scaling behind the scenes. It folds existing infrastructure products into one assembled system, taking an app live in around 30 seconds.','ample'),
('Rajiv Sancheti','','Caddy','AI and Smart Tech','Caddy is a personal AI for everyday work that lives in your text messages. It surfaces what matters from your email, calendar and apps, and acts on it when you reply.','caddy')]

def sec_investments():
    out='\n  <section><div class="wrap"><div class="invest">'
    for nm,yr,co,tag,desc,page in INV:
        sl=slug(co)
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
        <a class="btn small" href="companies/{page}.html">More on {esc(co)}</a>
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
def sec_updates():
    return '''
  <section><div class="wrap"><div class="posts">
    <article class="post"><div class="post-cover"><h2>Mehta Scholars Attend Startup World Cup</h2></div>
      <div class="post-body"><div class="post-meta"><span>Harker Mehta Scholars</span><span>Apr 26</span><span>1 min read</span></div>
      <p>On April 17th, our Mehta Scholar team participated in the Startup World Cup Youth Qualifier, organized by Harker and Pegasus Tech Ventures. Our senior Mehta Scholars, Leana Zhou and Tanvi Sivakumar, facilitated the fireside chat with Brandon Yang from Cartesia. Meanwhile, our junior Mehta Scholars engaged in networking opportunities with professionals across various industries, gaining key insights and forming important connections.</p></div></article>
  </div></div></section>'''

# ============ THE REGISTRY ============
PAGES=[
 dict(slug='index', key='home', label='Home', track='main', foot=True,
      title='Home | Mehta Scholars',
      desc='The Harker Venture Investment Initiative — Mehta Scholars invest in and support Harker alumni founders and their companies.',
      hero=None, body=[sec_home_intro]),

 dict(slug='about', key='about', label='About', track='main', foot=True,
      title='About | Mehta Scholars',
      desc='Meet the Mehta Scholar team and learn how our analysts research and invest in Harker alumni founders.',
      hero=('The Mehta Scholar Team','Student analysts for The Harker Venture Pool.'),
      body=[sec_about_prose, sec_process, sec_team]),

 dict(slug='alumni-companies', key='alumni', label='Alumni Companies', track='main', foot=True,
      title='Alumni Companies | Mehta Scholars',
      desc='Companies founded by Harker alumni across AI, health &amp; bio, fintech, security, enterprise, commerce, energy, media, and deep tech.',
      drop=[('ai','AI'),('health','Health &amp; Bio'),('fintech','Fintech'),
            ('security','Security'),('enterprise','Enterprise'),('commerce','Commerce')],
      hero=('Harker fosters the best.','The companies founded by Harker alumni — the ventures our Mehta Scholars research, back, and champion.','serif'),
      body=[sec_alumni_grid]),

 dict(slug='our-investments', key='invest', label='Our Investments', track='main', foot=True,
      title='Our Investments | Mehta Scholars',
      desc="Harker's Mehta Scholars invest in Harker alumni startups. See a selection of our past investments.",
      hero=('Our Investments',"Harker's Mehta Scholars invest in Harker alumni startups. We review reports with the Venture Advisory Committee and the Venture Investment Committee, then decide together. Here are a few of our past investments."),
      body=[sec_investments]),

 dict(slug='committee-list', key='committee', label='Committee List', track='main', foot=True,
      title='Committee List | Mehta Scholars',
      desc='The Venture Investment, Venture Advisory, and Entrepreneurship Advisory Committees supporting the Mehta Scholars.',
      hero=('Harker connects you with the best.','The committees of experienced investors and founders who guide, review, and support our work.','serif'),
      body=[sec_committee]),

 dict(slug='updates', key='updates', label='Updates', track='main', foot=True,
      title='Updates | Mehta Scholars',
      desc='News and updates from The Harker Venture Investment Initiative.',
      hero=('Updates','News, milestones, and announcements from the Mehta Scholars.'),
      body=[sec_updates]),
]

def render(pg, p=''):
    doc=head(pg['title'], pg['desc'], p)
    doc+=nav(pg['key'], p)
    if pg.get('hero'): doc+=sec_hero(*pg['hero'])
    for s in pg['body']: doc+=s()
    doc+=footer(p)
    return doc

for pg in PAGES:
    open(os.path.join(ROOT, pg['slug']+'.html'),'w').write(render(pg))

# ============ COMPANY / FOUNDER DETAIL PAGES ============
os.makedirs(ROOT+'/companies',exist_ok=True)
pages={}
for f in companies: pages.setdefault(f['page'],[]).append(f)
def fact(label,val): return f'<div class="fact"><span class="fact-l">{label}</span><span class="fact-v">{esc(val)}</span></div>' if val else ''
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
    doc=head(f"{f0['name']} | Mehta Scholars", f"{f0['name']} — {', '.join(c['company'] for c in cos)}.", p='../')
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
    open(f'{ROOT}/companies/{pgslug}.html','w').write(doc)

# ============ SITEMAP ============
# Generated from the registry so an IA change cannot leave it stale. It used to be
# hand-maintained inside public/ - the one directory contributors are told never to
# edit - and had drifted (it listed pages that no longer existed and missed two new ones).
SITE='https://www.mehtascholars.com/'
locs=[SITE]+[SITE+pg['slug']+'.html' for pg in PAGES if pg['slug']!='index'] \
           +[SITE+'companies/'+s+'.html' for s in sorted(pages)]
open(ROOT+'/sitemap.xml','w',encoding='utf-8').write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + ''.join(f'  <url><loc>{u}</loc></url>\n' for u in locs) + '</urlset>\n')

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

stubs=[]; skipped=[]
for line in open(os.path.join(BASE,'captured','redirects.txt'), encoding='utf-8'):
    line=line.strip()
    if not line or line.startswith('#'): continue
    parts=line.split()
    if len(parts) < 2: continue
    old, new = parts[0], parts[1]
    if '*' in old:
        skipped.append((old,'wildcard - needs a 404 page')); continue
    old = old.lstrip('/')
    if not old: continue
    # Pages already resolves /foo to foo.html, so an identity mapping needs no stub
    # (and a stub there would add a pointless extra hop).
    if new.lstrip('/') == old + '.html':
        skipped.append(('/'+old,'Pages resolves this already')); continue
    dest = os.path.join(ROOT, old) if old.endswith('.html') else os.path.join(ROOT, old, 'index.html')
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    open(dest,'w',encoding='utf-8').write(redirect_stub(new))
    stubs.append(('/'+old, new))

print("Generated:", ", ".join(pg['slug'] for pg in PAGES))
print("Company pages:", len(pages), f"(from {len(companies)} company records, {len(founders)} founder records)")
print("Sitemap URLs:", len(locs))
print("Redirect stubs:", len(stubs))
for o,n in stubs: print(f"    {o}  ->  {n}")
if skipped:
    print("Not stubbed:", len(skipped))
    for o,why in skipped: print(f"    {o}  ({why})")
