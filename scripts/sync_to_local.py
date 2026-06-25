#!/usr/bin/env python3
"""
sync_to_local.py — Sync SKILL.md files from a GitHub repo to a local folder as catalog entries.

Fetches SKILL.md files and marketplace.json directly from a remote GitHub repo via the GitHub API.
Each skill becomes a short catalog document with metadata and install instructions.
The actual skill content stays in the source repo — SharePoint is for discovery only.

Usage:
    python scripts/sync_to_local.py --repo InstituteforDiseaseModeling/idm_standards
    python scripts/sync_to_local.py --repo InstituteforDiseaseModeling/idm_standards --output ./skill-registry
    python scripts/sync_to_local.py --repo InstituteforDiseaseModeling/idm_standards --clean

Required:
    --repo    GitHub repo in the format <org>/<repo>

Optional environment variables:
    GITHUB_TOKEN      GitHub personal access token (increases API rate limit)
    GITHUB_SERVER_URL e.g. https://github.com (default: https://github.com)
"""

import argparse
import base64
import json
import os
import re
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

import yaml


# ── Config ────────────────────────────────────────────────────────────────────

GITHUB_SERVER_URL = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

DEFAULT_OUTPUT_DIR = "./skill-registry"


# ── GitHub API ────────────────────────────────────────────────────────────────

def github_api_request(url: str) -> dict | list | None:
    """Make a GitHub API request. Returns None if 404."""
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if GITHUB_TOKEN:
        req.add_header("Authorization", f"Bearer {GITHUB_TOKEN}")
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        if e.code == 403:
            print("Error: GitHub API rate limit hit. Set GITHUB_TOKEN env var to increase the limit.")
            sys.exit(1)
        print(f"Error: GitHub API returned {e.code}: {e.reason}")
        sys.exit(1)


def fetch_file_content(repo: str, path: str, branch: str) -> str | None:
    """Fetch content of a single file from GitHub. Returns None if not found."""
    data = github_api_request(
        f"https://api.github.com/repos/{repo}/contents/{path}?ref={branch}"
    )
    if data is None:
        return None
    return base64.b64decode(data["content"]).decode("utf-8")


def fetch_marketplace_json(repo: str, branch: str) -> dict | None:
    """
    Find and parse marketplace.json from the repo.
    Searches common locations: root, .claude-plugin/, marketplace.json
    """
    candidate_paths = [
        "marketplace.json",
        ".claude-plugin/marketplace.json",
        ".claude/marketplace.json",
    ]
    for path in candidate_paths:
        content = fetch_file_content(repo, path, branch)
        if content:
            try:
                print(f"  Found marketplace.json at: {path}")
                return json.loads(content)
            except json.JSONDecodeError:
                continue
    return None


def find_skill_files_from_github(repo: str) -> tuple[list[tuple[str, str]], dict]:
    """
    Find all SKILL.md files in a remote GitHub repo using the Git Trees API.
    Also fetches marketplace.json for plugin/team metadata.
    Returns:
        - list of (path, content) tuples for each SKILL.md
        - marketplace dict (empty if not found)
    """
    print(f"Fetching skill files from GitHub: {repo}")

    # Get default branch
    repo_info = github_api_request(f"https://api.github.com/repos/{repo}")
    branch = repo_info.get("default_branch", "main")

    # Fetch marketplace.json for plugin/team metadata
    marketplace = fetch_marketplace_json(repo, branch) or {}

    # Get full file tree recursively
    tree_data = github_api_request(
        f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"
    )

    # Filter to SKILL.md files only
    skill_paths = [
        item["path"] for item in tree_data.get("tree", [])
        if item["type"] == "blob" and item["path"].endswith("SKILL.md")
    ]

    if not skill_paths:
        print(f"  No SKILL.md files found in {repo}")
        return [], marketplace

    print(f"  Found {len(skill_paths)} SKILL.md file(s)")

    # Fetch content of each SKILL.md
    results = []
    for skill_path in skill_paths:
        print(f"  Fetching: {skill_path}")
        content = fetch_file_content(repo, skill_path, branch)
        if content:
            results.append((skill_path, content))

    return results, marketplace


# ── Marketplace Helpers ───────────────────────────────────────────────────────

def extract_plugin_from_marketplace(marketplace: dict, skill_path: str) -> str:
    """
    Find the plugin name from marketplace.json that owns this skill path.
    Matches by checking if the skill path starts with the plugin source path.
    """
    for plugin in marketplace.get("plugins", []):
        source = plugin.get("source", "").lstrip("./")
        if skill_path.startswith(source):
            return plugin.get("name", "Unknown")
    # Fallback: use top-level marketplace name
    return marketplace.get("name", "Unknown")


def extract_team_from_marketplace(marketplace: dict) -> str:
    """Extract team/owner name from marketplace.json."""
    owner = marketplace.get("owner", {})
    if isinstance(owner, dict):
        return owner.get("name", "Unknown")
    if isinstance(owner, str):
        return owner
    return "Unknown"


# ── Path Helpers (fallback if no marketplace.json) ───────────────────────────
# Expected repo structure for path-based extraction:
#   groups/<team-name>/skills/<category-name>/<skill-name>/SKILL.md
#   foundation-wide/skills/<category-name>/<skill-name>/SKILL.md

def extract_team_from_path(skill_path: str) -> str:
    parts = Path(skill_path).parts
    if "groups" in parts:
        idx = parts.index("groups")
        if idx + 1 < len(parts):
            return parts[idx + 1].replace("-", " ").title()
    if "foundation-wide" in parts:
        return "Foundation-Wide"
    return "Unknown"


