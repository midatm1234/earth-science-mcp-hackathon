# Setup

This page explains every piece of software, how to install it on each operating system, and how to check it. The short version is in [START_HERE.md](../START_HERE.md). Which combinations were actually tested is recorded in [compatibility.md](compatibility.md).

## What you install and why

| Software | Required? | Cost | What it does here |
|---|---|---|---|
| [VS Code](https://code.visualstudio.com/) | yes | free | Editor and home of the AI assistant |
| [uv](https://docs.astral.sh/uv/) | yes | free | Installs Python 3.13 and the exact package versions in `uv.lock`; runs scripts with `uv run`; starts the MCP server for every assistant |
| **One** AI assistant: GitHub Copilot, Claude Code or Codex | yes | account needed (free tiers exist for Copilot and ChatGPT/Codex) | The MCP client and agent used in tutorials |
| [Git](https://git-scm.com/downloads) | optional | free | Only for the pull-request route. Recommended on Windows (Claude Code uses its Bash). |
| Assistant command-line tools (`claude`, `copilot`, `codex`) | optional | free software | Same assistants in a terminal; useful for diagnostics and for organizers' automated checks |
| [Node.js](https://nodejs.org/) | optional | free | Only for the optional MCP Inspector and for installing the Copilot/Codex CLIs with npm |
| Docker, Jupyter | not needed | – | Never needed for the core workshop |

You do **not** need API keys or API credits for any provider, Azure OpenAI, a cloud account or a GPU.

## Before you start

- Use a normal local folder (for example `Documents/hackathon`). Avoid OneDrive, iCloud Drive, Google Drive or Dropbox folders: they try to synchronise the thousands of small files in `.venv` and can lock files while Python runs.
- About 1 GB of free disk space.
- Administrator rights are not needed for uv; VS Code can be installed per user.
- On a managed (corporate/university) laptop, check that you may install VS Code extensions and that outbound HTTPS is allowed. Organization policies can disable Copilot features or the Claude/Codex integrations ([troubleshooting](troubleshooting.md#assistant-sign-in-and-usage-limits)).

## Step 1 – Install VS Code and uv

| OS | VS Code | uv |
|---|---|---|
| macOS | [download](https://code.visualstudio.com/), drag to Applications | `curl -LsSf https://astral.sh/uv/install.sh \| sh` (or `brew install uv`) |
| Windows | [download](https://code.visualstudio.com/) (User Installer) | PowerShell: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 \| iex"` (or `winget install --id=astral-sh.uv -e`) |
| Linux | `.deb`/`.rpm`/snap from the VS Code site | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |

**Quit and restart VS Code** after installing uv. VS Code reads `PATH` when it starts; the AI assistants start the MCP server with the `uv` command, so VS Code must see it. Check in a VS Code terminal: `uv --version`.

## Step 2 – Get the repository and open it

| Route | Steps |
|---|---|
| No GitHub account | Download the event bundle ZIP from the organizer's link, shared drive or USB stick (**TBD**). Check its SHA-256 if given: macOS/Linux `shasum -a 256 file.zip`; Windows `Get-FileHash file.zip`. Unzip. |
| Git | `git clone https://github.com/midatm1234/earth-science-mcp-hackathon.git` |

In VS Code use **File → Open Folder…** and select the `earth-science-mcp-hackathon` folder **itself**. Every assistant reads its configuration from the top of the opened folder: `.mcp.json`, `.codex/config.toml`, `AGENTS.md`, `.claude/` and `.agents/`. If you open a parent folder, none of it is found.

Answer **Yes, I trust the authors** to VS Code's Workspace Trust prompt. In Restricted Mode, VS Code does not start the project's MCP servers.

## Step 3 – Install the project and the skills

In the VS Code terminal (**Terminal → New Terminal**):

```bash
uv sync
uv run python scripts/install_skills.py
uv run python scripts/first_call.py
```

Expected: `Installed NN packages`, then `installed ... -> .claude/skills/...` and `... -> .agents/skills/...` for both skills, then `Success:`. Supported Python range: 3.11–3.14; uv downloads 3.13 if needed.

The skills are copied to `.claude/skills/` (Claude Code; also read by Copilot) and `.agents/skills/` (Codex and Copilot). Copilot lists a skill once even though it is in both places.

### Alternative without uv (pip)

Use this only if uv cannot be installed. You need Python 3.11–3.14 from [python.org](https://www.python.org/downloads/).

| OS | Commands |
|---|---|
| macOS, Linux | `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt -r requirements-dev.txt` |
| Windows | `py -3.13 -m venv .venv; .venv\Scripts\Activate.ps1; pip install -r requirements.txt -r requirements-dev.txt` |

Replace `uv run python` with `python` in every command. The shared MCP configuration starts servers with `uv`, so on this route edit the `command` in [.mcp.json](../.mcp.json) and [.codex/config.toml](../.codex/config.toml) to the full path of `.venv/bin/python` (Windows: `.venv\Scripts\python.exe`) and drop `run`, `--quiet`, `python` from `args`. Do not commit that change.

## Step 4 – Set up your AI assistant

Choose one. You can install more than one; they share the same project files.

### GitHub Copilot

1. Copilot Chat is built into current VS Code. Sign in with GitHub from the **Accounts** menu (bottom left) and follow the prompts to enable Copilot for your account (Copilot Free is offered to individuals without an organization plan).
2. Open the Chat view (**View → Chat**). Keep the default **Copilot** session; the *Local* session type reads a different MCP file (`.vscode/mcp.json`) that this repository does not use.
3. Copilot reads the MCP servers from `.mcp.json` in the trusted workspace. Command Palette (**Cmd/Ctrl+Shift+P**) → **MCP: List Servers** should show `obs-model-starter` and `earthdata`. Use **Show Output** on a server if it fails to start.
4. Skills: type `/` in the chat input; `obs-model-comparison` and `earth-data-discovery` appear. Invoke with `/obs-model-comparison …`.
5. Ask the START_HERE question. Approve the tool calls when Copilot asks.

### Claude Code

1. Extensions view (**Cmd/Ctrl+Shift+X**) → search **Claude Code** (publisher **Anthropic**) → Install.
2. Open the Claude Code panel (Claude icon in the editor toolbar or activity bar, or Command Palette → "Claude Code") and sign in with your **Claude account (subscription)**. Do not choose an API/Console account.
3. Approve the project MCP servers `obs-model-starter` and `earthdata` when asked (they are defined in `.mcp.json`). Type `/mcp` to see them connected. If they stay pending, open a terminal and run `claude` once to approve them (requires the [Claude Code CLI](https://code.claude.com/docs/en/setup): `curl -fsSL https://claude.ai/install.sh | bash`, Windows `irm https://claude.ai/install.ps1 | iex`).
4. Skills: `/obs-model-comparison …`.
5. Type `/status` to confirm you are using your Claude account, not an API key.

### Codex

1. Extensions view → search **Codex** (publisher **OpenAI**) → Install. Open the Codex panel and **sign in with ChatGPT** (not an API key).
2. **Trust the project once.** Codex reads `.codex/config.toml` (the MCP servers) only for trusted projects. Either:
   - with the Codex CLI (macOS/Linux `curl -fsSL https://chatgpt.com/codex/install.sh | sh`; Windows PowerShell `powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"`; or `npm install -g @openai/codex`): run `codex` in the VS Code terminal in this folder and accept *"trust this folder"*; or
   - add these two lines to `~/.codex/config.toml` (Windows: `%USERPROFILE%\.codex\config.toml`), using the folder's full path:

     ```toml
     [projects."/full/path/to/earth-science-mcp-hackathon"]
     trust_level = "trusted"
     ```

   The Codex CLI and the VS Code extension share `~/.codex/config.toml`, so this is needed only once. On macOS, paths under `/tmp` resolve to `/private/tmp`: use the real path.
3. Start a new Codex chat. Ask "Which MCP tools do you have?" The answer should list `obs-model-starter` (3 tools) and `earthdata` (7 tools). With the CLI: `codex mcp list`.
4. Skills are read from `.agents/skills/`. Invoke with `$obs-model-comparison …` (type `$` to pick a skill).
5. Ask the START_HERE question. Codex calls the MCP tools; approve them if asked.

### Interfaces and harnesses (for the curious)

VS Code 1.144 can also run Claude and Codex as *harnesses* inside its own Chat view. They use the same project files as the extensions (Claude: `.mcp.json`, `.claude/skills`; Codex: `.codex/config.toml`, `.agents/skills`). The tested combinations are listed in [compatibility.md](compatibility.md); use the extension route above unless your mentor suggests otherwise.

## Optional – MCP Inspector (visual tool tester)

Needs Node.js. In one terminal start the server over HTTP, in another run the Inspector:

```bash
uv run python servers/obs-model-starter/server.py --transport http
npx @modelcontextprotocol/inspector
```

In the Inspector choose transport **Streamable HTTP**, URL `http://127.0.0.1:8765/mcp`, Connect, then Tools → List Tools.

## What the setup clinic checks

| Check | How | Pass looks like |
|---|---|---|
| uv | `uv --version` in a VS Code terminal | version printed |
| Project | `uv run python scripts/first_call.py` | ends with `Success:` |
| Skills installed | `uv run python scripts/install_skills.py --check` | `ok` for each skill and folder |
| Workspace | VS Code title shows `earth-science-mcp-hackathon`; not in Restricted Mode | trusted |
| Assistant signed in | Copilot: Accounts menu · Claude: `/status` · Codex: panel shows your ChatGPT account | personal account, not an API key |
| MCP in the assistant | Copilot: **MCP: List Servers** · Claude: `/mcp` · Codex: "Which MCP tools do you have?" | `obs-model-starter` and `earthdata` |
| End to end | the START_HERE question | ~23 pairs, bias ≈ −1.05 °C, RMSE ≈ 1.21 °C, MCP tools called (not a shell script) |
