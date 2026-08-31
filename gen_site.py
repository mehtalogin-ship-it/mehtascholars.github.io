# -*- coding: utf-8 -*-
import json, re, os

# Cloudflare Pages serves public/, so generated HTML and the assets it references go
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
    p=[x for x in re.split(r'\s+',name.strip()) if x]
    if not p: return '?'
    return (p[0][0]+(p[-1][0] if len(p)>1 else '')).upper()

def slug(s):
    s=re.sub(r"[^a-z0-9]+","-",s.lower()).strip('-')
    return s or 'company'

def esc(t): return (t or '').replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

FONTS='<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Questrial&family=Playfair+Display:wght@500;600&family=Montserrat:wght@400;500;600&display=swap" rel="stylesheet">'

SEAL='''<svg class="seal" viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="48" fill="#0a582a"/><circle cx="50" cy="50" r="40" fill="none" stroke="#d9c67a" stroke-width="2"/><text x="50" y="46" text-anchor="middle" fill="#fff" font-family="Questrial, sans-serif" font-size="15">THE</text><text x="50" y="62" text-anchor="middle" fill="#d9c67a" font-family="Questrial, sans-serif" font-size="15">MEHTA</text><text x="50" y="82" text-anchor="middle" fill="#fff" font-family="Questrial, sans-serif" font-size="7" letter-spacing="1">ENDOWMENT</text></svg>'''

def nav(active, p=''):
    def cls(k): return ' class="active"' if k==active else ''
    return f'''  <header class="site-header">
    <nav class="nav">
      <a class="brand" href="{p}index.html"><img class="brand-logo" src="{p}assets/logo.png?v=1" alt="The Mehta Endowment seal" width="70" height="60"><span class="brand-name">Harker Venture<br>Investment Initiative</span></a>
      <button class="nav-toggle" aria-label="Menu">&#9776;</button>
      <ul class="nav-links">
        <li><a href="{p}index.html"{cls('home')}>Home</a></li>
        <li><a href="{p}about.html"{cls('about')}>About</a></li>
        <li class="has-drop"><a href="{p}alumni-companies.html"{cls('alumni')}>Alumni Companies</a>
          <ul class="drop">
            <li><a href="{p}alumni-companies.html#ai">AI</a></li>
            <li><a href="{p}alumni-companies.html#health">Health &amp; Bio</a></li>
            <li><a href="{p}alumni-companies.html#fintech">Fintech</a></li>
            <li><a href="{p}alumni-companies.html#security">Security</a></li>
            <li><a href="{p}alumni-companies.html#enterprise">Enterprise</a></li>
            <li><a href="{p}alumni-companies.html#commerce">Commerce</a></li>
          </ul></li>
        <li><a href="{p}our-investments.html"{cls('invest')}>Our Investments</a></li>
        <li><a href="{p}committee-list.html"{cls('committee')}>Committee List</a></li>
        <li><a href="{p}updates.html"{cls('updates')}>Updates</a></li>
        <li><a class="nav-cta" href="mailto:harkermehtascholars@gmail.com">Contact Us!</a></li>
      </ul>
    </nav>
  </header>'''

def footer(p=''):
    return f'''  <footer class="site-footer">
    <div class="wrap">
      <div class="footer-grid">
        <div><img class="footer-logo" src="{p}assets/logo.png?v=1" alt="The Mehta Endowment" width="118" height="101"><span class="brand-name">Harker Venture Investment Initiative</span>
          <p style="margin-top:14px;max-width:38ch">Mehta Scholars serve as analysts for The Harker Venture Pool, investing in and supporting Harker alumni founders.</p></div>
        <div><h4>Explore</h4><ul class="footer-links">
          <li><a href="{p}index.html">Home</a></li><li><a href="{p}about.html">About</a></li>
          <li><a href="{p}alumni-companies.html">Alumni Companies</a></li><li><a href="{p}our-investments.html">Our Investments</a></li>
          <li><a href="{p}committee-list.html">Committee List</a></li><li><a href="{p}updates.html">Updates</a></li></ul></div>
        <div><h4>Get in touch</h4><ul class="footer-links">
          <li><a href="mailto:MehtaScholars@harker.org">MehtaScholars@harker.org</a></li>
          <li><a href="mailto:harkermehtascholars@gmail.com">harkermehtascholars@gmail.com</a></li>
          <li style="color:var(--muted)">500 Saratoga Ave,<br>San Jose, CA 95129</li></ul></div>
      </div>
      <div class="footer-bottom"><span>&copy; 2026 The Harker Venture Investment Initiative &middot; Mehta Scholars</span><span>The Harker School</span></div>
    </div>
  </footer>
  <script src="{p}js/main.js?v=22"></script>
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
  <link rel="stylesheet" href="{p}css/styles.css?v=37">
</head>
<body>
'''

