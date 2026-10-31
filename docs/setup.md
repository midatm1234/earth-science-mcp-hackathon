# Setup

This page explains every piece of free software, how to install it on each operating system, and how to check it. The short version is in [START_HERE.md](../START_HERE.md). Which combinations were actually tested is recorded in [compatibility.md](compatibility.md).

## What you install and why

| Software | Required? | Cost | What it does here |
|---|---|---|---|
| [uv](https://docs.astral.sh/uv/) | yes | free | Installs Python 3.13 and the exact package versions in `uv.lock`; runs scripts with `uv run` |
| [Claude Code](https://code.claude.com/docs/en/setup) | yes | free software; needs a Claude subscription to use | The AI assistant (MCP client + agent) used in tutorials |
| Claude subscription | yes | paid | Sign-in for Claude Code. The only paid prerequisite. |
| [Git](https://git-scm.com/downloads) | optional | free | Only for the pull-request route. Recommended on Windows so Claude Code can use Bash. |
| [VS Code](https://code.visualstudio.com/) + Anthropic's **Claude Code** extension | optional | free | Editor with the same Claude Code features in a side panel, same subscription |
| [Node.js](https://nodejs.org/) | optional | free | Only for the optional MCP Inspector (`npx @modelcontextprotocol/inspector`) |
| Docker, Jupyter | not needed | – | Never needed for the core workshop |

You do **not** need Anthropic API credits, Azure OpenAI, OpenAI credits, GitHub Copilot, a cloud account or a GPU.

## Before you start

- Use a normal local folder (for example `Documents/hackathon`). Avoid OneDrive, iCloud Drive, Google Drive or Dropbox folders: they try to synchronise the thousands of small files in `.venv` and can lock files while Python runs.
- About 1 GB of free disk space (Python ≈ 100 MB, packages ≈ 60 MB, Claude Code ≈ 200 MB).
- Administrator rights are not needed for uv or Claude Code; both install into your user folder.
- On a managed (corporate/university) laptop, check that you may run downloaded programs and that outbound HTTPS is allowed. If a proxy intercepts TLS, see [troubleshooting](troubleshooting.md#network-proxy-and-certificates).

## Step 1 – Install uv

| OS | Command |
|---|---|
| macOS, Linux | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Windows (PowerShell) | `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 \| iex"` |
| Alternatives | macOS: `brew install uv`; Windows: `winget install --id=astral-sh.uv -e` |

Close and reopen the terminal. Check: `uv --version` prints `uv 0.x.y`.

## Step 2 – Install Claude Code

| OS | Command |
|---|---|
| macOS, Linux, WSL | `curl -fsSL https://claude.ai/install.sh \| bash` |
| Windows (PowerShell) | `irm https://claude.ai/install.ps1 \| iex` |
| Windows (cmd) | `curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd` |
| Alternative | macOS: `brew install --cask claude-code` (does not auto-update) |

Official requirements (checked 2026-10-30): macOS 13+, Windows 10 1809+, Ubuntu 20.04+ (or similar), 4 GB RAM. On Windows, install [Git for Windows](https://git-scm.com/downloads/win) (`winget install --id Git.Git -e`) so Claude Code can use its Bash tool; without it Claude Code falls back to PowerShell, which also works for these tutorials.

Check: `claude --version` prints a version such as `2.1.185 (Claude Code)`.

### Sign in with your Claude subscription

1. Run `claude` in any folder.
2. Choose the **Claude account** (subscription) login and complete it in the browser.
3. In Claude Code, type `/status`. It should show your Claude account, not an API key.

If `/status` shows an API key, an environment variable such as `ANTHROPIC_API_KEY` or a configured key helper is overriding your subscription. See [troubleshooting](troubleshooting.md#claude-sign-in-and-usage-limits).

Claude plans and their Claude Code usage limits change over time. The organizer confirms before the event which plan level is sufficient (**TBD**); the exercises use short sessions.

## Step 3 – Get the repository

| Route | Steps |
|---|---|
| No GitHub account | Download the event bundle ZIP from the organizer's link, shared drive or USB stick (**TBD**). Check its SHA-256 if given: macOS/Linux `shasum -a 256 file.zip`; Windows `Get-FileHash file.zip`. Unzip. |
| Git | `git clone <URL TBD>` |

Then `cd earth-science-mcp-hackathon`.

## Step 4 – Install the project

```bash
uv sync
```

Expected: `Installed NN packages` and a new `.venv/` folder. `uv` reads `.python-version` (3.13) and downloads that Python if your computer does not have it. Supported range: Python 3.11–3.14.

Check:

```bash
uv run python --version
uv run python scripts/first_call.py
```

### Alternative without uv (pip)

Use this only if uv cannot be installed. You need Python 3.11–3.14 from [python.org](https://www.python.org/downloads/).

| OS | Commands |
|---|---|
| macOS, Linux | `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt -r requirements-dev.txt` |
| Windows | `py -3.13 -m venv .venv; .venv\Scripts\Activate.ps1; pip install -r requirements.txt -r requirements-dev.txt` |

Then replace `uv run python` with `python` in every command. The project's `.mcp.json` starts the server with `uv`; with pip, register the server for yourself instead:

```bash
claude mcp add --scope local obs-model-starter -- /full/path/to/earth-science-mcp-hackathon/.venv/bin/python servers/obs-model-starter/server.py
```

(Windows: `...\.venv\Scripts\python.exe`.) `requirements.txt` is exported from `uv.lock`, so both routes install the same versions.

## Step 5 – Install the skills and open Claude Code

```bash
uv run python scripts/install_skills.py
claude
```

Accept the folder trust prompt and approve the two project MCP servers (`obs-model-starter`, `earthdata`). Type `/mcp` to see them connected. Type `/` and look for `obs-model-comparison` and `earth-data-discovery` in the menu to confirm the skills loaded.

## Optional – VS Code with the Claude Code extension

1. Install VS Code.
2. Extensions view → search **Claude Code** (publisher **Anthropic**) → Install.
3. Open the `earth-science-mcp-hackathon` folder (File → Open Folder).
4. Open the Claude Code panel (Claude icon in the editor toolbar or activity bar, or Command Palette → "Claude Code"); sign in with the same Claude account.
5. The extension uses the same `.mcp.json`, `.claude/skills/` and subscription as the terminal. If a server shows as pending, run `claude` once in the integrated terminal (Terminal → New Terminal) to approve it.

## Optional – MCP Inspector (visual tool tester)

Needs Node.js. In one terminal start the server over HTTP, in another run the Inspector:

```bash
uv run python servers/obs-model-starter/server.py --transport http
npx @modelcontextprotocol/inspector
```

In the Inspector choose transport **Streamable HTTP**, URL `http://127.0.0.1:8765/mcp`, Connect, then Tools → List Tools.

## What the setup clinic checks

| Check | Command | Pass looks like |
|---|---|---|
| uv | `uv --version` | version printed |
| Claude Code | `claude --version` | version printed |
| Project | `uv run python scripts/first_call.py` | ends with `Success:` |
| Skills installed | `uv run python scripts/install_skills.py --check` | `ok` for each skill |
| Claude sign-in | `claude`, then `/status` | Claude account shown |
| MCP in Claude | `/mcp` | both servers connected |
