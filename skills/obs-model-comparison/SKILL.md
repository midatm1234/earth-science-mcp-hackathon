---
name: obs-model-comparison
description: Compares monthly model output with observations at a site using the obs-model-starter MCP tools, after checking units, time-stamp conventions, missing data and provenance, then explains bias and RMSE with limitations. Use when the user asks how well a model matches observations, wants model bias or RMSE at a station or site, or asks to evaluate or validate a model run against measurements from the sample datasets.
license: Apache-2.0
compatibility: Requires the obs-model-starter MCP server (servers/obs-model-starter) connected to the client. Written for Claude Code, GitHub Copilot and Codex; docs/compatibility.md records what was tested.
allowed-tools: mcp__obs-model-starter__list_datasets mcp__obs-model-starter__describe_dataset mcp__obs-model-starter__compare_model_to_obs
metadata:
  version: "0.1.0"
  catalog-id: obs-model-comparison
---

# Observation–model comparison

Guide a careful, reproducible comparison of a model run against observations using the `obs-model-starter` MCP tools. The skill supplies the procedure; the MCP server supplies the data and the arithmetic. Never compute statistics yourself from memory or invent numbers: every number in the answer must come from a tool result.

## When to use

- "How biased is model A at the mountain site?"
- "Compare model B with the station observations for 2021."
- "Which model run fits the valley observations better?"
- Any request for bias, RMSE or agreement between the sample model and observation datasets.

## When not to use

- Questions about finding new datasets, collections or granules: use the `earth-data-discovery` skill instead.
- General questions about climate, or about real places, that the synthetic sample data cannot answer. Say so plainly.
- Requests to download data or to compare variables other than those the server lists.

## Required tools

From the MCP server **`obs-model-starter`**:

| Tool | Use |
|---|---|
| `list_datasets` | find dataset ids and which are observations or models |
| `describe_dataset` | check units, time convention, sites, missing values, QC, provenance |
| `compare_model_to_obs` | compute aligned bias and RMSE |

Each assistant shows these with its own prefix, for example `mcp__obs-model-starter__compare_model_to_obs` (Claude Code), `obs-model-starter-compare_model_to_obs` (GitHub Copilot) or `mcp__obs_model_starter__compare_model_to_obs` (Codex). The `allowed-tools` header above uses Claude Code names; other assistants ignore it.

If these tools are not available, stop and tell the user: "The obs-model-starter MCP server is not connected. Check the MCP server list in your assistant, or see tutorials/00-first-tool-call.md." Do not fall back to guessing, and do not run the server's scripts through a shell instead.

## Procedure

1. **Select inputs.** Call `list_datasets`. Map the user's words to one observation dataset and one model dataset. If more than one model fits ("the model"), ask which one or compare each separately and say so.
2. **Check metadata.** Call `describe_dataset` for both datasets. Confirm and note:
   - same `variable`;
   - units of each, and that a conversion exists (for example K → degC);
   - time resolution is monthly for both, and the time-stamp convention of each (first of month vs mid-month);
   - the requested site exists in both, and its coverage, missing and QC-rejected counts;
   - `provenance.class` (state clearly if it is `synthetic`).
3. **Resolve the period.** Translate the user's period to `start`/`end` as `YYYY-MM`. If none was given, use the full overlap and say so. Do not set `include_suspect` unless the user asks to use suspect observations.
4. **Compare.** Call `compare_model_to_obs` with the chosen ids, `site_id`, and period. For several sites or models, make one call per combination.
5. **Check the result before explaining it.** Read `n_valid_pairs`, every non-empty list in `excluded`, `unit_conversion` and `warnings`. If a tool returns an error, quote it, explain the likely fix, and retry only with corrected arguments.
6. **Explain.** Use the output format below.

## Expected output

Write a short answer with these parts:

1. **Result**: one sentence, for example "Model A is on average 1.05 °C colder than the valley observations (RMSE 1.21 °C, 23 monthly pairs, 2020-01 to 2021-12)."
2. **Table** of the statistics per site/model: site, model, n pairs, mean bias, RMSE, units.
3. **How the comparison was made**: unit conversion applied, calendar-month matching rule, months excluded and why (missing value, QC, absent month).
4. **Provenance**: dataset ids, versions, provenance class, license.
5. **Limitations**: at least the representativeness of point vs grid cell, sample size if under 6 pairs, and that synthetic data say nothing about the real world.
6. **Tool trace**: the tool names and arguments used, so a reviewer can reproduce the answer.

Sign convention: a negative bias means the model is colder (lower) than the observations.

## Assumptions

- Both inputs are calendar-month means, so day-of-month labels can be ignored.
- The server's unit metadata are correct.
- Observations flagged other than `good` should be excluded by default.

## Limitations

- Only the variables, sites and datasets exposed by the server can be compared.
- Bias and RMSE alone do not show seasonal structure or significance; suggest further analysis instead of over-interpreting.
- The bundled data are synthetic; do not draw conclusions about real climate or real models.

## Example tasks

- `/obs-model-comparison` (Claude Code, Copilot) or `$obs-model-comparison` (Codex): Compare model A with the station observations at SYN-VALLEY.
- "Which of the two model runs is closer to the observations at the mountain site in 2021?"
- "What is the RMSE of model B at the coastal site if suspect observations are included?" (set `include_suspect=true` and highlight the change)
- Boundary case: "Compare model A at SYN-VALLEY for 2022." → the tool reports no rows; explain that the data cover 2020-01 to 2021-12.