def extract_category_from_path(skill_path: str) -> str:
    parts = Path(skill_path).parts
    if "skills" in parts:
        idx = parts.index("skills")
        if idx + 1 < len(parts):
            return parts[idx + 1].replace("-", " ").title()
    # Fallback: use parent folder name
    return Path(skill_path).parent.parent.name.replace("-", " ").title()


# ── Helpers ───────────────────────────────────────────────────────────────────

def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from a SKILL.md file."""
    pattern = r"^---[ \t]*\n(.*?)\n---[ \t]*\n"
    match = re.match(pattern, content, re.DOTALL)
    if not match:
        return {}
    try:
        parsed = yaml.safe_load(match.group(1))
        return parsed if isinstance(parsed, dict) else {}
    except yaml.YAMLError:
        return {}

def build_github_url(repo: str, skill_path: str, branch: str = "main") -> str:
    return f"{GITHUB_SERVER_URL}/{repo}/blob/{branch}/{skill_path}"


def build_repo_url(repo: str) -> str:
    return f"{GITHUB_SERVER_URL}/{repo}"


def build_document_filename(skill_path: str, frontmatter: dict, team: str, category: str) -> str:
    """Format: <team>-<category>-<skill-name>.md"""
    team_slug = team.lower().replace(" ", "-")
    category_slug = category.lower().replace(" ", "-")
    skill_name = frontmatter.get("name") or Path(skill_path).parent.name
    return f"{team_slug}-{category_slug}-{skill_name}.md"


def build_catalog_entry(
    repo: str,
    skill_path: str,
    frontmatter: dict,
    marketplace: dict,
) -> str:
    """
    Build a short catalog entry pointing users to the original repo.
    Uses marketplace.json for plugin/team metadata when available.
    """
    skill_name = frontmatter.get("name") or Path(skill_path).parent.name
    team = extract_team_from_marketplace(marketplace) if marketplace else extract_team_from_path(skill_path)
    category = extract_category_from_path(skill_path)
    plugin = extract_plugin_from_marketplace(marketplace, skill_path) if marketplace else "Unknown"
    repo_name = repo.split("/")[-1]
    marketplace_name = marketplace.get("name", repo_name) if marketplace else repo_name
    repo_url = build_repo_url(repo)
    github_url = build_github_url(repo, skill_path)
    description = frontmatter.get("description", "No description provided.").strip()
    owner = frontmatter.get("owner", marketplace.get("owner", {}).get("name", "Unknown") if marketplace else "Unknown")
    version = frontmatter.get("version", "Unknown")

    return f"""# {skill_name}

| Field | Value |
|---|---|
| **Team** | {team} |
| **Category** | {category} |
| **Plugin** | {plugin} |
| **Repo** | {repo_name} |
| **Owner** | {owner} |
| **Version** | {version} |

## Description

{description}

---

## How to Use This Skill

> This catalog entry is for **discovery only**.
> To use this skill, install it from the original repository using one of the methods below.

### Option 1 — Claude Code Marketplace
```
# Add the repo marketplace (first time only)
/plugin marketplace add {repo}

# Install this skill
/plugin install {plugin}@{marketplace_name}
```

### Option 2 — Git Submodule
```bash
git submodule add {repo_url}.git .claude/skills/{repo_name}
```
Then reference the skill in your `CLAUDE.md`:
```markdown
## Skills
- .claude/skills/{repo_name}/{skill_path}
```

### Option 3 — Clone the Repo
```bash
git clone {repo_url}.git
```

---

## Links

- [View full SKILL.md on GitHub]({github_url})
- [View repository]({repo_url})
"""


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Sync SKILL.md files from a GitHub repo to a local catalog folder."
    )
    parser.add_argument(
        "--repo", "-r",
        required=True,
        help="GitHub repo in <org>/<repo> format (e.g. InstituteforDiseaseModeling/idmtools)"
    )
    parser.add_argument(
        "--output", "-o",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output folder path (default: {DEFAULT_OUTPUT_DIR})"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clear the output folder before syncing"
    )
    args = parser.parse_args()

    output_dir = Path(args.output)

    if args.clean and output_dir.exists():
        shutil.rmtree(output_dir)
        print(f"Cleared output folder: {output_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output folder: {output_dir.resolve()}\n")

    # Fetch skill files and marketplace.json from GitHub
    skill_files, marketplace = find_skill_files_from_github(args.repo)
    if not skill_files:
        print("Nothing to sync.")
        sys.exit(0)

    if marketplace:
        team = extract_team_from_marketplace(marketplace)
        print(f"  Marketplace: {marketplace.get('name', 'Unknown')} (Team: {team})")

    print("\nSyncing skills...")
    synced = 0
    skipped = 0

    for skill_path, content in skill_files:
        print(f"\nProcessing: {skill_path}")
        frontmatter = parse_frontmatter(content)

        name = frontmatter.get("name") or Path(skill_path).parent.name
        if not name:
            print(f"  Skipping — no name found")
            skipped += 1
            continue

        team = extract_team_from_marketplace(marketplace) if marketplace else extract_team_from_path(skill_path)
        category = extract_category_from_path(skill_path)

        filename = build_document_filename(skill_path, frontmatter, team, category)
        catalog_content = build_catalog_entry(args.repo, skill_path, frontmatter, marketplace)

        out_path = output_dir / filename
        existed = out_path.exists()
        out_path.write_text(catalog_content, encoding="utf-8")

        print(f"  {'Updated' if existed else 'Created'}: {out_path}")
        synced += 1

    print(f"\nDone. Synced: {synced}, Skipped: {skipped}")
    print(f"Output folder: {output_dir.resolve()}")


if __name__ == "__main__":
    main()