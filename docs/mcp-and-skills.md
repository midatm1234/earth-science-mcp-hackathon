# MCP and agent skills, explained

This page explains the six parts you will work with and how they fit together. Terms in **bold** are also in the [glossary](glossary.md).

## The short version

- **MCP gives an agent access to tools and data.** An MCP server is a small program that offers functions ("tools") such as "compare model and observations at a site". The agent can discover and call them.
- **A skill gives an agent reusable instructions for carrying out a task.** A skill is a folder with a `SKILL.md` file: when to use it, which tools to call in which order, what to check, and how to report the result.
- A skill can **guide the use of MCP tools**: the tool does the calculation correctly; the skill makes sure the agent checks units and time conventions first, calls the tool with sensible arguments, and explains the result with provenance and limitations.

## The six parts

| Part | What it is | In this hackathon |
|---|---|---|
| **AI application (host)** | The program you talk to. It runs the language model and the agent loop. | Claude Code (terminal) or the Claude Code extension for VS Code |
| **MCP client** | The piece inside the host that holds one connection to one MCP server and passes messages. | Created by Claude Code for each server in `.mcp.json`; also `scripts/first_call.py` is a client without any AI |
| **MCP server** | A program that offers tools (and optionally resources and prompts) using the Model Context Protocol. | `servers/obs-model-starter` (local), Earthdata MCP (remote, run by NASA), your team's server |
| **Tool** | One function a server offers: a name, a description, a typed input schema and a structured result. | `compare_model_to_obs`, `get_granules` |
| **Registry / catalog** | A list of available servers and skills with metadata so people (and agents) can find and evaluate them. | [catalog/](../catalog/) in this repository |
| **Agent skill** | A folder with `SKILL.md` (YAML header + instructions) and optional scripts or references. The agent loads it when relevant or when you type `/skill-name`. | `skills/obs-model-comparison`, `skills/earth-data-discovery`, your team's skill |

```text
 you ──► AI application (Claude Code) ─┬─ language model decides what to do
                                       │      ▲ reads skill instructions (SKILL.md)
                                       │
                                       ├─ MCP client ──stdio──► obs-model-starter server ──► local CSV fixtures
                                       └─ MCP client ──HTTPS──► Earthdata MCP server ──► NASA CMR metadata
```

## What happens during one request

You ask: "Compare model A with the station observations at SYN-VALLEY."

1. **Discovery.** When Claude Code starts, each MCP client asks its server `tools/list`. The model sees tool names, descriptions and input schemas. It also sees the name and description of every installed skill.
2. **Skill selection.** The request matches the `obs-model-comparison` description, so Claude loads the full `SKILL.md`. (Typing `/obs-model-comparison` loads it explicitly.)
3. **Tool calls.** Following the skill, Claude calls `list_datasets`, `describe_dataset` twice, then `compare_model_to_obs` with JSON arguments. Each call is a `tools/call` message; Claude Code asks your permission before the first call to each tool.
4. **Results.** The server returns structured JSON: number of valid pairs, bias, RMSE, units, excluded months, warnings, provenance.
5. **Answer.** Claude writes the answer in the format the skill requires, including provenance and limitations.

The model never reads the CSV files directly. It only sees what the tools return, which keeps answers grounded and auditable.

## Why both?

| Without… | What goes wrong |
|---|---|
| the MCP tool | The model may invent numbers, or ask you to paste data and do arithmetic itself. |
| the skill | The model may call the tool without checking units or time stamps, pick the wrong dataset, or omit provenance and limitations. |

Tools are tested like code (deterministic inputs → outputs). Skills are tested like procedures (does the agent follow them, trigger them at the right time, and not trigger them when irrelevant?).

## Transports: stdio and Streamable HTTP

The same server code can talk two ways; only the transport differs.

| Transport | How it works | When |
|---|---|---|
| **stdio** | The client starts the server as a child process and exchanges JSON-RPC messages over standard input/output. | Local development on your laptop. Default in `.mcp.json`. **Never `print()` to stdout in a stdio server**: it corrupts the message stream. Log to stderr. |
| **Streamable HTTP** | The server listens on a URL such as `http://127.0.0.1:8765/mcp`; clients send HTTP POST requests. | Remote or shared servers (Earthdata MCP, a future event server), and for testing with several clients. |

## Reachability: who can reach which server?

- A **local client** (Claude Code on your laptop) can reach any endpoint your laptop can reach: a stdio process it starts, `http://127.0.0.1:...`, a server on the venue network, or a public HTTPS URL.
- **Claude on the web (claude.ai) remote connectors** are called from Anthropic's infrastructure, not from your laptop. They can only reach servers on the public internet over HTTPS. `127.0.0.1` or a venue-only address will not work there. The core workshop therefore uses Claude Code locally.
- A file path returned by a remote server (for example `/srv/outputs/plot.png`) is a path **on that server**. It is not on your laptop. Remote tools should return compact results, or a download URL your client can reach, never a bare server-local path. See [server-deployment-plan.md](server-deployment-plan.md#delivery-of-generated-artifacts).

## Hosting servers vs installing skills

These are separate operations by different people:

| | MCP server | Agent skill |
|---|---|---|
| What is it? | A running program | A folder of instructions |
| Where does it live? | On your laptop (stdio) or on a host (HTTP) | Copied into `.claude/skills/<name>/` (project) or `~/.claude/skills/<name>/` (personal) on the machine running Claude Code |
| How do you add it? | `.mcp.json` or `claude mcp add ...` | `uv run python scripts/install_skills.py <name>` |
| Hosting needed? | Optional (a shared server is **TBD**) | Never; skills are not hosted |

A hosted server does not install any skill on your laptop, and installing a skill does not start any server. A skill whose required MCP server is not connected cannot do its job: it should say so and stop (both starter skills do).

## Compatibility claims

Skills here follow the open [Agent Skills](https://agentskills.io/specification) format, and the servers follow the MCP specification. That does **not** prove they work in every agent. We only claim what was tested; see [compatibility.md](compatibility.md).

## Optional advanced topics

Not needed for the hackathon, but often asked about: retrieval-augmented generation (RAG), writing your own agent loop (the ReAct pattern), multi-agent orchestration, MCP resources and prompts, OAuth for remote servers, and model training. The [reference review](reference-review.md) points to tutorials that cover them.
