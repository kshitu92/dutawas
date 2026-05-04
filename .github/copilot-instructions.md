# Copilot instructions for `dutawas`

## Build, test, and validation commands

| Task | Command |
| --- | --- |
| Install Ruby dependencies | `bundle install` |
| Build the site | `bundle exec jekyll build` |
| Run the full local test flow | `make test` |
| Run the Ruby test file directly | `bundle exec ruby test/test_site.rb` |
| Run a single test | `bundle exec ruby -Itest test/test_site.rb --name test_site_builds` |
| Serve locally | `make serve` or `bundle exec jekyll serve` |
| Run the CI-equivalent local check in Docker | `make ci-local` |
| Install Python deps for the scheduled update checker | `python -m pip install -r .github/scripts/requirements.txt` |
| Run the consulate update checker manually | `GITHUB_TOKEN=... GITHUB_REPOSITORY=kshitu92/dutawas python .github/scripts/check_updates.py` from `.github/scripts/` |

There is currently **no dedicated lint command** in this repository.

## High-level architecture

This repository is a **Jekyll site** using the `just-the-docs` theme. The published site is built from Markdown pages in the repository root (`index.md`, `about.md`, `consulates.md`) plus detailed consulate pages under `consulates/`. `_config.yml` controls the site-wide Jekyll behavior, including pretty permalinks, callouts, and theme settings.

Navigation is split across **front matter** and `_data/navigation.yml`. The page front matter controls titles, parents, child relationships, and permalinks, while `_data/navigation.yml` provides the menu structure used by the site. When adding or renaming a consulate page, keep both in sync.

The repository also has a separate **automation path** under `.github/scripts/` and `.github/workflows/`. GitHub Actions builds the Jekyll site on pushes and PRs, deploys `_site` to GitHub Pages from `main`, and runs a scheduled Python job that scrapes consulate websites and opens PRs with content updates. `config.py` is the source of truth for which consulates are monitored, which Markdown file each one updates, and which regex patterns are used to extract fields.

## Key conventions

- Consulate pages are expected to build to `consulates/<slug>/index.html`; the test suite currently asserts the slugs `washington-state`, `boston`, `new-york`, and `dallas`.
- Adding a new consulate usually requires coordinated edits in **multiple files**: the page in `consulates/`, the overview links in `consulates.md`, the menu in `_data/navigation.yml`, and the assertions in `test/test_site.rb`. If the page should be auto-monitored, also update `.github/scripts/config.py`.
- Keep the existing **section structure** on consulate pages (`Location and Contact Information`, `Services Provided`, `Jurisdiction`, `Important Information`, `Forms and Documents`, `Frequently Asked Questions`, `Sources`) unless there is a clear reason to change it. The content is intentionally documentation-oriented rather than blog-style.
- Preserve the emphasized field labels such as `*Address:*`, `*Phone:*`, `*Email:*`, and `*Office Hours:*` on auto-monitored pages. The update script rewrites those sections with regex-based replacements and is sensitive to that formatting.
- Maintain `permalink`, `parent`, `nav_order`, and `has_children` front-matter fields carefully. The site uses pretty permalinks, so link paths should match the front matter rather than raw filenames.
- The test suite includes a relaxed `HTMLProofer` run: it prints warnings without failing the suite. Do not assume the absence of test failures means all generated HTML is clean.
- This repository is a **community-maintained information site**, not an official embassy or consulate system. Content changes should preserve that tone and keep source citations / “Last checked” notes current on factual pages.
