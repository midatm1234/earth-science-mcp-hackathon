# Start here

This page is the shortest path from a laptop to your first successful MCP tool call. It takes about 20 minutes, most of it downloads. Do it **before** the event if you can; the setup clinic will help with anything that does not work.

You do not need to know Python, Git or MCP. Copy each command exactly. A "terminal" is the text window where you type commands: **Terminal** on macOS, **PowerShell** on Windows, any terminal on Linux.

## 1. Install two free tools (10 minutes)

**uv** installs Python and this project's packages. **Claude Code** is the AI assistant you will use.

macOS or Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
curl -fsSL https://claude.ai/install.sh | bash
```

Windows (PowerShell):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
irm https://claude.ai/install.ps1 | iex
```

**Close the terminal and open a new one**, then check both:

```bash
uv --version
claude --version
```

Each prints a version number. If you see "command not found", see [Troubleshooting: installation](docs/troubleshooting.md#installation). Details and optional tools (Git, VS Code): [docs/setup.md](docs/setup.md).

## 2. Get this repository (2 minutes)

Either:

- **Without GitHub:** download the event ZIP from the link or USB stick provided by the organizers (location **TBD**), and unzip it into a normal folder such as `Documents` (not a OneDrive, iCloud or Google Drive synced folder); or
- **With Git:** `git clone <repository URL, TBD>`.

Then move into the folder:

```bash
cd earth-science-mcp-hackathon
```

## 3. Install the project (3 minutes)

```bash
uv sync
```

This downloads Python 3.13 if needed and installs the locked packages into a private folder `.venv`. Nothing else on your computer changes.

## 4. Make your first tool call — no AI involved (1 minute)

```bash
uv run python scripts/first_call.py
```

Expected ending:

```text
Step 3 - key results:
  site            : SYN-VALLEY
  valid pairs     : 23
  units           : degC (model conversion: K -> degC by subtracting 273.15)
  mean bias       : -1.054 degC  (mean(model - observation), in the units above)
  RMSE            : 1.212 degC
  ...
Success: you listed tools and called one through the Model Context Protocol.
```

You just used an MCP **client** (the script) to start an MCP **server** (the starter), list its **tools**, and call one. The data are synthetic teaching values.

## 5. Make the same call through Claude (5 minutes)

```bash
uv run python scripts/install_skills.py
claude
```

1. The first time, Claude Code asks you to sign in. Choose **Claude account (subscription)** and finish in the browser. Do not choose an API/Console account: you do not need API credits.
2. Claude Code asks whether to trust this folder and whether to use the MCP servers in `.mcp.json`. Answer **yes** for `obs-model-starter` and `earthdata`.
3. Type `/mcp` and press Enter. Both servers should show as connected. Press Esc.
4. Type:

   ```text
   Compare model A with the station observations at SYN-VALLEY.
   ```

5. Approve the tool calls when asked. Claude should report about 23 monthly pairs, a mean bias near −1.05 °C and an RMSE near 1.21 °C, mention the excluded month 2020-07, and say the data are synthetic.

Type `/exit` to leave.

## Where next

- Continue with [tutorial 00](tutorials/00-first-tool-call.md), which explains what just happened and adds the HTTP transport.
- Then follow [tutorials 01–05](README.md#learning-path).
- Stuck? [docs/troubleshooting.md](docs/troubleshooting.md), or ask at the setup clinic.
