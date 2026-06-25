#!/usr/bin/env python3
"""
search_skills.py — Search the SharePoint Skill Registry for existing skills.

Authenticates using your GF Microsoft account (no shared secrets needed).
A browser window will open on first run to log you in.

Usage:
    python scripts/search_skills.py --query "code review"
    python scripts/search_skills.py --team idm
    python scripts/search_skills.py --category "software tools"
    python scripts/search_skills.py --query "python" --team idm
    python scripts/search_skills.py --all
    python scripts/search_skills.py --summary

Required environment variable (or set in .env):
    SHAREPOINT_SITE_URL    e.g. https://bmgf.sharepoint.com/sites/AISkillsRegistry

Optional environment variable:
    SKILL_LIBRARY_NAME     SharePoint document library name (default: Skill Registry)
    AZURE_CLIENT_ID        Azure app client ID (has a default set by your org)
"""

import argparse
import os
import sys
from pathlib import Path

# Load .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional

try:
    from azure.identity import InteractiveBrowserCredential
    from office365.runtime.auth.token_response import TokenResponse
    from office365.sharepoint.client_context import ClientContext
except ImportError:
    print("Error: Missing required packages.")
    print("Run: pip install azure-identity office365-REST-Python-Client")
    sys.exit(1)


# ── Config ────────────────────────────────────────────────────────────────────

# This is the Azure App Registration CLIENT ID for the AI Skills Registry.
# It is not a secret — it is safe to check into the repo.
# Contact the Skills Working Group if you need this value.
AZURE_CLIENT_ID = os.environ.get("AZURE_CLIENT_ID", "")
if not AZURE_CLIENT_ID:
    print("Error: AZURE_CLIENT_ID is not set.")
    print("Contact the Skills Working Group (#ai-skills on Slack) to get the value,")
    print("then add it to your .env file as AZURE_CLIENT_ID=<value>.")
    sys.exit(1)

SHAREPOINT_SITE_URL = os.environ.get(
    "SHAREPOINT_SITE_URL",
    "https://bmgf.sharepoint.com/sites/AISkillsRegistry"
)
SKILL_LIBRARY_NAME = os.environ.get("SKILL_LIBRARY_NAME", "Skill Registry")

# SharePoint permission scope
SHAREPOINT_SCOPE = "https://bmgf.sharepoint.com/.default"


# ── Auth ──────────────────────────────────────────────────────────────────────

def get_sharepoint_context() -> ClientContext:
    """
    Authenticate using the user's GF Microsoft account.
    Opens a browser window on first run — subsequent runs use a cached token.
    """
    print("Authenticating with your GF Microsoft account...")
    print("(A browser window will open if this is your first time)")

    credential = InteractiveBrowserCredential(
        client_id=AZURE_CLIENT_ID,
    )

    def acquire_token():
        token = credential.get_token(SHAREPOINT_SCOPE)
        return TokenResponse(**{"access_token": token.token, "token_type": "Bearer"})

    ctx = ClientContext(SHAREPOINT_SITE_URL).with_access_token(acquire_token)
    ctx.load(ctx.web)
    ctx.execute_query()
    print(f"Connected as: {ctx.web.current_user.login_name if hasattr(ctx.web, 'current_user') else 'GF user'}\n")
    return ctx


# ── Search ────────────────────────────────────────────────────────────────────

def fetch_all_skills(ctx: ClientContext) -> list[dict]:
    """Fetch all catalog entries from the SharePoint document library."""
    library = ctx.web.lists.get_by_title(SKILL_LIBRARY_NAME)
    items = library.items.select([
        "Id",
        "FileLeafRef",
        "Title",
        "SkillName",
        "RepoName",
        "Team",
        "Category",
        "Description",
        "Owner",
        "Version",
        "GitHubURL",
        "SkillPath",
    ]).get().execute_query()

    return [item.properties for item in items]


def filter_skills(
    skills: list[dict],
    query: str = None,
    team: str = None,
    category: str = None
) -> list[dict]:
    results = skills

    if team:
        results = [
            s for s in results
            if team.lower() in (s.get("Team") or "").lower()
        ]

    if category:
        results = [
            s for s in results
            if category.lower() in (s.get("Category") or "").lower()
        ]

    if query:
        query_lower = query.lower()
        results = [
            s for s in results
            if (
                query_lower in (s.get("SkillName") or "").lower()
                or query_lower in (s.get("Description") or "").lower()
                or query_lower in (s.get("Category") or "").lower()
                or query_lower in (s.get("RepoName") or "").lower()
                or query_lower in (s.get("FileLeafRef") or "").lower()
            )
        ]

    return results


def print_results(
    skills: list[dict],
    query: str = None,
    team: str = None,
    category: str = None
):
    filters = []
    if query:
        filters.append(f"query='{query}'")
    if team:
        filters.append(f"team='{team}'")
    if category:
        filters.append(f"category='{category}'")
    filter_str = ", ".join(filters) if filters else "none (showing all)"

    print(f"Search filters: {filter_str}")
    print(f"Results: {len(skills)} skill(s) found\n")

    if not skills:
        print("No matching skills found.")
        print("You may want to create a new one and contribute it back!")
        return

    print("-" * 70)
    for skill in skills:
        name = skill.get("SkillName") or skill.get("Title", "Unknown")
        repo = skill.get("RepoName", "Unknown")
        plugin = skill.get("Plugin", "Unknown")

        print(f"  Skill:       {name}")
        print(f"  Team:        {skill.get('Team', 'Unknown')}")
        print(f"  Category:    {skill.get('Category', 'Unknown')}")
        print(f"  Description: {skill.get('Description', 'No description')}")
        print(f"  Owner:       {skill.get('Owner', 'Unknown')}")
        print(f"  Version:     {skill.get('Version', 'Unknown')}")
        if skill.get("GitHubURL"):
            print(f"  GitHub:      {skill.get('GitHubURL')}")
        print(f"\n  To install:")
        print(f"    /plugin marketplace add <org>/{repo}")
        print(f"    /plugin install {plugin}@{repo}")
        print("-" * 70)


def print_summary(skills: list[dict]):
    teams = sorted(set(s.get("Team", "Unknown") for s in skills))
    categories = sorted(set(s.get("Category", "Unknown") for s in skills))
    print(f"Total skills in registry: {len(skills)}")
    print(f"\nTeams ({len(teams)}):      {', '.join(teams)}")
    print(f"Categories ({len(categories)}): {', '.join(categories)}")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Search the GF AI Skills Registry on SharePoint."
    )
    parser.add_argument("--query", "-q", help="Search by keyword")
    parser.add_argument("--team", "-t", help="Filter by team (e.g. idm, global-health)")
    parser.add_argument("--category", "-c", help="Filter by category (e.g. 'software tools')")
    parser.add_argument("--all", "-a", action="store_true", help="List all skills")
    parser.add_argument("--summary", action="store_true", help="Show summary of teams and categories")
    args = parser.parse_args()

    if not any([args.query, args.team, args.category, args.all, args.summary]):
        parser.print_help()
        sys.exit(0)

    ctx = get_sharepoint_context()

    print(f"Fetching skills from '{SKILL_LIBRARY_NAME}'...")
    all_skills = fetch_all_skills(ctx)

    if args.summary:
        print_summary(all_skills)
        return

    filtered = filter_skills(
        all_skills,
        query=args.query,
        team=args.team,
        category=args.category,
    )

    print_results(filtered, query=args.query, team=args.team, category=args.category)


if __name__ == "__main__":
    main()