def inner_photo(name, p=''):
    """Return <img> if a real photo exists, else initials text."""
    ph=PHOTOS.get(name)
    if ph: return f'<img src="{p}{ph}" alt="{esc(name)}" loading="lazy">'
    return initials(name)

def avatar(name, cls='avatar', p=''):
    return f'<div class="{cls}">{inner_photo(name, p)}</div>'

# ============ HOME ============
home=head('Home | Mehta Scholars','The Harker Venture Investment Initiative — Mehta Scholars invest in and support Harker alumni founders and their companies.')
home+=nav('home')
home+='''
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
          <a class="btn" href="mailto:harkermehtascholars@gmail.com">Join Now</a>
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
home+=footer()
open(ROOT+'/index.html','w').write(home)

# ============ ABOUT ============
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
# final
_parts.append(_step('fin',_ICO_FLAG,'final','<h4>Founder works with the committee</h4><p>In every case, the founder works with committee members &mdash; especially the Entrepreneurship Advisory Committee.</p>'))
PROC=f'''<div class="process" id="procDiagram">
      <div class="pf">{''.join(_parts)}</div>
    </div>'''
TEAM=[('Class of 2025',['Andy Chung','Saahira Dayal','Sophie Degoricija','Ian Gerstner','Yifan Li','Tiana Salvi']),
      ('Class of 2026',['Tanvi Sivakumar','Leana Zhou']),
      ('Class of 2027',['Akash Dubey','Bazigh Tahirzad','David Kelly','Ronica Khattri','Amy Tong'])]
try: SCHOLAR_LI=json.load(open(CAP+'scholar_linkedin.json'))
except Exception: SCHOLAR_LI={}
teamhtml=''
for cls,ppl in TEAM:
    teamhtml+=f'<div class="class-block"><h3>{cls}</h3><div class="people">'
    for n in ppl:
        av=avatar(n); li=SCHOLAR_LI.get(n)
        if li: av=f'<a href="{li}" target="_blank" rel="noopener" class="scholar-link" aria-label="{esc(n)} on LinkedIn">{av}</a>'
        teamhtml+=f'<div class="person">{av}<div class="name">{n}</div></div>'
    teamhtml+='</div></div>'
about=head('About | Mehta Scholars','Meet the Mehta Scholar team and learn how our analysts research and invest in Harker alumni founders.')
about+=nav('about')
about+=f'''
  <section class="page-hero"><div class="wrap"><h1>The Mehta Scholar Team</h1><p>Student analysts for The Harker Venture Pool.</p></div></section>
  <section><div class="wrap" style="max-width:900px">
    <p style="font-size:1.15rem">Mehta Scholars serve as analysts for The Harker Venture Pool. This real-world, hands-on experience provides a unique opportunity to our advanced-level Business &amp; Entrepreneurship students who take Honors Corporate Finance &amp; Honors Venture Capital in their 11th-grade year. Top performers are then selected to be Mehta Scholars during their 12th-grade year.</p>
    <p style="font-size:1.15rem">Mehta Scholars identify, research, promote, and support alumni founders and their companies as they look to invest in their companies from the Harker Venture Pool. They also connect alumni founders with other VCs, Angel Investors, Entrepreneurs, and other Business and Technology Professionals in the Harker Strategic Ecosystem as needed.</p>
  </div></section>
  <section class="section-tint"><div class="wrap"><div class="section-head"><p class="eyebrow">Our Process</p><h2>From profile to investment</h2></div>
    {PROC}</div></section>
  <section><div class="wrap"><div class="section-head"><p class="eyebrow">Our Team</p><h2>Meet the scholars</h2></div>{teamhtml}</div></section>
