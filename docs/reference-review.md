# Reference review

Review date: **2026-10-30**. Reviewer: organizer preparation for Hugo Kyo Lee. All repositories were cloned read-only (`git clone --depth 1`) and inspected; no code was copied except where stated in [attribution.md](attribution.md).

## Sources inspected

| Source | URL | Branch | Commit (date) | License |
|---|---|---|---|---|
| MCP tool registry | https://github.com/midatm1234/mcp-tool-registry (mirror of [eve-esa/mcp-tool-registry](https://github.com/eve-esa/mcp-tool-registry)) | `main` | `a49119dedcb7e929b69b7d78912dd52665c871fc` (2026-10-21) | Apache-2.0 (`LICENSE`) |
| Earthdata MCP | https://github.com/midatm1234/earthdata-mcp | `main` | `bb0ac5d5b2f59593659c6f8fbf02c3b12ff890df` (2026-05-21) | **No LICENSE file found** |
| Tutorial on Agentic AI | https://github.com/midatm1234/Tutorial-Agentic-AI | `main` | `05bd2feae72eca73d526356c630d07ee75f45bef` (2026-08-25) | **No LICENSE file found** |
| EVE handbook notebook | `MCP-Handbook.ipynb` (supplied file, 11 cells) | – | – | Not stated |
| EVE lab notebook (Team 3 project) | `START_HERE.ipynb` (supplied file, 74 cells, 13.6 MB, embedded imagery) | – | `STARTER_VERSION` = `d93c781` | Not stated; links to `eve-esa/agentic-eo-hackathon-bifold` |
| EVE Team 3 slides | `EVE Hackathon AAI4EO – Team 3.gslides` | – | – | **Not available** in the supplied folder; not reviewed |
| Live Earthdata MCP endpoint | https://cmr.earthdata.nasa.gov/mcp/v1 | – | server `earthdata-mcp`, version `dev`, protocol `2025-11-25` | Public service |
| MCP Python SDK | PyPI `mcp` | – | 2.3.0 (2026-10-02) | MIT |
| Claude Code docs | https://code.claude.com/docs/en/skills, `/setup`, `/mcp` | – | fetched 2026-10-30 | – |
| Agent Skills specification | https://agentskills.io/specification | – | fetched 2026-10-30 | – |

## mcp-tool-registry

**What it is.** A monorepo of MCP servers for Earth Observation, one folder per server under `servers/`, each with a FastMCP `server.py`, pinned `requirements.txt`, optional `.env.template` and `test.py`. CI (`pr-checks.yml`, `scripts/validate_pr.py`) checks one-server-per-PR, required files, entrypoint contract (`host="0.0.0.0"`, `port=8000`, `stateless_http=True`, `--transport stdio|http`), version constraints, `.env.template` placeholders, a 5 MB file-size limit, hard-coded secret patterns, startup, ruff and a Docker build. `deploy.yml` deploys merged servers to AWS Bedrock AgentCore. `CODEOWNERS` protects shared infrastructure.

**Reusable patterns adopted.** One folder per contribution; dual transport in one `server.py`; pinned dependencies; secret scan (patterns adapted, Apache-2.0, attributed); per-file size limit; CODEOWNERS for infrastructure; CI that installs only what a contribution needs.

**Adaptations.**

| Registry | This repository | Why |
|---|---|---|
| Merge → automatic AgentCore deployment | No deployment workflow; [deployment plan](server-deployment-plan.md) with manual promotion | No host is provisioned for this event; merge must not imply hosting |
| `requirements.txt` needs any version constraint (`>=` allowed) | Exact `==` pins checked against `uv.lock` | Identical installs on every laptop; reproducibility |
| `mcp[cli]>=1.2.0` and `from mcp.server.fastmcp import FastMCP` | `mcp==2.3.0`, `from mcp.server.mcpserver import MCPServer` | SDK 2.x renamed FastMCP (v1 import raises an explanatory error). Unpinned `>=1.2.0` now resolves to 2.x and breaks v1 code |
| HTTP default, `0.0.0.0` | stdio default, `127.0.0.1` for HTTP on laptops; `0.0.0.0` only in containers | Laptop safety; Claude Code uses stdio locally |
| Servers only | Servers **and** agent skills, with a catalog recording review, local verification, peer tests and hosting separately | Event scope |
| Test file optional | Tests required, including a real MCP call and an `is_error` case | "Meaningful tool tests" requirement |

## earthdata-mcp

**What it is.** NASA's MCP server over CMR (FastMCP ≥ 3.2, Python 3.13), with tools `get_keywords`, `get_collections`, `get_granules`, `get_services`, `get_tools`, `get_citations`, `get_variables`, and server instructions enforcing *Discover → Verify → Access*. Deployed at `https://cmr.earthdata.nasa.gov/mcp/v1` (Streamable HTTP). Live check on 2026-10-30: all seven tools listed; a MERRA-2 query returned real collection, granule, variable, service and citation records ([cached](../examples/data/cached/earthdata_discovery_merra2_t2m.json)).

