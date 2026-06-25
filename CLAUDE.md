# AI Skills Registry

## Searching for Skills on SharePoint

When the user asks you to find, search, or browse skills:

- **Primary approach:** Read the "Skill Registry" library root directly using the known drive ID — this works immediately and does not depend on search indexing:
  ```
  read_resource: file:///b!s_UnY7EY5kK_H0cj3PNmwKjr_msK3JVLmvOxnaIosnXdSB7sWaeLSrhuRA939lGH/root
  ```
  Then read each file URI returned to get full skill details.

- **Fallback (if drive read fails):** Use the SharePoint search tool (Microsoft 365 MCP connector), restricted to this site and library only:
  - **Site:** `https://bmgf.sharepoint.com/sites/AISkillsRegistry`
  - **Library:** `Skill Registry`
  - Search with `fileType: md` to target skill cards

Do not use Glean or broad SharePoint search — it is too slow and returns unrelated results.

> **Note:** SharePoint search indexes new files with a delay (5–30 min). The direct drive read above bypasses this and always reflects the current state of the library.
