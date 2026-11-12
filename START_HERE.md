# Start here

This page is the shortest path from a laptop to your first successful MCP tool call, in VS Code, with the AI assistant of your choice: **GitHub Copilot**, **Claude Code** or **Codex**. It takes about 20 minutes, most of it downloads. Do it **before** the event if you can; the setup clinic will help with anything that does not work.

You do not need to know Python, Git or MCP. Copy each command exactly. A "terminal" is the text window where you type commands. In VS Code: **Terminal → New Terminal**.

## 1. Install VS Code and uv (10 minutes)

1. Install [VS Code](https://code.visualstudio.com/) and open it once.
2. Install **uv**, which installs Python and this project's packages. In a terminal:

   macOS or Linux:

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

   Windows (PowerShell):

   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

3. **Quit VS Code completely and start it again** (so it sees uv), open a terminal and check: `uv --version` prints a version number. If not, see [Troubleshooting: installation](docs/troubleshooting.md#installation).

## 2. Get this repository and open it in VS Code (2 minutes)

Either:

- **Without GitHub:** download the event ZIP from the link or USB stick provided by the organizers (location **TBD**), and unzip it into a normal folder such as `Documents` (not a OneDrive, iCloud or Google Drive synced folder); or
- **With Git:** `git clone https://github.com/midatm1234/earth-science-mcp-hackathon.git`.

In VS Code: **File → Open Folder…** and choose the **`earth-science-mcp-hackathon`** folder itself (not a folder above it). When VS Code asks *"Do you trust the authors of the files in this folder?"*, choose **Yes, I trust the authors**. The AI assistants only read this project's settings in a trusted folder that is open at its top level.

## 3. Install the project (3 minutes)

In the VS Code terminal (it opens in the project folder):

```bash
uv sync
uv run python scripts/install_skills.py
```

`uv sync` downloads Python 3.13 if needed and installs the locked packages into a private folder `.venv`. The second command copies the two agent skills to where every assistant looks for them.

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

## 5. Make the same call through your AI assistant (5 minutes)

Pick **one** assistant and follow its column. Details and screenshots of each step: [docs/setup.md](docs/setup.md#step-4--set-up-your-ai-assistant).

| | GitHub Copilot | Claude Code | Codex |
|---|---|---|---|
| Install | Built into VS Code | Extensions view → **Claude Code** (publisher Anthropic) | Extensions view → **Codex** (publisher OpenAI) |
| Sign in | Accounts menu → sign in with GitHub | JPL gen api subscription | Sign in with ChatGPT, not an API key |
| Open | Chat view (**View → Chat**); keep the default **Copilot** session (not *Local*) | Claude Code panel | Codex panel |
| Allow this project's settings | Workspace trust from step 2 is enough | Approve `obs-model-starter` and `earthdata` when asked | Trust the project once ([how](docs/setup.md#codex)) |
| Check MCP servers | Command Palette → **MCP: List Servers**: `obs-model-starter`, `earthdata` | type `/mcp` | ask "Which MCP tools do you have?" |

Then ask:

```text
Compare model A with the station observations at SYN-VALLEY.
```

Approve the tool calls when asked. The assistant should use the `obs-model-comparison` skill, call `describe_dataset` and `compare_model_to_obs`, and report about 23 monthly pairs, a mean bias near −1.05 °C and an RMSE near 1.21 °C. It should also mention the excluded month 2020-07 and say the data are synthetic. Wording varies; the numbers must match step 4.

If the assistant answers by running `scripts/first_call.py` or Python in the terminal instead of calling the MCP tool, the MCP servers are not connected: see [Troubleshooting: MCP server not connected](docs/troubleshooting.md#mcp-server-not-connected).

## Where next

- Continue with [tutorial 00](tutorials/00-first-tool-call.md), which explains what just happened and adds the HTTP transport.
- Then follow [tutorials 01–05](README.md#learning-path).
- Stuck? [docs/troubleshooting.md](docs/troubleshooting.md), or ask at the setup clinic.
