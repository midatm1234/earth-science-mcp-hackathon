# Compatibility

We claim only what was tested. "Documented" means instructions exist but nobody has run them yet. Commands and outputs: [validation-report.md](validation-report.md).

## Platforms and Python

| Platform | Python | Install route | Status | Date |
|---|---|---|---|---|
| macOS 27.0.1, Apple silicon (arm64) | 3.13.18 (uv-managed, freshly downloaded) | uv, event bundle, empty uv cache | **tested** – all checks pass | 2026-10-30 |
| macOS 27.0.1, arm64 | 3.11.18, 3.12.16, 3.14.10 (uv-managed) | uv | **tested** – all checks pass | 2026-10-30 |
| macOS 27.0.1, arm64 | 3.14.3 (Homebrew) | pip + venv, `requirements*.txt` | **tested** – all checks pass | 2026-10-30 |
| macOS 27.0.1, arm64 | 3.13.18 | offline wheelhouse (`UV_OFFLINE=1`) | **tested** – all checks pass | 2026-10-30 |
| macOS Intel (x86_64) | 3.11–3.14 | uv | documented, untested | – |
| Windows 10/11 (x64, PowerShell) | 3.11–3.14 | uv / pip | documented, **untested** (CI job defined, not yet run) | – |
| Linux (Ubuntu 22.04/24.04) | 3.11–3.14 | uv / pip | documented, **untested** (CI jobs defined, not yet run) | – |
| WSL2 | 3.11–3.14 | uv | documented, untested | – |

The GitHub Actions workflow ([checks.yml](../.github/workflows/checks.yml)) covers Ubuntu (3.11, 3.13, 3.14), macOS and Windows (3.13) once the repository is pushed (destination **TBD**). Until it has run, those rows stay untested.

## MCP SDK and protocol

| Component | Version | Status |
|---|---|---|
| `mcp` Python SDK (server and client) | 2.3.0 | tested |
| Server ↔ client in-process | SDK 2.3.0 | tested (pytest) |
| Server over stdio (subprocess) | SDK 2.3.0 client | tested (pytest, `first_call.py`) |
| Server over Streamable HTTP | SDK 2.3.0 client; raw `curl` JSON-RPC declaring protocol `2025-06-18` | tested |
| SDK client → Earthdata MCP (remote) | negotiated protocol `2025-11-25` | tested live, 2026-10-30 |
| MCP Inspector | – | documented, untested |
| Code written for SDK v1 (`from mcp.server.fastmcp import FastMCP`) | – | **incompatible** with `mcp` 2.x; use `MCPServer` ([reference review](reference-review.md#mcp-tool-registry)) |

## Claude clients

| Client | Version | What was tested | Status |
|---|---|---|---|
| Claude Code CLI | 2.1.185 (macOS arm64) | Reads `.mcp.json`; connects `obs-model-starter` (stdio via uv) and `earthdata` (HTTP); lists both installed skills at session start (4/4 sessions) | **tested (client side)** |
| Claude Code CLI | 2.1.185 | Model-driven tool calls; explicit, natural and negative skill invocation; combined workflow | **pending** – the test machine's Claude Code used an institutional API gateway via a key helper (not a subscription), and that gateway was unreachable. Run `scripts/verify_claude_workflow.py` with a subscription account. |
| Claude Code with **subscription sign-in** | any | Sign-in, usage within plan limits | **pending** (organizer rehearsal) |
| Claude Code extension for VS Code | – | Same MCP servers and skills in the panel | documented, untested |
| Claude Desktop / claude.ai web | – | Not used; web remote connectors cannot reach laptop or `127.0.0.1` servers | out of scope |
| Other agents that read Agent Skills | – | Not tested | **no claim** |

## Skills format

| Check | Tool | Status |
|---|---|---|
| Frontmatter and naming per the Agent Skills spec | `skills-ref` 0.1.1 (`agentskills validate`) | tested – both skills valid |
| Hackathon sections and catalog rules | `scripts/validate_repo.py` | tested |
| Discovery by Claude Code | Claude Code 2.1.185 session init lists both skills | tested |
| Triggering and following the procedure | `scripts/verify_claude_workflow.py` | **pending** (see above) |

A valid `SKILL.md` does not by itself show that any agent will trigger or follow it. Add rows here only with evidence.
