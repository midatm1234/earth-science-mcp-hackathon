# Claude Code project instructions

@AGENTS.md

## Claude Code specifics

- MCP servers for this project are defined in `.mcp.json`: `obs-model-starter` (local stdio via `uv`) and `earthdata` (public NASA Earthdata MCP over HTTPS). Their tools appear as `mcp__obs-model-starter__<tool>` and `mcp__earthdata__<tool>`.
- Skills are installed from `skills/` into `.claude/skills/` with `uv run python scripts/install_skills.py`. If a skill is missing, suggest that command instead of recreating the skill.
- When answering scientific questions with the starter tools, follow the `obs-model-comparison` skill: check metadata first, report units, valid pairs, exclusions, provenance (the data are synthetic) and limitations, and show the tool trace.
- Earthdata tools are for metadata discovery only. Do not download data or ask for Earthdata credentials during the workshop.
- After changing a server, remind the user to restart the Claude Code session so the server reloads.
