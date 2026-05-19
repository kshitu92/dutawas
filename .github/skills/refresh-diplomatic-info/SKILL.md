---
name: refresh-diplomatic-info
description: "Research and update embassy and consulate pages in this repository using the page's existing source links first, then additional official sources when needed. Use when asked to refresh mission information, verify contact details, or update source-backed diplomatic service content."
license: MIT
---

# Refresh diplomatic mission information

Use this skill when updating embassy or consulate content in this repository.

## Workflow

1. Start from the existing page content. Collect the current official links from:
   - the page's `## Sources` section
   - inline `Website:` links
2. Re-check those links first. If they are incomplete, outdated, or broken, search for additional **official** sources such as:
   - `*.gov.np` mission pages
   - official consulate or embassy domains already linked from the page
   - official application or appointment portals directly referenced by the mission
3. Update the page with only **verifiable** changes. Prefer exact facts over paraphrase for:
   - address, phone, email, office hours
   - services currently offered
   - jurisdiction / supported states
   - appointment or submission requirements
   - official resource links
4. Preserve repository structure and page formatting:
    - keep front matter, permalink, and parent/nav fields intact unless the information architecture itself is changing
    - keep the existing section layout and factual tone
    - preserve emphasized labels like `*Address:*`, `*Phone:*`, `*Email:*`, and `*Office Hours:*` on pages that use them
5. Refresh the `## Sources` section so it reflects the links actually used, and update month/year “Last checked” notes when facts change.
6. If official sources conflict, prefer the most direct and most recently updated official source. Call out uncertainty plainly instead of guessing.
7. Do not invent missing data. If a page does not exist for a mission, only create one when the user explicitly asks for a new page.

## Repository-specific rules

- Most mission pages live under `consulates/*.md`.
- Mission updates often require related edits outside the page itself; check the [update playbook](references/update-playbook.md).
- After changing mission content, run the repository build/test flow:
  - `bundle exec jekyll build`
  - `bundle exec ruby test/test_site.rb`

## Use this skill well

- Prefer official sources for cited facts.
- Use third-party search results only to discover official pages, not as the final authority.
- Keep community-maintained disclaimers and source attribution intact.

## Reference

- [Mission update playbook](references/update-playbook.md)
