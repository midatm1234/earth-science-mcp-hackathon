# Skills

Canonical source of every agent skill in this repository. Each folder is an [Agent Skills](https://agentskills.io/specification) package: `SKILL.md` with YAML frontmatter (`name`, `description`, …) and instructions, plus optional `scripts/`, `references/`, `assets/`.

| Skill | Purpose | Needs MCP server |
|---|---|---|
| [obs-model-comparison](obs-model-comparison/SKILL.md) | Guides the sample observation–model comparison: inputs, units, time alignment, tool calls, reporting with provenance and limitations | `obs-model-starter` |
| [earth-data-discovery](earth-data-discovery/SKILL.md) | Discovery-first check with Earthdata MCP and the catalog; fills the discovery record | `earthdata` (public) |

## Install, update, remove

Each AI assistant reads skills from its own folder. This repository keeps **one canonical copy** here and copies it with a script, so the same command works on macOS, Linux and Windows:

| Assistant | Project folder | Personal folder (`--personal`) | Explicit invocation |
|---|---|---|---|
| Claude Code | `.claude/skills/<name>/` | `~/.claude/skills/<name>/` | `/name` |
| Codex | `.agents/skills/<name>/` | `~/.agents/skills/<name>/` | `$name` |
| GitHub Copilot (VS Code) | reads `.claude/skills/`, `.agents/skills/` and `.github/skills/` | `~/.copilot/skills/`, `~/.claude/skills/`, `~/.agents/skills/` | `/name` |

```bash
uv run python scripts/install_skills.py                     # install or update all, for every assistant
uv run python scripts/install_skills.py <skill-name>        # one skill
uv run python scripts/install_skills.py --client codex      # one assistant: claude | copilot | codex
uv run python scripts/install_skills.py --personal          # into your home folder
uv run python scripts/install_skills.py --check             # report missing or outdated copies
uv run python scripts/install_skills.py --remove <skill-name>
```

After installing or updating, start a new chat/session in the repository folder. Edit only `skills/<name>/`; installed copies are overwritten and are git-ignored. Copilot shows a skill once even when it is in two folders.

Installing a skill does not start or host any MCP server. The skill's required server must be connected separately (`.mcp.json` for Copilot and Claude Code, `.codex/config.toml` for Codex).

## Writing skills for several assistants

- Name MCP tools by server and tool (`obs-model-starter` → `compare_model_to_obs`) in the body. Each assistant adds its own prefix: `mcp__obs-model-starter__…` (Claude Code), `obs-model-starter-…` (Copilot), `mcp__obs_model_starter__…` (Codex).
- `allowed-tools` in the frontmatter is used by Claude Code only.
- Do not rely on assistant-specific commands (`/mcp`, `Grep`) inside the procedure.

## Tested assistants

See [docs/compatibility.md](../docs/compatibility.md). A valid `SKILL.md` alone is not evidence that an assistant will discover or follow it; only the combinations listed there were exercised.
