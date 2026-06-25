# AI Skills Registry

A catalog of AI agent skills across Gates Foundation teams — publish skills here so the whole org can discover and use them.

**SharePoint:** [AI Skills Registry](https://bmgf.sharepoint.com/sites/AISkillsRegistry) → `Skill Registry` library

---

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env and fill in your values
```

> **Note:** `AZURE_CLIENT_ID` is required for `search_skills.py`. Contact the Skills Working Group (`#ai-skills` on Slack) to get the value.

---

## Finding Skills

### Option A: Browse on SharePoint

1. Go to [AI Skills Registry](https://bmgf.sharepoint.com/sites/AISkillsRegistry)
2. Open the **Skill Registry** document library
3. Each `.md` file is a skill — open one to see what it does and how to install it

You can also search within the library using SharePoint's search bar. Filter by keyword, team, or category.

### Option B: Browse the Skills Catalog Page

Visit the hosted skills catalog — a searchable, filterable page with install instructions for every skill:

**[AI Skills Registry — Skills Catalog](https://gatesfoundation.github.io/ai-skills-registry/)**

No login required. Use the search bar to filter by name, description, team, or category. Each card shows the skill's description and the exact commands to install it.

### Option C: Ask Claude Code

This requires the **Microsoft 365 MCP connector** in Claude Code. Set it up once:

1. Add this to your Claude Code settings at `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "Microsoft_365": {
      "type": "mcp-remote",
      "url": "https://mcp.claude.ai/mcp/connectors/microsoft-365"
    }
  }
}
```

2. Open Claude Code — it will prompt you to sign in with your GF Microsoft account the first time.

Once connected, you can ask Claude Code directly:

```
List all skills on SharePoint
```
```
Show me the skill card for audit-code
```
```
How do I install the idm-pkg-install skill?
```

---

## Reading a Skill Card

Each skill card is a Markdown file with a metadata table at the top:

| Field | What it means |
|---|---|
| **Team** | The team that owns and maintains this skill |
| **Category** | The type of work this skill helps with |
| **Plugin** | The plugin name used to install the skill in Claude Code |
| **Repo** | The GitHub repository where the skill lives |
| **Owner** | Contact email for questions or issues |
| **Version** | The skill version |

Below the table you'll find:
- A **Description** explaining what the skill does and when to use it
- **Installation instructions** for three methods (see below)
- **Links** to the full skill source on GitHub

---

## Installing a Skill in Claude Code

When you find a skill, the card gives you the **Plugin** name and **Repo**. Use those to install it.

### Option 1 — Claude Code Marketplace (recommended)

```
# Add the repo marketplace (first time only)
/plugin marketplace add <org>/<repo>

# Install the skill
/plugin install <plugin>@<marketplace-name>
```

Example — installing `audit-code` from the IDM standards catalog entry:
```
/plugin marketplace add InstituteforDiseaseModeling/idm_standards
/plugin install idm-standards@idm_standards
```

### Option 2 — Git Submodule

```bash
git submodule add https://github.com/<org>/<repo>.git .claude/skills/<repo>
```

Then add a reference in your project's `CLAUDE.md`:
```markdown
## Skills
- .claude/skills/<repo>/<path-to-SKILL.md>
```

### Option 3 — Clone the Repo

```bash
git clone https://github.com/<org>/<repo>.git
```

### Using the Skill

Once installed, open Claude Code in your project and ask naturally — the skill activates automatically when relevant:
```
Review my Python code in src/simulation.py
Help me set up this IDM package
Summarize this meeting transcript
```

---

## Publishing a Skill to the Registry

### Step 1 — Generate the catalog document

Pull skill files from a GitHub repo and generate catalog documents locally:

```powershell
python scripts/sync_to_local.py --repo <org>/<repo>
```

Example:
```powershell
python scripts/sync_to_local.py --repo InstituteforDiseaseModeling/idm_standards --output ./skill-idm-standards --clean
```

Catalog files land in `./skill-registry/` by default, or in the folder you specified with `--output`. Review them before uploading.

Optional flags:
- `--output <path>` — change the output folder
- `--clean` — clear the output folder before syncing

Set `GITHUB_TOKEN` in your environment if you hit GitHub API rate limits.

### Step 2 — Upload to SharePoint

Drag the generated `.md` files into the **Skill Registry** library on SharePoint:

**[AI Skills Registry](https://bmgf.sharepoint.com/sites/AISkillsRegistry)** → `Skill Registry`

No pipeline or credentials needed — just drag and drop.

---

## Questions?

Post in `#ai-skills` on Slack or contact the Skills Working Group.
