# Tutorial 00 – Your first MCP tool call

| | |
|---|---|
| **Scientific purpose** | Get a trustworthy number (model bias against observations) from a tool rather than from the model's memory. |
| **Learning objective** | Make a successful MCP tool call three ways: from a plain client script over stdio, over Streamable HTTP, and through Claude Code. Name the client, server and tool in each case. |
| **Estimated time** | 30 minutes (5 if you completed [START_HERE](../START_HERE.md)) |
| **Starting state** | [Setup](../docs/setup.md) done: `uv`, `claude` installed; repository downloaded; `uv sync` run. |
| **Credentials** | Claude subscription sign-in for part C only. No other accounts. |

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

## B. The same server over Streamable HTTP

Terminal 1 (leave running):

```bash
uv run python servers/obs-model-starter/server.py --transport http
```

Expected: `starting obs-model-starter 0.1.0 on http://127.0.0.1:8765/mcp` and `Uvicorn running on http://127.0.0.1:8765`.

Terminal 2:

```bash
uv run python scripts/first_call.py --http http://127.0.0.1:8765/mcp
```

Same results as part A. Stop the server in terminal 1 with Ctrl+C. The scientific code is identical; only the transport changed. The server listens on `127.0.0.1`, so only your own laptop can reach it.

## C. Through Claude Code

```bash
uv run python scripts/install_skills.py
claude
```

1. Trust the folder; approve the project MCP servers `obs-model-starter` and `earthdata` ([why approval](../docs/troubleshooting.md#mcp-server-not-connected)).
2. Type `/mcp`. Expected: both listed as connected; `obs-model-starter` shows 3 tools.
3. Ask, without naming tools:

   ```text
   What sample datasets do you have access to through MCP, and what are their units?
   ```

   Expected: Claude asks permission to run `list_datasets` (shown as `obs-model-starter - list_datasets (MCP)`); after you approve, it lists three synthetic datasets: station observations in degC, model A in K, model B in degC.

4. Ask the scientific question:

   ```text
   Compare model A with the station observations at SYN-VALLEY.
   ```

   Expected: calls to `describe_dataset` and `compare_model_to_obs`; an answer with 23 pairs, bias ≈ −1.05 °C, RMSE ≈ 1.21 °C, the K→°C conversion, the excluded month 2020-07, a note that observations are points and model values are grid cells, and that the data are synthetic. Wording varies; the numbers must match part A.

## What you learned

| Part | Client | Server | Transport | Tool |
|---|---|---|---|---|
| A | `scripts/first_call.py` | obs-model-starter | stdio | `compare_model_to_obs` |
| B | `scripts/first_call.py` | obs-model-starter | Streamable HTTP | `compare_model_to_obs` |
| C | Claude Code | obs-model-starter | stdio (from `.mcp.json`) | chosen by the model |

## Exercise (5 minutes)

1. Run `uv run python scripts/first_call.py --site SYN-MOUNTAIN --model syn-model-b-tas-monthly`. Which months are excluded and why?
2. In Claude Code ask: "Is model A or model B closer to the observations at SYN-MOUNTAIN?" Check that both numbers match the script.

<details><summary>Answer for 1</summary>

`month_absent_from_obs: ['2020-12']` – the observation row is missing. Model B has no fill values. 23 valid pairs.
</details>

## Common errors and recovery

| Symptom | Cause | Fix |
|---|---|---|
| `uv: command not found` | Terminal opened before install | Open a new terminal; see [troubleshooting](../docs/troubleshooting.md#installation) |
| `FAILED: ... ConnectError` in part B | Server in terminal 1 not running, or different port | Start it; check the URL ends with `/mcp` |
| `address already in use` | Port 8765 taken | `--port 8780` on the server and the matching URL on the client |
| `/mcp` shows "pending approval" or nothing | Project servers not approved | Restart `claude` in the repository folder and approve; or see [troubleshooting](../docs/troubleshooting.md#mcp-server-not-connected) |
| `/mcp` shows `obs-model-starter` failed | `uv` not on Claude Code's PATH, or started outside the repository folder | Start `claude` from the repository root; [troubleshooting](../docs/troubleshooting.md#mcp-server-not-connected) |
| Claude answers without calling a tool | It answered from general knowledge | Say "use the obs-model-starter tools"; check the tool was approved |
| Usage limit message | Subscription limit reached | Continue with parts A and B; see [troubleshooting](../docs/troubleshooting.md#claude-sign-in-and-usage-limits) |

Next: [Tutorial 01 – Discover existing capabilities](01-discover-existing-capabilities.md)
