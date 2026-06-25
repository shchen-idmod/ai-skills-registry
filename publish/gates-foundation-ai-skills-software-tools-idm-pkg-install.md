# idm-pkg-install

| Field | Value |
|---|---|
| **Team** | Gates Foundation AI Skills |
| **Category** | Software Tools |
| **Plugin** | idm-skills |
| **Repo** | gf-agent-skills |
| **Owner** | gf-ai-skills@gatesfoundation.org |
| **Version** | "1.0.0" |

## Description

Use this skill when installing, setting up, or troubleshooting any IDM package or repository. Triggers include: installing a released IDM package from PyPI, setting up an IDM project environment from a GitHub repo or local path, running pip install or conda install against an IDM codebase, resolving dependency conflicts in scientific Python environments, or any request like 'install emodpy', 'install this repo', 'set up the environment for', or 'get this running'. Use this skill before writing any install commands - it determines the correct source, strategy, and mode based on what the user wants.

---

## How to Use This Skill

> This catalog entry is for **discovery only**.
> To use this skill, install it from the original repository using one of the methods below.

### Option 1 — Claude Code Marketplace
```
# Add the repo marketplace (first time only)
/plugin marketplace add shchen-idmod/gf-agent-skills

# Install this skill
/plugin install idm-skills@gf-foundation-skills
```

### Option 2 — Git Submodule
```bash
git submodule add https://github.com/shchen-idmod/gf-agent-skills.git .claude/skills/gf-agent-skills
```
Then reference the skill in your `CLAUDE.md`:
```markdown
## Skills
- .claude/skills/gf-agent-skills/groups/idm/skills/software-tools/idm-pkg-install/SKILL.md
```

### Option 3 — Clone the Repo
```bash
git clone https://github.com/shchen-idmod/gf-agent-skills.git
```

---

## Links

- [View full SKILL.md on GitHub](https://github.com/shchen-idmod/gf-agent-skills/blob/main/groups/idm/skills/software-tools/idm-pkg-install/SKILL.md)
- [View repository](https://github.com/shchen-idmod/gf-agent-skills)
