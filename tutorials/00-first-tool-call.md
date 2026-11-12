# Tutorial 00 – Your first MCP tool call

| | |
|---|---|
| **Scientific purpose** | Get a trustworthy number (model bias against observations) from a tool rather than from the model's memory. |
| **Learning objective** | Make a successful MCP tool call two ways: from a plain client script over stdio, and through your AI assistant in VS Code (GitHub Copilot, Claude Code or Codex). Name the client, server and tool in each case. |
| **Starting state** | [Setup](../docs/setup.md) done: VS Code and uv installed; repository folder open and trusted in VS Code; `uv sync` and `install_skills.py` run; one AI assistant signed in. |
| **Credentials** | Your AI assistant's account sign-in for part B only. No other accounts. |

## A. Plain MCP client over stdio (no AI)

```bash
uv run python scripts/first_call.py
```

What happens: the script ([first_call.py](../scripts/first_call.py)) is an MCP **client**. It starts [server.py](../servers/obs-model-starter/server.py) as a subprocess, sends `tools/list`, then `tools/call` for `compare_model_to_obs`.

Expected output (key lines):

```text
Step 1 - tools/list returned:
  - list_datasets: List the sample datasets this server can read.
  - describe_dataset: Summarize one dataset's metadata before using it.
  - compare_model_to_obs: Compare monthly model values with observations at one site.
...
  valid pairs     : 23
  mean bias       : -1.054 degC  (mean(model - observation), in the units above)
  RMSE            : 1.212 degC
  excluded months : {'obs_missing_value': ['2020-07']}
Success: you listed tools and called one through the Model Context Protocol.
```

You will also see log lines starting with a timestamp: those come from the server on **stderr**, which is where server logs must go.

Try an invalid input to see a readable error rather than a crash:

```bash
uv run python scripts/first_call.py --site ATLANTIS
```

Expected: `The tool returned an error ... No rows for site 'ATLANTIS' ... Observation sites: SYN-COAST, SYN-MOUNTAIN, SYN-VALLEY.`

## B. Through your AI assistant

The assistant is another MCP client. It starts the same server from the project configuration: `.mcp.json` for Copilot and Claude Code, `.codex/config.toml` for Codex.

1. Make sure the MCP servers are connected ([setup, step 4](../docs/setup.md#step-4--set-up-your-ai-assistant)):

   | Copilot | Claude Code | Codex |
   |---|---|---|
   | Command Palette → **MCP: List Servers** | `/mcp` | "Which MCP tools do you have?" (CLI: `codex mcp list`) |

   Expected: `obs-model-starter` (3 tools) and `earthdata` (7 tools).

2. Ask, without naming tools:

   ```text
   What sample datasets do you have access to through MCP, and what are their units?
   ```

   Expected: the assistant asks permission to run `list_datasets` from `obs-model-starter` (Copilot shows it as `obs-model-starter-list_datasets`, Claude Code as `mcp__obs-model-starter__list_datasets`, Codex as a call to server `obs-model-starter`, tool `list_datasets`). After you approve, it lists three synthetic datasets: station observations in degC, model A in K, model B in degC.

3. Ask the scientific question:

   ```text
   Compare model A with the station observations at SYN-VALLEY.
   ```

   Expected: the assistant uses the `obs-model-comparison` skill and calls `describe_dataset` and `compare_model_to_obs`. The answer reports 23 pairs, bias ≈ −1.05 °C, RMSE ≈ 1.21 °C, the K→°C conversion, the excluded month 2020-07, a note that observations are points and model values are grid cells, and that the data are synthetic. Wording varies; the numbers must match part A.

If the assistant instead runs `scripts/first_call.py` or Python in the terminal, it did **not** use MCP: fix the connection ([troubleshooting](../docs/troubleshooting.md#mcp-server-not-connected)).
 
## Exercise

Ask your assistant: "Is model A or model B closer to the observations at SYN-MOUNTAIN?" Check that its numbers match the answer below.

<details><summary>Answer</summary>

Model B is closer. At SYN-MOUNTAIN:

| Model | Valid pairs | Mean bias (model − obs) | RMSE |
|---|---|---|---|
| A | 22 | +2.808 °C | 2.901 °C |
| B | 23 | −0.665 °C | 1.126 °C |

Model A has 22 pairs because its 2021-11 value is missing; both models also lose 2020-12 because the observation is absent. Model A is converted from K to °C by the tool. Wording varies, but your assistant's numbers must match these. Both datasets are synthetic, so the ranking says nothing about real models.
</details>

## Common errors and recovery

| Symptom | Cause | Fix |
|---|---|---|
| `uv: command not found` | Terminal opened before install | Open a new terminal; see [troubleshooting](../docs/troubleshooting.md#installation) |
| Assistant shows no `obs-model-starter` server | Folder not open at its top level, workspace not trusted, or (Codex) project not trusted | [troubleshooting](../docs/troubleshooting.md#mcp-server-not-connected) |
| Server listed as failed | `uv` not visible to VS Code | Quit and restart VS Code; [troubleshooting](../docs/troubleshooting.md#mcp-server-not-connected) |
| Assistant answers without calling a tool | It answered from general knowledge | Say "use the obs-model-starter tools"; check the tool was approved |
| Usage limit message | Account limit reached | Continue with part A; see [troubleshooting](../docs/troubleshooting.md#assistant-sign-in-and-usage-limits) |

Next: [Tutorial 01 – Discover existing capabilities](01-discover-existing-capabilities.md)
