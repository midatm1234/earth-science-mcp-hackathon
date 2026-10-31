# Skills

Canonical source of every agent skill in this repository. Each folder is an [Agent Skills](https://agentskills.io/specification) package: `SKILL.md` with YAML frontmatter (`name`, `description`, …) and instructions, plus optional `scripts/`, `references/`, `assets/`.

| Skill | Purpose | Needs MCP server |
|---|---|---|
| [obs-model-comparison](obs-model-comparison/SKILL.md) | Guides the sample observation–model comparison: inputs, units, time alignment, tool calls, reporting with provenance and limitations | `obs-model-starter` |
| [earth-data-discovery](earth-data-discovery/SKILL.md) | Discovery-first check with Earthdata MCP and the catalog; fills the discovery record | `earthdata` (public) |

## Install, update, remove (Claude Code)

Claude Code loads skills from `.claude/skills/<skill-name>/SKILL.md` (this project) or `~/.claude/skills/<skill-name>/SKILL.md` (all your projects). This repository keeps **one canonical copy** here and installs copies with a script, so the same command works on macOS, Linux and Windows:

```bash
uv run python scripts/install_skills.py                 # install or update all, project scope
uv run python scripts/install_skills.py <skill-name>    # one skill
uv run python scripts/install_skills.py --personal      # into ~/.claude/skills/
uv run python scripts/install_skills.py --check         # report missing or outdated copies
uv run python scripts/install_skills.py --remove <skill-name>
```

After installing or updating, start a new Claude Code session in the repository folder. Edit only `skills/<name>/`; installed copies are overwritten and are git-ignored.

Installing a skill does not start or host any MCP server. The skill's required server must be connected separately (`.mcp.json` or `claude mcp add`).

## Tested clients

Only Claude Code has been exercised with these skills; see [docs/compatibility.md](../docs/compatibility.md). A valid `SKILL.md` alone is not evidence that another agent will discover or follow it.
