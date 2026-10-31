# Guidance for coding agents

This file tells AI coding agents (GitHub Copilot, Codex and Claude Code via `CLAUDE.md`) how to work in this repository. Humans: see [CONTRIBUTING.md](CONTRIBUTING.md).

## Repository map

- `servers/<name>/` – MCP servers. `science.py` holds scientific functions (no MCP imports); `server.py` is a thin MCP wrapper using `mcp.server.mcpserver.MCPServer` (MCP Python SDK 2.x, **not** the v1 `mcp.server.fastmcp` import).
- `skills/<name>/SKILL.md` – canonical agent skills. `.claude/skills/` and `.agents/skills/` hold installed copies; never edit them, edit `skills/` and run `uv run python scripts/install_skills.py`.
- `.mcp.json` (Copilot, Claude Code) and `.codex/config.toml` (Codex) register MCP servers; keep them identical with `uv run python scripts/client_config.py register <name>` / `check`.
- `catalog/entries/*.yaml` – one record per server or skill; regenerate `catalog/index.md` with `uv run python scripts/catalog.py index`.
- `templates/` – scaffolding used by `scripts/new_contribution.py`.
- `docs/`, `tutorials/` – participant documentation for beginners; keep wording plain and steps exact.

## Commands

| Task | Command |
|---|---|
| Install | `uv sync` |
| All checks (no network, no LLM) | `uv run python scripts/check_all.py` |
| One server's tests | `uv run pytest servers/<name>/tests` |
| Validation subset | `uv run python scripts/validate_repo.py --only skills --only links` |
| Lint | `uv run ruff check .` |
| Plain MCP call | `uv run python scripts/first_call.py` |

## Rules

1. Never `print()` to stdout in a server; stdio carries the protocol. Log to stderr.
2. Keep science separate from MCP wrappers. Tools take typed, described arguments (`Annotated[..., Field(description=...)]`), return compact structured dicts, and raise `ToolError` with an actionable message for expected failures.
3. Every numeric result must carry units, the rules used (alignment, missing data) and provenance; synthetic data must be labelled synthetic.
4. Add or update tests with hand-computed expected values and at least one real MCP call; keep tests offline and credential-free.
5. Pin dependencies with `==`, add them via `uv add`, and keep `servers/*/requirements.txt` identical to `uv.lock`.
6. Never write secrets, `.env` files or credentials. Never add a deployment workflow; deployment is disabled until the organizer authorizes a host.
7. Keep catalog status fields (review, local verification, peer testing, hosting) separate; do not mark anything hosted or peer-tested without evidence.
8. Do not claim verification you did not run. Mark checks pending or blocked instead.
9. Use relative links in Markdown; run the link check after editing docs.
