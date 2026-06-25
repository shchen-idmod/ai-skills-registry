# audit-code

| Field | Value |
|---|---|
| **Team** | IDM |
| **Category** | Audit Code |
| **Plugin** | idm-standards |
| **Repo** | idm_standards |
| **Owner** | IDM |
| **Version** | Unknown |

## Description

The Audit-Code skill scores a software project against IDM engineering quality tiers (1–3) across quality, usability, and safety metrics, and writes a code_audit.md report. Use this skill when the user asks to "audit my code", "score my project", "check engineering quality", "evaluate code quality", "assess tier compliance", or invokes /idm-standards:audit-code. Also use proactively when the user says "how good is this code?" or "what improvements does this project need?". For R projects, this skill routes to audit-r-code.

---

## How to Use This Skill

> This catalog entry is for **discovery only**.
> To use this skill, install it from the original repository using one of the methods below.

### Option 1 — Claude Code Marketplace
```
# Add the repo marketplace (first time only)
/plugin marketplace add InstituteforDiseaseModeling/idm_standards

# Install this skill
/plugin install idm-standards@idm-standards
```

### Option 2 — Git Submodule
```bash
git submodule add https://github.com/InstituteforDiseaseModeling/idm_standards.git .claude/skills/idm_standards
```
Then reference the skill in your `CLAUDE.md`:
```markdown
## Skills
- .claude/skills/idm_standards/idm_standards_plugin/skills/audit-code/SKILL.md
```

### Option 3 — Clone the Repo
```bash
git clone https://github.com/InstituteforDiseaseModeling/idm_standards.git
```

---

## Links

- [View full SKILL.md on GitHub](https://github.com/InstituteforDiseaseModeling/idm_standards/blob/main/idm_standards_plugin/skills/audit-code/SKILL.md)
- [View repository](https://github.com/InstituteforDiseaseModeling/idm_standards)