'''
about+=footer()
open(ROOT+'/about.html','w').write(about)

# ============ ALUMNI COMPANIES ============
STAGE_ORDER=["Acquired / IPO'd",'Pre-Seed','Seed','Series A and Later']
SECTORS=[('all','All'),('ai','AI'),('health','Health &amp; Bio'),('fintech','Fintech'),('security','Security'),
 ('enterprise','Enterprise/SaaS'),('commerce','Commerce/Consumer'),('energy','Energy/Climate'),('media','Media/Gaming'),('hardware','Hardware/Deep-Tech')]
alumni=head('Alumni Companies | Mehta Scholars','Companies founded by Harker alumni across AI, health &amp; bio, fintech, security, enterprise, commerce, energy, media, and deep tech.')
alumni+=nav('alumni')
alumni+='''
  <section class="page-hero serif"><div class="wrap"><h1>Harker fosters the best.</h1><p>The companies founded by Harker alumni — the ventures our Mehta Scholars research, back, and champion.</p></div></section>
  <section class="co-section"><div class="wrap">
    <div class="filters">'''
alumni+=''.join(f'<button class="filter-btn{" active" if k=="all" else ""}" data-filter="{k}" id="{k}">{lbl}</button>' for k,lbl in SECTORS)
alumni+='</div>'
for stage in STAGE_ORDER:
    grp=[f for f in companies if f.get('stage_group')==stage]
    if not grp: continue
    alumni+=f'<div data-stage-group><h2 class="stage-label">{esc(stage)}</h2><div class="co-grid">'
    for f in grp:
        if f.get('tile'):
            thumb=f'<div class="co-thumb"><img src="{f["tile"]}?v=10" alt="{esc(f["company"])}" loading="lazy"></div>'
        else:
            thumb=f'<div class="co-thumb ph" style="--tc:{f.get("color","#2f6d3a")}"><span>{esc(f["company"])}</span></div>'
        alumni+=f'<a class="co-tile" data-sector="{f["sector_key"]}" href="companies/{f["page"]}.html">{thumb}<div class="co-name">{esc(f["name"])} {esc(f.get("year",""))}</div></a>'
    alumni+='</div></div>'
alumni+='</div></section>'
alumni+=footer()
open(ROOT+'/alumni-companies.html','w').write(alumni)

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

# ============ OUR INVESTMENTS ============
INV=[('Namrata Anand','\'10','Diffuse Bio','Health Tech & Life Sciences','Diffuse Bio is a biotechnology company specializing in generative AI for protein design. Their mission is to create AI systems that engineer novel, useful proteins with exceptional precision.'),
('Barrett Glasauer','\'09','Rejigg','Fintech','Rejigg connects quality small business owners with vetted buyers, minimizing fees, eliminating brokers, and streamlining the acquisition process.'),
('Surhbi Sarna','\'03','Collate','Health Tech & Life Sciences','Collate uses AI to create and streamline accurate documentation for diagnostic, medical device, and drug development companies, thereby reducing time to market and expediting the creation of life-saving innovations.'),
('Aumesh Mishra','\'16','Tivara','Health Tech & Life Sciences','Tivara is an AI company that automates insurance approval (prior authorization) for healthcare clinics, helping doctors deliver care to patients faster.'),
('Anita Modi','\'04','Peer AI','Health Tech & Life Sciences','Peer AI is an agentic AI platform that provides support for regulatory documentation for life sciences and biotech companies with strong security and compliance.'),
('Drew Goldstein','\'13','Ephemeral Technologies','Health Tech & Life Sciences','Ephemeral Technologies works to accelerate end-to-end drug development and delivery using an integrated AI, software, and robotics platform.'),
('Daanish Jamal','\'12','Dolomite Therapeutics','Health Tech & Life Sciences','Dolomite Therapeutics works to develop biologic degraders that induce durable remission in patients with autoimmune kidney disease.')]
inv=head('Our Investments | Mehta Scholars',"Harker's Mehta Scholars put $25k SAFEs into Harker alumni startups. See a selection of our past investments.")
inv+=nav('invest')
inv+='''
  <section class="page-hero"><div class="wrap"><h1>Our Investments</h1><p>Harker's Mehta Scholars put $25k SAFEs into Harker alumni startups. We review reports with the Venture Advisory Committee and the Venture Investment Committee. Here are a few of our past investments.</p></div></section>
  <section><div class="wrap"><div class="invest">'''
for nm,yr,co,tag,desc in INV:
    sl=slug(co)
    logo=f'<div class="invest-logo"><img src="assets/invest-logos/{sl}.png?v=2" alt="{esc(co)} logo" loading="lazy"></div>' if os.path.exists(f'{ROOT}/assets/invest-logos/{sl}.png') else ''
    inv+=f'''<div class="invest-card">
      <div class="invest-top">
        <div class="invest-co-block">{logo}<div class="co">{esc(co)}</div></div>
        <div class="invest-founder">{esc(nm)} {esc(yr)}</div>
      </div>
      <div class="invest-body">
        <div class="invest-headshot">{inner_photo(nm)}</div>
        <span class="tag">{esc(tag)}</span>
        <p>{esc(desc)}</p>
        <a class="btn small" href="companies/{sl}.html">More on {esc(co)}</a>
      </div></div>'''
inv+='</div></div></section>'
inv+=footer()
open(ROOT+'/our-investments.html','w').write(inv)

# ============ COMMITTEE ============
ORDER=['Venture Investment Committee','Venture Advisory Committee','Entrepreneurship Advisory Committee']
comm=head('Committee List | Mehta Scholars','The Venture Investment, Venture Advisory, and Entrepreneurship Advisory Committees supporting the Mehta Scholars.')
comm+=nav('committee')
comm+='''
  <section class="page-hero serif"><div class="wrap"><h1>Harker connects you with the best.</h1><p>The committees of experienced investors and founders who guide, review, and support our work.</p></div></section>'''
def linklabel(u): return 'Instagram' if 'instagram.com' in (u or '') else 'LinkedIn'
cdata=[]; idx=0; tint=False
for grp in ORDER:
    mem=[m for m in committee if m['committee']==grp]
    if not mem: continue
    seccls=' section-tint' if tint else ''; tint=not tint
    comm+=f'<section class="{seccls.strip()}"><div class="wrap"><div class="section-head"><p class="eyebrow">{grp}</p></div><p class="committee-intro">{esc(sections.get(grp,""))}</p><div class="members-grid">'
    for m in mem:
        cdata.append({'name':m['name'],'org':m['org'],'bio':m.get('bio',''),
          'linkedin':m.get('linkedin',''),'linklabel':linklabel(m.get('linkedin','')),
          'company':m.get('company_url',''),'photo':PHOTOS.get(m['name'],''),'initials':initials(m['name'])})
        comm+=f'''<button class="member-tile" data-idx="{idx}"><div class="photo">{inner_photo(m['name'])}</div><div class="m-head"><h3>{esc(m['name'])}</h3><div class="org">{esc(m['org'])}</div><p class="tile-bio">{esc(m.get('bio',''))}</p></div><span class="tile-more">View profile &rarr;</span></button>'''
        idx+=1
    comm+='</div></div></section>'
comm+='''
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
comm+=footer()
open(ROOT+'/committee-list.html','w').write(comm)

