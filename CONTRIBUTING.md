# Contributing to Dutawas

Thank you for helping keep consulate information accurate for the Nepali community! There are several ways to contribute, and **you do not need to know how to code** for most of them.

## Report Outdated Information (No Coding Needed)

If you notice something wrong or outdated on the site:

1. Go to [github.com/kshitu92/dutawas/issues/new](https://github.com/kshitu92/dutawas/issues/new?template=outdated_info.md)
2. Select the **"Flag Outdated Information"** template
3. Fill in what is wrong and what the correct information is
4. Submit — a maintainer will review and update the site

You can also click the **"Help keep this page accurate"** link at the bottom of any consulate page.

## Suggest New Content (No Coding Needed)

Want to see a new consulate, service, or page added?

1. Go to [github.com/kshitu92/dutawas/issues/new](https://github.com/kshitu92/dutawas/issues/new?template=new_content.md)
2. Select the **"Suggest New Content"** template
3. Describe what you want added and why it would be useful
4. Include any source links if you have them

## Edit a Page Using GitHub's Web Editor (No Local Setup)

For small edits like fixing a typo or updating a phone number:

1. Navigate to the page's `.md` file in the [GitHub repository](https://github.com/kshitu92/dutawas)
   - Consulate pages are in the `consulates/` folder
2. Click the **pencil icon** (Edit this file) in the top right
3. Make your change
4. Click **"Propose changes"** at the bottom
5. Click **"Create pull request"**
6. A maintainer will review and merge your change

## Add a New Consulate Page

If you want to add a new consulate or embassy page:

### File naming

Create a new `.md` file in the `consulates/` folder. Use lowercase, hyphen-separated names:
- `consulates/washington-dc.md`
- `consulates/chicago.md`

### Required frontmatter

Every consulate page must start with:

```yaml
---
title: [Consulate Name]
layout: default
nav_order: [number]
parent: Consulates
permalink: /consulates/[slug]/
last_verified: [YYYY-MM-DD]
verified_by: [your_github_username]
---
```

### Required sections

Follow this structure (match existing pages):

1. **Location and Contact Information** — address, phone, email, office hours
2. **Services Provided** — bullet list
3. **Jurisdiction** — which states/areas this consulate serves
4. **Fee Schedule** — table format, with source
5. **Document Checklists** — checklist format for major services
6. **Appointment Booking** — how to schedule
7. **Important Information** — notable rules and tips
8. **Forms and Documents** — links to official forms
9. **Frequently Asked Questions** — Q&A format
10. **Sources** — official URLs with last-checked dates

### Content rules

- **Never invent information.** If you are not sure of a fee, phone number, or policy, write "Check with consulate for current information" rather than guessing.
- **Always include sources.** Every page must have a Sources section listing where information was verified and when.
- **Use official embassy/consulate websites** as primary sources (listed in the site's about page).

## Run the Site Locally (For Developers)

See the [README](README.md) for instructions on running the site locally with Jekyll.

Quick start:
```bash
git clone https://github.com/YOUR_USERNAME/dutawas.git
cd dutawas
bundle install
bundle exec jekyll serve
# Open http://localhost:4000
```

## Pull Request Checklist

Before submitting a PR, confirm:

- [ ] Information is accurate and sourced from official websites
- [ ] Sources section is included with last-checked dates
- [ ] Page follows the existing structure and formatting style
- [ ] Frontmatter includes `last_verified` and `verified_by` fields
- [ ] No broken links
- [ ] Fees say "Check with consulate" if you are not 100% certain
- [ ] PR description explains what changed and why

## Questions?

Open an issue or reach out to the maintainer [@kshitu92](https://github.com/kshitu92).
