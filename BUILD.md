# Building & updating the site

This is a **static site generated from data**. Content lives in `captured/*.json`;
`gen_site.py` turns it into the HTML you deploy. There is no server or database.

## Update content (companies, founders, committee, scholars)
1. Edit the relevant file in `captured/` (e.g. `companies.json`, `photo_map.json`,
   `scholar_linkedin.json`, `committee.json`).
2. Regenerate the site:
   ```bash
   python3 gen_site.py
   ```
3. Commit and push. The host redeploys automatically.

## Change design / layout
Edit `public/css/styles.css`, `public/js/main.js`, or the page templates inside
`gen_site.py`, then run `python3 gen_site.py`, commit, and push.

## Add or fix logos / headshots (occasional)
Helper tools live in `scripts/` (`tilegen.py` builds white-silhouette logo tiles,
`procphoto.py` squares up headshots). They need `pip install pillow numpy` and the
font at `assets/fonts/Questrial.ttf`.

## Layout
`gen_site.py` and `captured/` live at the repo root; everything the site serves lives in
`public/`. The generator reads from `captured/` and writes into `public/` - so the only
directory that gets deployed is `public/`, and nothing generated ever lands at the root.

## Hosting
Static, no build step. **GitHub Pages** is the host: `.github/workflows/pages-deploy.yml`
runs on every push to `main` and publishes the `public/` directory as the Pages artifact.
**Cloudflare** is only DNS — it points the custom domain at GitHub Pages. There is no
Cloudflare Pages build, and nothing in this repo configures Cloudflare.

Because GitHub Pages serves the artifact as-is, `public/_redirects` does nothing.
That file is Netlify/Cloudflare Pages syntax and GitHub Pages has no equivalent, so the
old Wix slug redirects it lists are not in effect — see "Redirects" below.

## Redirects
`public/_redirects` is inert on GitHub Pages. To actually redirect the old Wix URLs,
either:
- add a small HTML file at each old path containing a `<meta http-equiv="refresh">` plus
  a `<link rel="canonical">`, generated from the same list; or
- do it at the edge in Cloudflare with Redirect Rules / Bulk Redirects, which needs the
  domain proxied through Cloudflare (orange cloud), not DNS-only.

The second is cleaner and uses infrastructure that is already there.
