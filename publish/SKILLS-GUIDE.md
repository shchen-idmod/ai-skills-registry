# How to Use the AI Skills Registry

This guide explains how to find AI agent skills, understand what they do, and install them in Claude Code.

---

## What Is a Skill?

A **skill** is a packaged set of instructions that gives Claude Code specialized knowledge for a specific task — like reviewing disease models, writing grant proposals, or installing IDM packages. Skills activate automatically when you describe your task in natural language.

---

## Step 1 — Find a Skill

You're already here! Browse the **Skill Registry** library on this SharePoint site. Each `.md` file is one skill.

Open any file to see what it does and whether it fits your need.

---

## Step 2 — Read the Skill Card

Each skill card has a metadata table at the top:

| Field | What it means |
|---|---|
| **Team** | The team that owns and maintains this skill |
| **Category** | The type of work this skill helps with |
| **Plugin** | The plugin name used to install it in Claude Code |
| **Repo** | The GitHub repository where the skill lives |
| **Owner** | Contact email for questions or issues |
| **Version** | The skill version |

The **Description** section tells you exactly when and how to use the skill, including example trigger phrases.

---

## Step 3 — Install the Skill in Claude Code

The skill card includes installation instructions. There are three ways to install:

### Option 1 — Claude Code Marketplace (recommended)

Run these commands inside Claude Code:

```
# Add the repo marketplace (first time only)
/plugin marketplace add <org>/<repo>

# Install the skill
/plugin install <plugin>@<marketplace-name>
```

The exact commands are in the skill card — just copy and paste them.

### Option 2 — Git Submodule

```bash
git submodule add https://github.com/<org>/<repo>.git .claude/skills/<repo>
```

Then reference the skill in your project's `CLAUDE.md`:
```markdown
## Skills
- .claude/skills/<repo>/<path-to-SKILL.md>
```

### Option 3 — Clone the Repo

```bash
git clone https://github.com/<org>/<repo>.git
```

---

## Step 4 — Use the Skill

Once installed, open Claude Code in your project and describe your task naturally. The skill activates automatically:

```
Review my Python code in src/simulation.py
Help me set up this IDM package
Summarize this meeting transcript
Audit my project for code quality
```

You don't need to type a special command — Claude detects when a skill applies.

---

## Want to Publish Your Own Skill?

If your team has built a skill and wants to share it with the org, see the [AI Skills Registry README on GitHub](https://github.com/shchen-idmod/ai-skills-registry) for publishing instructions.

---

## Questions?

Post in `#ai-skills` on Slack or contact the Skills Working Group.
