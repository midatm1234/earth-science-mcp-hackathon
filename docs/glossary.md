# Glossary

| Term | Meaning |
|---|---|
| **Agent** | A language model that decides which tools to call, reads the results and repeats until it can answer. |
| **Agent skill** | A folder containing `SKILL.md` (YAML frontmatter with `name` and `description`, then instructions) and optional `scripts/`, `references/`, `assets/`. Loaded by the agent when relevant or when invoked as `/name`. Format: [agentskills.io](https://agentskills.io/specification). |
| **AI application / host** | The program you interact with that runs the model and agent loop, e.g. GitHub Copilot, Claude Code or Codex. |
| **AI assistant** | In this repository: GitHub Copilot (built into VS Code), Claude Code (Anthropic extension) or Codex (OpenAI extension). Any one is enough. |
| **Harness** | VS Code's name for the engine that runs an agent session (Copilot, Claude, Codex or Local). Each reads its own configuration files. |
| **Alignment (time)** | Matching values from two datasets to the same time period before comparing them. Here: calendar month. |
| **Bias (mean bias)** | Average of (model − observation). Negative means the model is lower. |
| **Catalog** | This repository's list of MCP servers and skills: [catalog/](../catalog/). |
| **CLI** | Command-line interface: a program you run by typing in a terminal. |
| **Client (MCP client)** | The component that connects to one MCP server and exchanges messages with it. |
| **CMR** | NASA's Common Metadata Repository: metadata for Earthdata collections, granules, variables and services. |
| **Collection** | A dataset in CMR (for example MERRA-2 M2TMNXSLV). Identified by a concept id like `C1276812859-GES_DISC`. |
| **Concept id** | CMR's identifier for a collection (`C…`), granule (`G…`), variable (`V…`), service (`S…`). |
| **Credential** | A secret used to prove identity: password, API key, token. Never written into files in this repository. |
| **Discovery record** | The form a team fills in before building: [templates/discovery-record.md](../templates/discovery-record.md). |
| **DOI** | Digital Object Identifier: a persistent citation link for a dataset or paper. |
| **Earthdata Login** | Free NASA account needed to download most Earthdata files. Not needed for metadata search. |
| **Earthdata MCP** | NASA's public MCP server for searching CMR metadata, at `https://cmr.earthdata.nasa.gov/mcp/v1`. It finds datasets; it is not a registry of MCP servers or skills. |
| **Fill value** | A special number (e.g. `-9999`) meaning "missing" in a data file. |
| **Fixture** | A small, fixed data file used for teaching and testing. |
| **Freeze** | The moment a contribution's version is fixed for peer testing (commit SHA recorded). |
| **Frontmatter** | The YAML block between `---` lines at the top of `SKILL.md`. |
| **Git, fork, branch, pull request (PR)** | Version-control concepts. A fork is your copy of a repository on GitHub, a branch is a line of changes, and a PR asks maintainers to merge your branch. Teams submit by pull request; the mentor merges. |
| **Granule** | One file (or file-like unit) within a collection, e.g. one month of MERRA-2. |
| **JSON** | A text format for structured data, used for tool inputs and outputs. |
| **JSON-RPC** | The message format MCP uses (requests with `method` and `params`, responses with `result` or `error`). |
| **Lock file** | `uv.lock`: exact versions of every package, so all laptops install the same thing. |
| **MCP (Model Context Protocol)** | An open protocol that lets AI applications discover and call tools and read data from external programs in a standard way. |
| **MCP Inspector** | An optional web tool for listing and calling a server's tools by hand. |
| **Peer test** | Independent reproduction of another team's contribution by people who did not write it. |
| **Provenance** | Where data and results came from: source, version, processing, and whether values are synthetic, cached or live. |
| **Representativeness** | Difference caused by comparing different spatial supports, e.g. a point station vs a grid-cell average. |
| **RMSE** | Root-mean-square error: sqrt(mean((model − observation)²)). Always ≥ 0; includes bias and scatter. |
| **Schema (input schema)** | The JSON description of a tool's arguments: names, types, required or optional. |
| **Server (MCP server)** | A program offering tools/resources/prompts over MCP. |
| **stdio** | Standard input/output. An MCP transport where the client starts the server and talks through its stdin/stdout. |
| **Streamable HTTP** | An MCP transport over HTTP, used for remote servers. |
| **Structured output** | A tool result as JSON fields (e.g. `n_valid_pairs`) rather than free text. |
| **Synthetic data** | Invented values for teaching or testing. Never presented as observations or model output. |
| **Tool** | A function exposed by an MCP server, with a name, description, input schema and result. |
| **Trust (workspace / project)** | Permission for tools to read a folder's configuration and run its MCP servers: VS Code Workspace Trust (Copilot, Claude Code), Codex project trust, Claude Code project-server approval. |
| **Transport** | How MCP messages travel: stdio or Streamable HTTP. |
| **uv** | A fast Python package and project manager that also installs Python. |
| **WKT** | Well-Known Text geometry, e.g. `POLYGON((lon lat, ...))`. Earthdata MCP expects **longitude first**. |
