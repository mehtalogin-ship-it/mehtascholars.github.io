import sys, os, json, re, io, base64, urllib.request, urllib.parse
import numpy as np
from collections import deque
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

W, H = 1284, 1194
# Paths are resolved against the repo, not the caller's cwd. captured/ lives at the
# repo root; everything the site serves lives under public/.
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB  = os.path.join(BASE, 'public')
FONT = os.path.join(PUB, 'assets', 'fonts', 'Questrial.ttf')
TEX  = os.path.join(PUB, 'assets', 'tiles', '_texture.png')
UA = {'User-Agent': 'Mozilla/5.0'}

def fetch(url, timeout=15):
    u = url
    for _ in range(5):
        req = urllib.request.Request(u, headers=UA)
        try:
            r = urllib.request.urlopen(req, timeout=timeout)
            return r.read(), r.geturl()
        except urllib.error.HTTPError as e:
            if e.code in (301, 302, 307, 308) and e.headers.get('Location'):
                u = urllib.parse.urljoin(u, e.headers['Location']); continue
            raise
    raise RuntimeError('too many redirects')

def get_icon(site):
    try:
        html_b, base = fetch(site)
    except Exception:
        base = site; html_b = b''
    html = html_b.decode('utf-8', 'ignore')
    urls = []
    for tag in re.findall(r'<link[^>]+>', html, re.I):
        if not re.search(r'rel="[^"]*icon', tag, re.I): continue
        m = re.search(r'href="([^"]+)"', tag)
        if m: urls.append(m.group(1))
    m = re.search(r'property="og:image"[^>]*content="([^"]+)"', html, re.I)
    if m: urls.append(m.group(1))
    for p in ('/apple-touch-icon.png', '/apple-icon.png', '/icon.png', '/logo.png', '/favicon.png'):
        urls.append(urllib.parse.urljoin(base, p))
    # download every candidate, keep the one with the largest min-dimension (skip banners)
    best = None; best_score = 0
    seen = set()
    for u in urls:
        if u in seen: continue
        seen.add(u)
        try:
            if u.startswith('data:'):
                data = base64.b64decode(u.split(',', 1)[1])
            else:
                data, _ = fetch(urllib.parse.urljoin(base, u))
            img = Image.open(io.BytesIO(data)).convert('RGBA')
        except Exception:
            continue
        w, h = img.size
        if min(w, h) < 48: continue
        if max(w, h) / min(w, h) > 2.4: continue          # skip wide banners/wordmarks
        score = min(w, h)
        if score > best_score:
            best, best_score = img, score
            if best_score >= 460: break
    if best is not None:
        return best
    try:
        dom = urllib.parse.urlparse(site).netloc.replace('www.', '')
        data, _ = fetch(f'https://icon.horse/icon/{dom}')
        return Image.open(io.BytesIO(data)).convert('RGBA')
    except Exception:
        return None

def central_components(binary):
    """binary HxW bool -> keep only comps that reach the central box, drop specks."""
    h, w = binary.shape
    cy0, cy1, cx0, cx1 = int(h*0.24), int(h*0.76), int(w*0.24), int(w*0.76)
    seen = np.zeros((h, w), bool); keep = np.zeros((h, w), bool)
    minarea = 0.004 * h * w
    for i in range(h):
        for j in range(w):
            if binary[i, j] and not seen[i, j]:
                q = deque([(i, j)]); seen[i, j] = True; pix = []; touches = False
                while q:
                    y, x = q.popleft(); pix.append((y, x))
                    if cy0 <= y < cy1 and cx0 <= x < cx1: touches = True
                    for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                        ny, nx = y+dy, x+dx
                        if 0 <= ny < h and 0 <= nx < w and binary[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True; q.append((ny, nx))
                if touches and len(pix) >= minarea:
                    for (y, x) in pix: keep[y, x] = True
    return keep

def white_mark(img):
    bb = img.getbbox()
    if bb: img = img.crop(bb)
    if max(img.size) > 600:
        img = ImageOps.contain(img, (600, 600))
    arr = np.asarray(img).astype(float); rgb, a = arr[..., :3], arr[..., 3]
    if (1.0 - (a > 200).mean()) > 0.08:
        mask = a / 255.0
    else:
        hh, ww = a.shape; b = max(3, int(min(hh, ww) * 0.06))
        border = np.concatenate([rgb[:b].reshape(-1,3), rgb[-b:].reshape(-1,3),
                                 rgb[:, :b].reshape(-1,3), rgb[:, -b:].reshape(-1,3)])
        bg = np.median(border, axis=0)
        dist = np.sqrt(((rgb - bg) ** 2).sum(-1))
        mask = np.clip((dist - 60) / 40, 0, 1)
    # cleanup: keep central connected components on a downsampled grid
    binary = mask > 0.5
    cov = binary.mean()
    if cov > 0.9 or cov < 0.006:
        return None, cov
    small = np.asarray(Image.fromarray((binary*255).astype(np.uint8)).resize((170,170), Image.NEAREST)) > 128
    keepS = central_components(small)
    keep = np.asarray(Image.fromarray((keepS*255).astype(np.uint8)).resize(mask.shape[::-1], Image.NEAREST)) > 128
    mask = mask * keep
    if (mask > 0.5).mean() < 0.004:
        return None, cov
    out = np.zeros((*mask.shape, 4), np.uint8); out[..., :3] = 255
    out[..., 3] = (np.clip(mask, 0, 1) * 255).astype(np.uint8)
    m = Image.fromarray(out)
    m = m.filter(ImageFilter.GaussianBlur(0.6))
    bb = m.getbbox()
    if bb: m = m.crop(bb)
    return m, cov

def hex2rgb(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))

def compose(color, name, mark, out):
    base = Image.new('RGBA', (W, H), hex2rgb(color)+(255,))
    base.alpha_composite(Image.open(TEX).convert('RGBA').resize((W, H)))
    draw = ImageDraw.Draw(base)
    lg = ImageOps.contain(mark, (500, 500), Image.LANCZOS)
    cx = (W-lg.size[0])//2; cy = int(H*0.23) + (500-lg.size[1])//2
    base.alpha_composite(lg, (cx, cy))
    name_y = int(H*0.23) + 500 + 46
    def fit(txt, size, maxw):
        f = ImageFont.truetype(FONT, size)
        while draw.textlength(txt, font=f) > maxw and size > 22:
            size -= 4; f = ImageFont.truetype(FONT, size)
        return f
    f = fit(name, 150, W-180); tw = draw.textlength(name, font=f)
    draw.text(((W-tw)//2, name_y), name, font=f, fill=(255,255,255,255))
    base.convert('RGB').save(out, quality=94)

if __name__ == '__main__':
    slugs = sys.argv[1].split(',')
    r = json.load(open(os.path.join(BASE, 'captured', 'companies.json')))
    by = {e['slug']: e for e in r}
    made=[]; nameonly=[]; fail=[]
    for slug in slugs:
        e = by.get(slug)
        if not e or not (e.get('website') or '').strip():
            nameonly.append(slug); continue
        img = get_icon(e['website'])
        if img is None: fail.append((slug,'no icon')); continue
        mark, cov = white_mark(img)
        if mark is None: nameonly.append(slug); continue
        compose(e.get('color','#2f6d3a'), e['company'], mark, os.path.join(PUB, "assets", "tiles", f"{slug}.png"))
        made.append(slug)
    print('MADE', len(made), made)
    print('NAMEONLY', len(nameonly), nameonly)
    print('FAIL', len(fail), fail)
