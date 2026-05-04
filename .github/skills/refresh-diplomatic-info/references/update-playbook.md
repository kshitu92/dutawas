# Mission update playbook

## Source priority

1. Existing links already present on the page.
2. Official Nepal mission pages and `mofa.gov.np` pages.
3. Official mission-owned domains already used in this repo, such as:
   - `nyc.nepalconsulate.gov.np`
   - `dls.nepalconsulate.gov.np`
   - `nepalconsulate.org`
4. Official application / appointment portals linked from those mission pages.

Do not rely on aggregator sites, business listings, or social posts for factual updates unless they only help you discover the official source.

## Page shape to preserve

Most detailed mission pages follow this structure:

1. `## Location and Contact Information`
2. `## Services Provided`
3. `## Jurisdiction`
4. `## Important Information`
5. `## Forms and Documents`
6. `## Frequently Asked Questions`
7. `## Sources`

Boston is a special case: it currently documents that there is no established consulate and routes users to New York. Verify that status before changing the page shape.

## Repo touchpoints to check

- `consulates/<slug>.md`: primary mission content
- `consulates.md`: overview links
- `_data/navigation.yml`: navigation entries
- `test/test_site.rb`: expected generated pages

If you rename a mission slug or add a new page, update all affected touchpoints together.

## Editing rules

- Preserve front matter unless the information architecture is intentionally changing.
- Keep links aligned with `permalink` values, not raw filenames.
- Keep factual copy concise and citation-backed.
- If a field is no longer published by an official source, say so explicitly instead of guessing.
- When a key fact changes, update the corresponding source note and “Last checked” month/year in the page.
