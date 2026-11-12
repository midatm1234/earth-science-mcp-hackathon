---
name: sst-latest-check
description: Reports how current the sea surface temperature (SST) data are, using the sst-latest MCP server to find the newest granule in NASA's CMR (default GHRSST MUR L4 global). Use when the user asks how current, recent or up to date sea surface temperature data are, what the latest or newest SST data available is, or when SST data were last updated.
license: Apache-2.0
compatibility: Requires the sst-latest MCP server connected to the client. Record the assistants you tested in submissions/test/submission.md.
allowed-tools: mcp__sst-latest__get_latest_sst_granule
metadata:
  version: "0.1.0"
  catalog-id: sst-latest-check
---

# Check how current the sea surface temperature data are

Answers "how current are the SST data?" by calling one tool that reads NASA's Common Metadata Repository (CMR) and returns the newest granule of an SST collection. Without a procedure, an assistant tends to answer from memory with a date it cannot know; this skill makes it report only what the tool returned, with the date it was checked.

## When to use

- "How current is the global sea surface temperature data from NASA?"
- "What is the latest SST data available?"
- "When was the MUR sea surface temperature product last updated?"

## When not to use

- Questions about temperature values at a place or time, such as "What was the SST at Santa Monica pier yesterday?" This skill reports which data exist, not the values.
- Forecasts of future sea surface temperature.
- Searching for or comparing SST collections, or checking data for a region and period. Use the `earth-data-discovery` skill.
- Comparing model output with observations. Use the `obs-model-comparison` skill.

## Required tools

From the MCP server **`sst-latest`**:

| Tool | Use |
|---|---|
| `get_latest_sst_granule` | Find the newest granule of an SST collection in NASA CMR. Optional input `collection_concept_id` (default `C1996881146-POCLOUD`, GHRSST MUR L4 global). |

Assistants add their own prefix (Claude Code `mcp__sst-latest__get_latest_sst_granule`, Copilot `sst-latest-get_latest_sst_granule`, Codex `mcp__sst_latest__get_latest_sst_granule`). The `allowed-tools` header uses Claude Code names; other assistants ignore it.

If this tool is not available, stop and say: "The sst-latest MCP server is not connected. Check the MCP server list in your assistant, and start a new session if the server was added recently." Do not guess a date, do not run the server's scripts through a shell, and do not substitute another tool.

## Procedure

1. **Select input.** If the user names a collection by concept id (for example `C1996881146-POCLOUD`), pass it as `collection_concept_id`. Otherwise call the tool with no arguments to use the default global MUR product.
2. **Call `get_latest_sst_granule`.**
3. **Check the result.** If the tool returns an error, quote it, explain the likely fix (for example a wrong collection id, or NASA CMR not reachable), and retry only with a corrected argument. Do not report a date the tool did not return.
4. **Explain** using the output format below.

## Expected output

1. **Result**: one sentence, for example "The newest MUR SST granule ends 2026-11-10T21:00Z, about 33 hours before the check on 2026-11-12."
2. **Table**: collection (id, short name, title, version); newest granule name; start and end time (UTC); age in hours; date checked.
3. **Method**: "newest" means the latest granule start time in CMR; age is measured from the granule end time to the date checked.
4. **Provenance**: NASA CMR search API, a live call; the tool returns the request URLs.
5. **Limitations**: this is metadata only, so it says which data exist and not the temperature values; CMR can lag the data centre; a listed granule may still need an Earthdata Login to download.
6. **Tool trace**: the tool name and arguments used.

## Assumptions

- The tool's `date_checked` and granule times are in UTC.
- CMR's declared time span for the granule is correct.

## Limitations

- Needs network access to NASA CMR when the tool runs.
- Reports on one collection per call; it does not compare products.
- Says nothing about data quality, cloud contamination or the temperature values.

## Example tasks

- `/sst-latest-check` (Claude Code, Copilot) or `$sst-latest-check` (Codex): how current is the global sea surface temperature data?
- "What is the newest SST data NASA has available?"
- Not applicable: "What was the sea surface temperature at Santa Monica pier yesterday?" The skill should not be used; it reports data availability, not values.
