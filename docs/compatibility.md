# Compatibility

We claim only what was tested. "Documented" means instructions exist but nobody has run them yet. Commands and outputs: [validation-report.md](validation-report.md).

## AI assistants

The hackathon supports three assistants in VS Code. They share the same repository files:

| | GitHub Copilot | Claude Code | Codex |
|---|---|---|---|
| VS Code integration | built-in Chat view (Copilot harness) | Anthropic *Claude Code* extension | OpenAI *Codex* extension |
| Account | GitHub with Copilot (Free tier exists) | Claude subscription | ChatGPT (Free tier includes Codex) |
| MCP configuration read | `.mcp.json` (trusted workspace) | `.mcp.json` (approved project servers) | `.codex/config.toml` (trusted project) |
| Skills folder read | `.claude/skills`, `.agents/skills`, `.github/skills` | `.claude/skills` | `.agents/skills` |
| Explicit skill invocation | `/name` | `/name` | `$name` |
| MCP tool name shown | `obs-model-starter-compare_model_to_obs` | `mcp__obs-model-starter__compare_model_to_obs` | server `obs-model-starter`, tool `compare_model_to_obs` |
| Project instructions | `AGENTS.md` | `CLAUDE.md` (imports `AGENTS.md`) | `AGENTS.md` |

### What was tested (2026-10-30, macOS 27.0.1 arm64)

`scripts/verify_agent_workflow.py` runs five checks through each assistant's command-line engine, from a clean clone in a local folder: **mcp** (real MCP call, numbers checked against the science module), **explicit** skill invocation, **natural** trigger, **negative** (skill and tools must not be used), **combined** (discovery skill + live Earthdata MCP + starter).

| Assistant engine | Version | mcp | explicit | natural | negative | combined | Notes |
|---|---|---|---|---|---|---|---|
| GitHub Copilot CLI | 1.0.105 (model claude-sonnet-5.5 via Copilot) | **pass** | **pass** | **pass** | **pass** | **pass** | Reads `.mcp.json` only in a trusted folder (`--trust-folder` in prompt mode). Without trust it silently ran `scripts/first_call.py` through the shell instead – not MCP. |
| Codex CLI bundled in the OpenAI VS Code extension | codex-cli 0.164.0-alpha.11.1 (extension 26.51021.22027), ChatGPT sign-in | **pass** | **pass** | **pass** | **pass** | **pass** | Reads `.codex/config.toml` and `.agents/skills` only after the project is trusted in `~/.codex/config.toml`. Codex reads `SKILL.md` with a read-only shell command before following it. |
| Claude Code CLI | 2.1.185 | blocked | blocked | – | – | – | Connects both MCP servers and lists both skills at session start (verified). Model-driven checks blocked: this machine's Claude Code is configured for an institutional API gateway that was unreachable; no Claude subscription was available. |

Additional checks that passed with Copilot and Codex: a team server and skill created by `scripts/new_contribution.py` were usable immediately (real `summarize_values` MCP call), proving the scaffold's registration in both config files.

### VS Code GUI

| Item | Status |
|---|---|
| VS Code 1.144.0 with Copilot Chat (built in), Claude Code extension 2.1.314, Codex extension 26.51021.22027 installed | present on the test machine |
| Copilot harness reads workspace `.mcp.json` and `.claude/.agents/.github` skills; `.mcp.json` inherits Workspace Trust | per official VS Code docs (checked 2026-10-30); engine behaviour verified with Copilot CLI |
| Codex extension and CLI share `~/.codex/config.toml` | per official OpenAI docs; the binary tested is the one inside the extension |
| START_HERE step 5 clicked through in the VS Code GUI with each assistant | **pending** – organizer rehearsal ([facilitator guide](facilitator-guide.md#rehearsal-checklist)) |
| VS Code *Local* harness (reads `.vscode/mcp.json`, which this repository does not provide) | not supported; participants use the default Copilot session |
| VS Code Claude/Codex harnesses inside the Chat view (Agent Host) | documented by VS Code, untested |

## Platforms and Python

| Platform | Python | Install route | Status | Date |
|---|---|---|---|---|
| macOS 27.0.1, Apple silicon (arm64) | 3.13.18 (uv-managed, freshly downloaded) | uv, event bundle, empty uv cache | **tested** – all checks pass | 2026-10-30 |
| macOS 27.0.1, arm64 | 3.11.18, 3.12.16, 3.14.10 (uv-managed) | uv | **tested** – all checks pass | 2026-10-30 |
| macOS 27.0.1, arm64 | 3.14.3 (Homebrew) | pip + venv, `requirements*.txt` | **tested** – all checks pass | 2026-10-30 |
| macOS 27.0.1, arm64 | 3.13.18 | offline wheelhouse (`UV_OFFLINE=1`) | **tested** – all checks pass | 2026-10-30 |
| macOS Intel (x86_64) | 3.11–3.14 | uv | documented, untested | – |
| Windows Server 2025 x64 (GitHub `windows-2025` runner image) | 3.13.17 | uv 0.13.6 (`uv sync --locked`) | **tested in CI** – `check_all.py` incl. stdio and HTTP transport tests, lint, lock checks ([run](https://github.com/midatm1234/earth-science-mcp-hackathon/actions/runs/41177032319)) | 2026-10-31 |
| Ubuntu 24.04 x64 (GitHub runner image) | 3.11.18, 3.13.18, 3.14.10 | uv 0.13.6 | **tested in CI** – same checks ([run](https://github.com/midatm1234/earth-science-mcp-hackathon/actions/runs/41177032319)) | 2026-10-31 |
| macOS 26 arm64 (GitHub runner image) | 3.13.16 | uv 0.13.6 | **tested in CI** – same checks ([run](https://github.com/midatm1234/earth-science-mcp-hackathon/actions/runs/41177032319)) | 2026-10-31 |
| Windows 10/11 desktop (participant laptop, PowerShell installers, VS Code + assistant) | 3.11–3.14 | uv / pip | documented, **untested** | – |
| Linux desktop (participant laptop, VS Code + assistant) | 3.11–3.14 | uv / pip | documented, **untested** | – |

The GitHub Actions workflow ([checks.yml](../.github/workflows/checks.yml)) runs on every push to `main` and every pull request: Ubuntu (3.11, 3.13, 3.14), macOS and Windows (3.13). It runs no AI assistant, so it does not cover the assistant rows above.

## MCP SDK and protocol

| Component | Version | Status |
|---|---|---|
| `mcp` Python SDK (server and client) | 2.3.0 | tested |
| Server over stdio / Streamable HTTP | SDK 2.3.0 client; raw `curl` JSON-RPC | tested |
| Protocol negotiated with Copilot CLI | `2026-07-28` | tested |
| Protocol negotiated with Earthdata MCP (SDK client) | `2025-11-25` | tested |
| Code written for SDK v1 (`from mcp.server.fastmcp import FastMCP`) | – | **incompatible** with `mcp` 2.x; use `MCPServer` |

## Skills format

| Check | Tool | Status |
|---|---|---|
| Frontmatter and naming per the Agent Skills spec | `skills-ref` 0.1.1 (`agentskills validate`) | tested – both skills valid |
| Hackathon sections and catalog rules | `scripts/validate_repo.py` | tested |
| Discovery and use by Copilot and Codex | `verify_agent_workflow.py` | tested (above) |
| Discovery by Claude Code | session init lists both skills | tested; use pending |

A valid `SKILL.md` does not by itself show that an assistant will trigger or follow it. Add rows here only with evidence.
