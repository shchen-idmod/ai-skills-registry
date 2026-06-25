# Contributing

There are two ways to contribute:

1. **Publish your skills** — add your team's skills to the registry so others can discover them (most common)
2. **Improve the registry** — fix bugs or add features to the tooling in this repo

---

## Contributing Code to This Registry

If you find a bug or want to improve the sync scripts, evals tooling, or documentation:

1. Fork or clone this repo
2. Create a branch: `git checkout -b fix/your-change`
3. Make your changes and test locally (see **Local Setup** below)
4. Open a pull request with a clear description of what changed and why

For larger changes, open an issue first to discuss the approach with the Skills Working Group.

---

## Publishing Your Skills

This guide explains how to publish skills from your repo to the AI Skills Registry so others across GF can discover and use them. Publishing to SharePoint is the primary workflow this registry supports.

---

## What Gets Published

Each `SKILL.md` file in your repo becomes a **catalog entry** in SharePoint. The catalog entry contains:
- Skill name, description, team, category
- Plugin and repo name
- Install instructions pointing back to your repo

The actual skill content stays in your repo — SharePoint is for **discovery only**.

---

## Requirements

Your `SKILL.md` files must have valid frontmatter:

```yaml
---
name: python-code-reviewer
description: Reviews Python code following IDM standards.
owner: idm-team
version: 1.0.0
---
```

| Field | Required | Description |
|---|---|---|
| `name` | Yes | Unique skill name, lowercase with hyphens |
| `description` | Yes | One sentence explaining what the skill does |
| `owner` | Yes | Team or person responsible for the skill |
| `version` | Yes | Semantic version e.g. `1.0.0` |

See `sharon-skills/` and `skill-idm-standards/` in this repo for working examples.

---

## Local Setup

Before testing the sync scripts, set up your environment:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

> **Note:** `SHAREPOINT_CLIENT_ID`, `SHAREPOINT_CLIENT_SECRET`, and `SHAREPOINT_TENANT_ID` are secrets — never commit them. Contact the Skills Working Group to get these credentials.

---

## Publishing Steps

### Step 1 — Copy the sync script
Copy `scripts/sync_to_sharepoint.py` from this repo into your repo's `scripts/` folder.

### Step 2 — Add the GitHub Actions workflow
Create `.github/workflows/sync-to-sharepoint.yml` in your repo:

```yaml
name: Sync Skills to SharePoint

on:
  push:
    branches:
      - main
    paths:
      - '**/SKILL.md'

  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install office365-REST-Python-Client
      - name: Sync skills to SharePoint
        run: python scripts/sync_to_sharepoint.py
        env:
          SHAREPOINT_SITE_URL: ${{ secrets.SHAREPOINT_SITE_URL }}
          SHAREPOINT_CLIENT_ID: ${{ secrets.SHAREPOINT_CLIENT_ID }}
          SHAREPOINT_CLIENT_SECRET: ${{ secrets.SHAREPOINT_CLIENT_SECRET }}
          SHAREPOINT_TENANT_ID: ${{ secrets.SHAREPOINT_TENANT_ID }}
          SKILL_LIBRARY_NAME: "Skill Registry"
```

### Step 3 — Add GitHub secrets
In your repo go to **Settings → Secrets and variables → Actions** and add:
- `SHAREPOINT_SITE_URL`
- `SHAREPOINT_CLIENT_ID`
- `SHAREPOINT_CLIENT_SECRET`
- `SHAREPOINT_TENANT_ID`

Contact the Skills Working Group to get these credentials.

### Step 4 — Test locally
```bash
python scripts/sync_to_local.py --repo <org>/<repo> --output ./skill-registry
```
Check the `skill-registry/` folder to verify the catalog entries look correct before pushing.

### Step 5 — Push to main
Once merged to main, the workflow runs automatically whenever a `SKILL.md` changes. Your skills will appear in the SharePoint registry within minutes.

---

## Updating a Skill

Just update your `SKILL.md` and push to main — the workflow automatically updates the SharePoint catalog entry.

## Removing a Skill

Contact the Skills Working Group to remove a catalog entry from SharePoint.

---

## Questions?

Contact the Skills Working Group or post in the `#ai-skills` Slack channel.