**Reusable patterns.** The discovery workflow (vocabulary → collections with `has_granules` → granule verification → variables/services → access via `earthaccess`); WKT longitude-first conventions; distinguishing metadata from downloads.

**Adaptations.** Used as a **remote service only** (no code reused, since no license file was found). Our [earth-data-discovery skill](../skills/earth-data-discovery/SKILL.md) is original text describing the same sequence, adds the hackathon catalog search (check B), a route for model data outside CMR, and the discovery record. We note explicitly that Earthdata MCP is a dataset search service, not a registry of MCP servers or skills, and that `get_citations` returns publications using a dataset whereas the dataset citation is the collection DOI.

## Tutorial-Agentic-AI

**What it is.** A ~3-hour workshop: `00_setup` → `01_prompting` → `02_rag` → `03_tools_function_calling` → `04_agent_loop` → `05_mcp` (local stdio `mcp_server.py` with `get_time`, `list_files`) → `06_skills_plugins` (a Markdown `weather_skill.md`) → `07_single_vs_multi_agent`, with slides. Every notebook calls **Azure OpenAI** (paid resource with chat and embedding deployments, keys in `.env`).

**Reusable patterns.** The instructional progression (tool call → agent loop → MCP → skills); "add a tool and the client sees it with no client changes"; each module ending in an exercise.

**Adaptations.** All paid-API exercises are replaced by the Claude subscription workflow in Claude Code (the host runs the agent loop; participants do not write one). The core path is MCP tool → skill → combination → peer test; RAG, custom agent loops and multi-agent orchestration are optional background ([mcp-and-skills.md](mcp-and-skills.md#optional-advanced-topics)). The weather skill is a plain Markdown file; ours are real Agent Skills packages with frontmatter, installed into `.claude/skills/`. Original material written; no reuse because no license was found.

## Supplied EVE materials

**MCP-Handbook.ipynb.** A clear explanation of host/client/server, tools vs resources vs prompts, transports (stdio vs Streamable HTTP, stateless HTTP), registry habits (one server per PR, secrets in env, pinned deps, compact outputs), and the ReAct loop, written against EVE and FastMCP. Adopted ideas: the participant table, "descriptions the model can act on", "logs to stderr", "compact outputs, not rasters". Adapted to Claude Code as the host, MCP SDK 2.x, and the skills concept (absent from the handbook).

**START_HERE.ipynb / STARTER_VERSION d93c781 (EVE Team 3).** A self-contained notebook that embeds real Sentinel-2/WorldCover inputs for Berlin, computes a Monte Carlo variogram and spherical fit to choose a spatial guard (buffer), builds compact train/validation/test regions with one-sided guards, trains three small CNNs on CPU, serves four in-notebook MCP tools, and replays a recorded EVE conversation (clearly labelled as a replay). Valuable patterns: explicit labelling of recorded vs live evidence; honest scientific limits ("does not establish independence"); acceptance criteria stated before results; provenance of every input. It also contains the EVE pull-request instructions and appendix of use cases.

Used as the **optional advanced case study** only ([challenge card A1](challenge-cards.md#a1--spatial-dependence-and-separation-buffers--optional)). Not embedded in the starter: 13.6 MB of base64 imagery, rasterio/scipy/CNN training dependencies, and EVE credentials would break the "small, credential-free, laptop" requirement. Its demonstration structure informed [templates/demo.md](../templates/demo.md). The Team 3 slides were not available and are listed as pending.

## Version selection (checked 2026-10-30)

| Component | Selected | Notes |
|---|---|---|
| Python | 3.13 default (`.python-version`); supported 3.11–3.14 | Registry and Earthdata use 3.13; tested locally on 3.13 and 3.14 ([validation report](validation-report.md)) |
| MCP SDK | `mcp==2.3.0` | Latest stable; SDK supports protocol versions back to 2025; Earthdata server negotiated `2025-11-25` |
| Standalone FastMCP | not used | Earthdata uses `fastmcp` 3.x, latest is 4.1.4; one SDK keeps the dependency set small |
| uv | 0.13.6 used to lock | Lock file `uv.lock`; `requirements.txt` exported from it |
| Claude Code | 2.1.185 tested | Skills in `.claude/skills/<name>/SKILL.md`; project MCP servers in `.mcp.json` need approval |

## Unresolved reuse decisions

| Item | Decision needed | Current handling |
|---|---|---|
| earthdata-mcp code and docs | License unknown | Not reused; only the public service is used; ask maintainers before reusing text |
| Tutorial-Agentic-AI notebooks and slides | License unknown | Not reused; original material written |
| EVE notebooks (handbook, START_HERE) and logos | License not stated in the files | Not redistributed; ideas summarised with attribution; ask EVE/Pi School before reusing text or images |
| EVE Team 3 slides | File not available | Review pending |
