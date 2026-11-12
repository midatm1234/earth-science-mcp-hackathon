---
name: sst-map-workflow
description: Makes a Cartopy map and a 10-day GIF animation of recent sea surface temperature (SST) for a region, using only the sst-latest MCP server (NOAA MUR analysis). Use when the user asks for a map, plot, picture or animation of recent, latest or newest sea surface temperature, an SST map or GIF for the last 10 days, or how the ocean surface temperature changed over the past days in a region.
license: Apache-2.0
compatibility: Requires the sst-latest MCP server connected to the client, with network access. Record the assistants you tested in submissions/test/submission.md.
allowed-tools: mcp__sst-latest__get_newest_sst_dates mcp__sst-latest__fetch_sst_subset mcp__sst-latest__draw_sst_map mcp__sst-latest__make_sst_gif mcp__sst-latest__list_sst_output_files
metadata:
  version: "0.1.0"
  catalog-id: sst-map-workflow
---

# Map and animate recent sea surface temperature

Guides an assistant through one fixed workflow: find the newest available day, fetch a small regional subset for the last 10 days, draw a map of the newest day, make a GIF of all 10 days, and list the files. The order matters (each tool needs the output of the one before), and without a procedure an assistant tends to write its own plotting script instead of using the tools.

## When to use

- "Make a map of the latest sea surface temperature off the California coast."
- "Animate the last 10 days of SST for the Gulf of Mexico."
- "Show me how the ocean surface temperature changed this week near Japan."

## When not to use

- The temperature at one place or time, such as "What was the SST at Santa Monica pier yesterday?" This skill draws gridded maps, not point values.
- Forecasts of future sea surface temperature.
- Finding out how current the data are without making a map. Use the `sst-latest-check` skill.
- Searching for datasets or checking availability. Use the `earth-data-discovery` skill.
- Comparing model output with observations. Use the `obs-model-comparison` skill.

## Required tools

From the MCP server **`sst-latest`** (these five tools only):

| Tool | Use |
|---|---|
| `get_newest_sst_dates` | List the newest daily dates (`days` = 10). |
| `fetch_sst_subset` | Fetch and save one day for the region: `date`, `south`, `north`, `west`, `east`. |
| `draw_sst_map` | Draw a Cartopy PNG for one fetched `date`. |
| `make_sst_gif` | Animate fetched `dates` (2 to 31, same region) into a GIF. |
| `list_sst_output_files` | List the files written. |

Assistants add their own prefix (Claude Code `mcp__sst-latest__fetch_sst_subset`, Copilot `sst-latest-fetch_sst_subset`, Codex `mcp__sst_latest__fetch_sst_subset`). The `allowed-tools` header uses Claude Code names; other assistants ignore it.

**Use only these tools.** Never fall back to shell commands, Python scripts, plotting code you write yourself, or tools from other servers. If a tool is missing, not connected or fails, say which one and stop. Do not guess dates or values. A new server only appears in a new session, so if the tools are missing, say that too.

## Procedure

1. **Get the region.** Ask the user for a region if none was given, as south, north, west and east in degrees (longitude -180 to 180, east positive, each side at most 40 degrees, not crossing the dateline).
2. **Find the newest day.** Call `get_newest_sst_dates` with `days` 10. Keep the 10 dates it returns.
3. **Fetch.** Call `fetch_sst_subset` once for each of the 10 dates, with the same region every time. Check each result for `n_points` above 0.
4. **Draw the map.** Call `draw_sst_map` for the newest date.
5. **Make the GIF.** Call `make_sst_gif` with all 10 dates.
6. **List the files.** Call `list_sst_output_files`.
7. **Explain** using the output format below.

If a step returns an error, quote it, explain the likely fix (for example a region that is too large or a date not fetched), and retry only with a corrected argument. If it still fails, stop and report what was completed.

## Expected output

1. **Result**: one sentence, for example "Made a map for 2026-11-10 and a 10-frame GIF for 2026-11-01 to 2026-11-10 off the California coast."
2. **Table**: region (south, north, west, east), dates covered, number of frames, value range in degC, file paths with sizes.
3. **Method**: daily MUR analysis, fetched on a thinned grid (the step is in the tool result); one shared colour scale across all frames.
4. **Provenance**: the source named in the tool results (NOAA CoastWatch ERDDAP, dataset jplMURSST41, GHRSST MUR v4.1 L4) and the date checked.
5. **Limitations**: an SST map shows a gridded analysis, not station measurements; the thinned grid hides small features; the data are as of the newest available day, which can lag real time.
6. **Tool trace**: the tool names and arguments used.

## Assumptions

- The region is small enough for the tool limits.
- The newest 10 days returned by `get_newest_sst_dates` are consecutive days.
- Cartopy can load its coastline data (it downloads it once, so the first map needs network access).

## Limitations

- One region per run; all frames use the same region.
- Not for point values, trends, anomalies or forecasts.
- Files are written to the server's `sst_output/` folder and are not removed automatically.

## Example tasks

- `/sst-map-workflow` (Claude Code, Copilot) or `$sst-map-workflow` (Codex): make a map and a 10-day animation of sea surface temperature for the California coast.
- "Show me the last 10 days of ocean surface temperature near Hawaii as a GIF."
- Not applicable: "What was the sea surface temperature at Santa Monica pier yesterday?" The skill should not be used; it makes gridded maps, not point values.
