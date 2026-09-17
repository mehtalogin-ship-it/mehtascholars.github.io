# AGENTS.md — how to edit this website without breaking it

You are working on **mehtascholars.com**, the live public site of The Harker Venture
Investment Initiative (Mehta Scholars). Read this file before touching anything.

The person directing you is a Mehta Scholar, not necessarily a developer. They may ask for
something in plain terms ("add this company", "fix this bio"). Your job is to translate that
into the right edit **in the right place** — which is usually not the file that contains the
text they're looking at.

---

## THE ONE RULE

### Never edit anything inside `public/`.

Every file in `public/` — all the HTML, the company pages, the redirect stubs — is
**generated** by `gen_site.py`. If you hand-edit one, your change looks correct, gets
committed, and is then **silently erased** the next time anyone runs the generator. Nobody
will know why the change disappeared.

```
EDIT THESE                          NEVER EDIT THESE
captured/*.json    ← content        public/*.html
gen_site.py        ← page templates public/companies/*.html
public/css/styles.css  ← design *   public/our-companies/, /blog/, /fintech/ … (stubs)
public/js/main.js      ← behavior *
```

\* `styles.css` and `main.js` live under `public/` but are **hand-written, not generated**.
They are the two exceptions. Everything else in `public/` is output.

**If you are about to edit an `.html` file, stop.** Find the source instead: page structure
and copy live in `gen_site.py`; data lives in `captured/`.

---

## How the site is built

```
captured/*.json  ──►  gen_site.py  ──►  public/  ──►  GitHub Pages
   (content)         (templates)      (the site)      (live in ~1 min)
```

Plain Python, standard library only. No build tools, no npm, no framework.

```bash
python3 gen_site.py
```

Safe to run any time — it is idempotent (running it twice changes nothing the second time).
**Run it after every content or template change**, then commit both your source edit and the
regenerated `public/` files together.

---

## Publishing — read this before you push

**Pushing to `main` publishes to the live public website within about a minute.** There is no
staging environment and no review step. `.github/workflows/pages-deploy.yml` deploys `public/`
on every push.

So:

- **Always preview locally before pushing** (see Verify below).
- **Ask the person before pushing.** Committing locally is cheap and reversible; publishing is
  neither. Do not push on your own initiative.
- Never `git push --force`. Never rewrite history on `main`.
- If something is already broken live, fix forward with a new commit. Don't revert-and-force.

---

## Common tasks

### Add or edit a company / founder

Edit `captured/companies.json`. Copy the shape of an existing record exactly:

```json
{
  "name": "Ravi Mishra", "first": "Ravi", "last": "Mishra",
  "year": "'04", "title": "Co-Founder & CEO", "company": "Ample",
  "founded": "", "city": "",
  "sector_raw": "Cloud infrastructure for AI-native development",
  "sector": "AI", "sector_key": "ai",
  "stage_raw": "Micro round, pre-YC", "stage_group": "Pre-Seed",
  "invest": "$1-2M micro round", "investors": "Y Combinator, …",
  "slug": "ample", "tile": "assets/tiles/ample.png", "color": "#D55A2D",
  "bio": "Ravi Mishra is the Co-Founder and CEO of Ample, …",
  "linkedin": "https://www.linkedin.com/in/ravimishra/",
  "website": "https://ample.computer/", "page": "ample"
}
```

`sector_key` and `stage_group` **must** be one of these — inventing a new value creates a
filter category that silently matches nothing:

| `sector_key` | `sector` |
|---|---|
| `ai` | AI |
| `health` | Health & Bio |
| `fintech` | Fintech |
| `enterprise` | Enterprise/SaaS |
| `commerce` | Commerce/Consumer |
| `security` | Security |
| `media` | Media/Gaming |
| `energy` | Energy/Climate |
| `hardware` | Hardware/Deep-Tech |

`stage_group`: `Pre-Seed` · `Seed` · `Series A and Later` · `Acquired / IPO'd`

Then `python3 gen_site.py`. The roster entry and the detail page at
`public/companies/<page>.html` are both created automatically.

