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
Static, no build step — **Cloudflare Pages**, serving `public/`. Pushing to `main`
triggers a redeploy. Custom domain + SSL are set in the Cloudflare dashboard, and the
build output directory there must be `public`.
```
