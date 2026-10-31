# Tutorial 01 – Discover existing capabilities

| | |
|---|---|
| **Scientific purpose** | Before building anything, establish that suitable data exist for your region and period, and that nobody has already built the capability. |
| **Learning objective** | Use Earthdata MCP to find a collection, verify granules for a region and period, and inspect variables, services, software and citations; search the hackathon catalog; complete a [discovery record](../templates/discovery-record.md) with a reuse/extend/build decision. |
| **Estimated time** | 45 minutes |
| **Starting state** | [Tutorial 00](00-first-tool-call.md) done. Network access. `earthdata` approved in Claude Code. Your team has a rough question (see [challenge cards](../docs/challenge-cards.md)). |
| **Credentials** | None. Earthdata metadata search is open. Downloading files (not done here) needs a free Earthdata Login. |

Background: [docs/discovery-first.md](../docs/discovery-first.md) explains the two required checks, the route for model data outside Earthdata, and why metadata discovery is not data access.

## Step 1 – Create your team's folder (2 minutes)

One person per team runs (choose short lowercase names with hyphens):

```bash
uv run python scripts/new_contribution.py --team <team-slug> --server <server-name> --skill <skill-name>
```

Example: `--team river-rats --server river-flow-tools --skill river-flow-check`. This creates `submissions/<team>/discovery-record.md` and runnable starter folders. If your team will **extend** `obs-model-starter` instead of building a new server, use only `--skill <name> --uses-server obs-model-starter`.

## Step 2 – Check A: data discovery with Earthdata MCP (20 minutes)

### Option 1: Claude Code with the discovery skill (recommended)

```bash
claude
```

```text
/earth-data-discovery Is monthly 2 m air temperature from MERRA-2 available for central California, POLYGON((-121 33,-117 33,-117 38,-121 38,-121 33)), in 2020?
```

Replace the variable, region and period with your team's. Approve the `earthdata` tool calls.

Expected (for the example; numbers as of 2026-10-30): the skill calls `get_collections` (finds `C1276812859-GES_DISC`, short name `M2TMNXSLV`, version 5.12.4, DOI `10.5067/AP1B0BA5PD2K`), `get_granules` (12 granules for 2020, `...202001.nc4` to `...202012.nc4`), `get_variables` (`T2M`, units `K`, fill value about `1e15`), `get_services` (Harmony and OPeNDAP), and fills the discovery-record headings.

### Option 2: plain MCP client, no AI

```bash
uv run python scripts/earthdata_probe.py --short-name M2TMNXSLV \
  --wkt "POLYGON((-121 33,-117 33,-117 38,-121 38,-121 33))" \
  --start 2020-01-01 --end 2020-12-31 --variable T2M
```

(Windows PowerShell: put the command on one line, or end lines with a backtick `` ` `` instead of `\`.) Use `--keyword "precipitation monthly"` instead of `--short-name` when you do not know the short name. Add `--save submissions/<team>/earthdata.json` to keep the evidence.

Expected: JSON with `"total_hits": 1` for collections and `"total_hits": 12` for granules, plus variables, services and citations.

### Offline fallback

If the network or Earthdata is unavailable, open the dated cached example [earthdata_discovery_merra2_t2m.json](../examples/data/cached/earthdata_discovery_merra2_t2m.json) to practise reading results, and mark section 5 of your record **blocked** until you can repeat the live check.

### Data outside Earthdata

If your model output lives elsewhere (CMIP6 on ESGF, Copernicus CDS, a lab server, your own run), record the source, run id, version, variable, units, grid, calendar and how you verified the files exist. See [discovery-first.md](../docs/discovery-first.md#model-data-not-indexed-in-earthdata).

## Step 3 – Check B: existing capabilities (10 minutes)

```bash
uv run python scripts/catalog.py search temperature
uv run python scripts/catalog.py search bias
```

Expected: `obs-model-starter` (bias/RMSE at a site) and the Earthdata entries. Also read [catalog/index.md](../catalog/index.md) and think about other MCP servers you know. Note what already exists and what is missing.

In Claude Code you can ask: `Search this repository's catalog for anything that computes seasonal cycles or anomalies.`

## Step 4 – Decide and record (10 minutes)

Open `submissions/<team>/discovery-record.md` and fill in all ten sections. Choose **reuse**, **extend** or **build**, and write a single, small, specific contribution, for example:

> Extend: add `seasonal_bias` to obs-model-starter, returning mean bias per season (DJF/MAM/JJA/SON) with pair counts, plus a skill that interprets seasonal bias.

Ask a mentor to sign off before you change code.

## Example prompt

```text
/earth-data-discovery We want to compare a regional model's daily precipitation with satellite estimates over the Ganges basin for the 2019 monsoon. Check availability and whether anything in the catalog already does this.
```

## Expected output

A completed discovery record: question; source; identifiers; WKT and ISO period; granule search with `total_hits` and first/last granule, dated; variables/units/fill values; services and software; capabilities considered; decision; contribution; tool trace.

## Exercise (10 minutes)

Run the discovery for a different variable your team cares about (for example "sea surface temperature", "soil moisture", "aerosol optical depth"). Use `get_keywords` (or `--keyword`) first. How many collections have granules in your region and period? Which one would you choose and why (resolution, period, processing level)?

## Common errors and recovery

| Symptom | Cause | Fix |
|---|---|---|
| 0 collections | Words too specific; CMR requires every word to match | Fewer words, or ask the skill to use `get_keywords` first |
| Many irrelevant collections | Missing `has_granules: true` or too broad keyword | Add instrument, platform or short name |
| 0 granules but collection looks right | Region or period outside coverage; latitude/longitude swapped | WKT is **longitude first**; check the polygon closes on its first point |
| Thousands of granules | Daily/hourly product over a long period | That's fine for discovery: record `total_hits`; narrow the period |
| `Could not reach https://cmr.earthdata.nasa.gov/mcp/v1` | Network/proxy | Use the cached example; mark section 5 blocked; see [troubleshooting](../docs/troubleshooting.md#network-proxy-and-certificates) |
| "I'll download it for you" | Agent going beyond discovery | Stop it: downloading needs Earthdata Login and is a separate step |

Next: [Tutorial 02 – Build an MCP tool](02-build-an-mcp-tool.md)
