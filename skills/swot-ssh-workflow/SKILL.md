---
name: swot-ssh-workflow
description: Makes a Cartopy map of the newest SWOT satellite sea surface height (SSH) pass over a region from the last 10 days, using only the swot-ssh MCP server. Use when the user asks for a map, plot or picture of recent or latest sea surface height, sea level, ocean eddies, fronts or currents seen from the SWOT satellite. Not for temperature or for the value at one place.
license: Apache-2.0
compatibility: Requires the swot-ssh MCP server connected to the client, network access, and an Earthdata Login (token in EARTHDATA_TOKEN or a urs.earthdata.nasa.gov entry in ~/.netrc) for the download step. Record the assistants you tested in submissions/test/submission.md.
allowed-tools: mcp__swot-ssh__find_swot_passes mcp__swot-ssh__fetch_swot_pass mcp__swot-ssh__draw_swot_map mcp__swot-ssh__list_swot_output_files
metadata:
  version: "0.1.0"
  catalog-id: swot-ssh-workflow
---

# Map the newest SWOT sea surface height pass

Guides an assistant through one fixed workflow: find SWOT passes over a region in the last 10 days, fetch the newest one, draw a map and list the files made. Each tool needs the output of the one before, and without a procedure an assistant tends to write its own download or plotting script.

## When to use

- "Show me a map of recent sea surface height off California."
- "Can you see any ocean eddies in the Gulf Stream from the latest SWOT data?"
- "Plot the newest sea level data from SWOT for the Mediterranean."

## When not to use

- Sea surface temperature or its maps. Use `sst-map-workflow` or `sst-latest-check`.
- The value at one place or time, such as "What is the sea level at Santa Monica pier?" SWOT gives swath snapshots, not point series.
- A daily gridded field, trends, animations or forecasts.
- Finding datasets or checking availability in general. Use `earth-data-discovery`.

## Required tools

From the MCP server **`swot-ssh`** (these four tools only):

| Tool | Use |
|---|---|
| `find_swot_passes` | List passes over the region: `south`, `north`, `west`, `east`, `days` = 10. |
| `fetch_swot_pass` | Download the newest pass and keep valid points in the region: `pass_name`, box, `variable`. |
| `draw_swot_map` | Draw the fetched pass: `pass_name`, same `variable`. |
| `list_swot_output_files` | List the files written. |

Assistants add their own prefix (Claude Code `mcp__swot-ssh__find_swot_passes`, Copilot `swot-ssh-find_swot_passes`, Codex `mcp__swot_ssh__find_swot_passes`). The `allowed-tools` header uses Claude Code names; other assistants ignore it.

**Use only these tools.** Never fall back to shell commands, Python scripts, plotting code you write yourself, or tools from other servers. If a tool is missing, not connected or fails, say which one and stop. Never ask the user to paste a token into the chat; if `fetch_swot_pass` reports missing credentials, relay its message about `EARTHDATA_TOKEN` or `~/.netrc` and stop. A new server only appears in a new session, so if the tools are missing, say that too.

## Procedure

1. **Get the region.** Ask for one if none was given: south, north, west, east in degrees (longitude -180 to 180, east positive, not crossing the dateline).
2. **Choose the variable.** Use `ssha_karin` (height anomaly) for eddies and fronts, which is the default for this skill. Use `ssh_karin` only if the user asks for it; it includes the geoid, so its values (for example about -30 m off California) are not ocean signal.
3. **Find passes.** Call `find_swot_passes` with the region and `days` 10. If none are listed, report that and stop. Take the pass with the newest start time. A listed pass may touch only a corner of the box.
4. **Fetch.** Call `fetch_swot_pass` for that pass with the same region and variable. Check that points were kept (`n_kept` above 0).
5. **Draw.** Call `draw_swot_map` with the same `pass_name` and `variable`.
6. **List files.** Call `list_swot_output_files`.
7. **Answer** using the format below.

If a step returns an error, quote it, explain the likely fix, and retry only with a corrected argument. If it still fails, stop and report what was completed.

## Expected output

1. **Result**: one sentence, for example "Mapped the newest SWOT pass over the California coast, 2026-11-04 19:21 to 20:13 UTC."
2. **Table**: region (south, north, west, east); pass name and start and end times (UTC); variable; units (m); value range; points in region, dropped as fill value, dropped by quality flag, kept; files made with sizes.
3. **Quality flags applied**: fill values masked, and points with any `ssh_karin_qual` flag set were dropped (as reported by the tool).
4. **Provenance**: source named in the tool results (NASA PO.DAAC SWOT_L2_LR_SSH_D, Version D, Basic product), and the date checked.
5. **Limitations**: SWOT is a swath measurement of sea surface height, not a daily gridded field; one pass is about 50 minutes and a box is revisited only every few days; `ssh_karin` includes the geoid.
6. **Tool trace**: tool names and arguments used.

## Assumptions

- The region is small enough for the tool limits and does not cross the dateline.
- The user has an Earthdata Login set up outside the chat.
- Cartopy can load coastline data (downloaded once, so the first map needs network access).

## Limitations

- One pass and one region per run; no gridding, animation or comparison with temperature.
- Files go to the server's `swot_output/` folder and are not removed automatically.

## Example tasks

- `/swot-ssh-workflow` (Claude Code, Copilot) or `$swot-ssh-workflow` (Codex): map the newest sea surface height pass over the California coast, 32 to 42 N and 128 to 117 W.
- "Are there eddies visible in the latest SWOT data south of Africa?"
- Not applicable: "What is the sea surface temperature near Hawaii?" The skill should not be used; it handles sea surface height only.
