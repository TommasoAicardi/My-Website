# My-Website

Personal academic website for Tommaso Aicardi, PhD student at Bocconi University.
Built as a static Jekyll site and hosted on GitHub Pages at
https://tommasoaicardi.github.io/My-Website/

## Structure

```
_config.yml              Jekyll site config (title, baseurl)
_layouts/default.html    Base HTML shell: meta tags, theme-init script, CSS/JS includes
index.html               All page content: sidebar + Home/Research dashboard sections
assets/css/style.css     Styling, theme (light/dark) variables, responsive breakpoints
assets/js/main.js        Section nav toggle, dark/light theme toggle, papers list rendering
assets/data/papers.json  Published papers, auto-generated (see below) — don't edit by hand
assets/doc/              CV PDF, date-stamped filename, auto-synced (see below)
assets/img/               Profile photo
scripts/fetch_scholar.py  Scrapes Google Scholar into assets/data/papers.json
scripts/fetch_cv.sh       Pulls the CV PDF from the CV repo
.github/workflows/        Scheduled GitHub Actions running the two scripts above
```

## Layout

- **Sidebar** (left column): profile photo and contact info — always visible.
- **Dashboard** (main column): a header bar with Home/Research nav buttons and a
  dark/light theme toggle, plus the two content sections (only one shown at a
  time, no page reload):
  - **Home**: About Me, Research Interests.
  - **Research**: Published Papers (auto-synced), Datasets and Resources,
    Ongoing Projects.

## Automation

Two scheduled workflows keep content current without manual edits:

- **`update-papers.yml`** (weekly, Mondays) — runs `scripts/fetch_scholar.py`,
  which scrapes the Google Scholar profile via the `scholarly` package and
  writes `assets/data/papers.json`. If the scrape fails or returns nothing,
  the existing file is left untouched (no bad data ever gets committed).
- **`update-cv.yml`** (weekly, Tuesdays) — runs `scripts/fetch_cv.sh`, which
  pulls `main-eng.pdf` from the public `TommasoAicardi/CV` repo, republishes
  it as `assets/doc/TommasoAicardi_<date>.pdf`, removes the previous dated
  file, and rewrites the CV link in `index.html` to match.

Both workflows can also be triggered manually from the repo's **Actions** tab
(`workflow_dispatch`), and both commit their changes back to `master` directly.

## Local development

Requires Ruby + Jekyll (`gem install jekyll bundler`).

```
jekyll serve
```

Then open http://localhost:4000. Note that the live site is served under the
`/My-Website` path (see `baseurl` in `_config.yml`), so asset links are
root-relative to that subpath, not the domain root.