# ============ UPDATES ============
upd=head('Updates | Mehta Scholars','News and updates from The Harker Venture Investment Initiative.')
upd+=nav('updates')
upd+='''
  <section class="page-hero"><div class="wrap"><h1>Updates</h1><p>News, milestones, and announcements from the Mehta Scholars.</p></div></section>
  <section><div class="wrap"><div class="posts">
    <article class="post"><div class="post-cover"><h2>Mehta Scholars Attend Startup World Cup</h2></div>
      <div class="post-body"><div class="post-meta"><span>Harker Mehta Scholars</span><span>Apr 26</span><span>1 min read</span></div>
      <p>On April 17th, our Mehta Scholar team participated in the Startup World Cup Youth Qualifier, organized by Harker and Pegasus Tech Ventures. Our senior Mehta Scholars, Leana Zhou and Tanvi Sivakumar, facilitated the fireside chat with Brandon Yang from Cartesia. Meanwhile, our junior Mehta Scholars engaged in networking opportunities with professionals across various industries, gaining key insights and forming important connections.</p></div></article>
  </div></div></section>'''
upd+=footer()
open(ROOT+'/updates.html','w').write(upd)

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

print("Generated: index, about, alumni-companies, our-investments, committee-list, updates")
print("Company pages:", len(pages), f"(from {len(companies)} company records, {len(founders)} founders)")
print("Redirect stubs:", len(stubs))
for o,n in stubs: print(f"    {o}  ->  {n}")
if skipped:
    print("Not stubbed:", len(skipped))
    for o,why in skipped: print(f"    {o}  ({why})")
