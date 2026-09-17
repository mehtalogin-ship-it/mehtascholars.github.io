# HANDOFF — Mehta Scholars site

> Orientation for a fresh Claude Code session. Read this first, then `BUILD.md` for the
> how-to. If the two ever disagree, trust the code — check `gen_site.py`.

---

## 0. What this is

**mehtascholars.com** — "The Harker Venture Investment Initiative" / Mehta Scholars. The
site was rebuilt from the old Wix site as freestanding HTML/CSS/JS the school owns. The
owner is Akash Dubey, a Mehta Scholar (Class of 2027); it is his own initiative's site.

**The rebuild and the cutover are both done.** The site is live on GitHub Pages. The
original migration task in earlier versions of this file — capture assets out of the Wix
editor — is complete and has been removed.

Standing rules:
- **Don't invent content.** Names, class years, companies and investments are claims about
  real people. If a fact is not in `captured/` or a source document, ask rather than guess.
- Confirm before anything outward-facing: pushes, DNS, publishing.

---

## 1. How the project is shaped

This is a **static site generated from JSON**. There is no server, no database, no build
toolchain — `gen_site.py` is plain Python stdlib.

```
gen_site.py          the generator: reads captured/, writes public/
captured/*.json      the content (companies, founders, committee, photos, redirects)
scripts/             tilegen.py (company tiles), procphoto.py (headshots)
public/              EVERYTHING THE SITE SERVES - this is what deploys
source-media/        raw phone/video source. gitignored, never deployed
.github/workflows/   pages-deploy.yml — publishes public/ on every push to main
```

The split that matters: **`captured/` is input and stays at the repo root; `public/` is
output.** `gen_site.py` resolves both from its own location, so the repo can live anywhere.

Regenerate with `python3 gen_site.py`. It is idempotent — run it after any content or
template change, then commit.

### What it produces

| | |
|---|---|
| 6 top-level pages | index, about, alumni-companies, our-investments, committee-list, updates |
| 98 company pages | `public/companies/`, from 107 records in `companies.json` |
| 10 redirect stubs | old Wix URLs → new pages |

Current data: **107 company records · 43 founders · 56 committee members · 8 investments.**

---

## 2. Hosting

**GitHub Pages**, serving `public/` via `.github/workflows/pages-deploy.yml`. Pushing to
`main` redeploys. The custom domain was bought through **Wix, which is the registrar only** —
its DNS panel points the domain at Pages. No Wix site, no Netlify, no Cloudflare is in the
serving path.

See `BUILD.md` → Hosting for the full picture.

---

## 3. Design system

- **Colors:** `#0a582a` dark forest green (primary / nav CTA), `#038112` accent green
  (active links), `#073d1e` deep green, `#1a1a1a` ink.
- **Fonts:** headings **Questrial**, serif accents **Playfair Display**, body **Montserrat**
  — all Google Fonts, defined as `--font-head` / `--font-serif` / `--font-body`.
- **Logo:** the real Mehta Endowment seal, in the header, footer and favicon.
- **Homepage:** a scroll-scrubbed 80-frame camera flight from outside the Rothschild
  Performing Arts Center into its lobby, landing on the black LED wall, which then powers
  on to white and carries two content slides. Frames are WebP in three resolution tiers.
  See `BUILD.md` → The homepage intro frames.

---

## 4. Gotchas that have already cost time

- **`public/_redirects` is gone and was never functional here.** It is Netlify/Cloudflare
  syntax; GitHub Pages ignores it. The list now lives at `captured/redirects.txt` and
  `gen_site.py` writes real meta-refresh stub pages from it. A stub is a client-side
  redirect, not a 301 — that is the ceiling on a static host.
- **The intro master has a defect baked in.** Frames 68–77 are frozen and frame 78 jumps
  backward. The frames on the site bridge it procedurally. If the video is ever
  regenerated, expect to fix it again — `BUILD.md` documents the method.
- **The intro's last frames must be exactly `#000000`** and are encoded **lossless**; lossy
  WebP shifts pure black off zero and the handoff to the page shows a seam.
- **`scripts/tilegen.py` builds flat white silhouettes from the alpha channel**, so any logo
  whose detail is a cut-out loses that detail. The KOS tile is a blank shield for this
  reason. Logos with interior detail need to be placed by hand.
- **Never commit media.** `source-media/` and `public/assets/intro/_source/` are gitignored.
  Git keeps binaries forever; a stray `git add -A` is unrecoverable without a rewrite.
- **Keep this repo out of iCloud.** A copy once lived in `~/Documents` and iCloud evicted its
  contents, leaving an unreadable `.git`. Repos belong outside `Documents` and `Desktop`.

---

## 5. Open items

1. **Page heroes have no photography.** All five inner pages use a flat green gradient.
   There are 41 real photos and videos of the building in `source-media/` — including
   12 MP interior shots of the actual lobby — that could sit behind those headers.
2. **Some category tags are inferred** from each company's business rather than from an
   explicit mapping, which the old Wix site never exposed. A real mapping from the owner
   would settle them.
3. **Missing headshots.** Ravi Mishra (Ample) and Tanuj Thapliyal (Kos.ai) fall back to
   initials avatars. Tanuj also has **no Harker class year** anywhere in `captured/`.
4. **Live chat is wired but disabled.** `var TAWK_SRC = ''` in `public/js/main.js`. The owner
   must paste their own Tawk.to embed URL to enable it; do not create the account for them.
5. **`MIGRATION.md` is stale.** Its §7 still says "Cutover — NOT started. Domain still points
   to Wix," which is false — the site has been live for weeks. That file needs the same pass
   this one just had.

---

## 6. Verification after any change

```bash
python3 gen_site.py
cd ~/Code/mehta-scholars-site && python3 -m http.server 8747 --directory public
```

Then check:
- All 6 pages return 200 with no console errors.
- Alumni filter: selecting Fintech narrows the roster to the fintech companies (13 records)
  and hides empty stage groups.
- Mobile nav toggle works below **940px**; the Alumni Companies dropdown works on hover
  and focus.
- Homepage: the flight scrubs smoothly with no stall or backward jump, lands on pure black,
  then the wall powers on to white before any content appears.