### Add or remove an investment

Edit the `INV = [...]` list near the top of `gen_site.py`. Each entry is
`(founder, year, company, sector label, description)`. Regenerate.

### Add a committee member

Edit `captured/committee.json` → `members`. Regenerate.

### Add someone's photo

Put the image in `public/assets/people/`, then add a `"Full Name": "assets/people/file.jpg"`
entry to `captured/photo_map.json`. People with no entry show an initials avatar — which is a
fine, deliberate fallback, not a bug.

### Change wording, layout or a page's structure

That text lives in `gen_site.py`, inside the Python string for that page. Edit it there and
regenerate. **Do not** edit the rendered HTML.

### Change colors, fonts or spacing

`public/css/styles.css`. Colors and fonts are CSS variables at the top under `:root` — change
them there, not at each use site. Then bump the `?v=` number on `styles.css` in `gen_site.py`
so browsers don't serve a cached copy, and regenerate.

---

## Verify before you push

```bash
python3 gen_site.py
python3 -m http.server 8747 --directory public
```

Open `http://localhost:8747/` and check:

- The page you changed looks right, and the browser console has no errors.
- The alumni filter still works: pick a sector, confirm the roster narrows and empty stage
  groups disappear.
- Mobile nav toggle works below 940px.
- `git status` shows changes only in files you intended, plus regenerated `public/` files.

---

## Things that break silently

These have all happened. None of them produce an error message.

- **Editing generated HTML.** Overwritten on the next `gen_site.py` run.
- **Inventing a `sector_key` or `stage_group`.** The company vanishes from filtered views.
- **Forgetting to run `gen_site.py`.** Your source edit is committed but the live site never
  changes, so it looks like the deploy failed.
- **Forgetting the `?v=` bump after a CSS/JS change.** Returning visitors keep the old file.
- **Adding a `_redirects` file.** GitHub Pages ignores that format entirely. Redirects are
  generated from `captured/redirects.txt` as real stub pages.
- **Committing media.** Never commit video or raw photos. `source-media/` and
  `public/assets/intro/_source/` are gitignored for this reason — git keeps binaries forever
  and they cannot be removed without rewriting history.
- **Hand-placing a logo with cut-out detail.** `scripts/tilegen.py` builds flat silhouettes
  from the alpha channel, so interior detail is lost (see the KOS tile). Such logos must be
  placed manually.

---

## Accuracy rules — these matter more than the code

This site makes public factual claims about **real people**: alumni, founders, investors, and
committee members, some of them students.

- **Never invent a fact.** Not a class year, not a company, not a funding round, not a title,
  not a LinkedIn URL. If it isn't in `captured/`, in a document the person gave you, or on the
  company's own site, **ask** — do not fill the gap with something plausible.
- A missing field rendering as blank is correct behavior. A wrong field is a published error
  about a real person.
- Never guess someone's pronouns or personal details.
- Don't add photos of people without the person's say-so, and never commit photos of students
  pulled from elsewhere.
- When you take a fact from a source, say which source in your commit message.

---

## Repo map

```
gen_site.py           the generator — page templates + the INV investments list
captured/             all content as JSON. THIS is what you edit
  companies.json        107 company/founder records → roster + detail pages
  founders.json         founder records
  committee.json        committee members and section blurbs
  photo_map.json        name → headshot path
  redirects.txt         old URL → new page (generates stub pages)
public/               GENERATED OUTPUT — the deployed site. Do not hand-edit
  css/styles.css        hand-written (exception)
  js/main.js            hand-written (exception)
scripts/              tilegen.py (company tiles), procphoto.py (headshots)
source-media/         raw photo/video source. gitignored, never deployed
.github/workflows/    pages-deploy.yml — publishes public/ on push to main
```

Further reading: **`BUILD.md`** for how-to detail, **`HANDOFF.md`** for project orientation,
**`MIGRATION.md`** for status and history.

---

## If you're unsure

Say so and ask. This is a live public site representing a real school program. An unanswered
question costs a message; a confidently wrong edit about a real person is published to the
world and may not be noticed for weeks.
