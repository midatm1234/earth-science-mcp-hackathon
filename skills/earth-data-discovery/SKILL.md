---
name: earth-data-discovery
description: Runs a discovery-first check before building anything - finds candidate NASA Earthdata collections, verifies granule availability for the requested region and period, inspects variables, services, software and citation information with the Earthdata MCP tools, searches the hackathon catalog for existing MCP servers and skills, and fills in a discovery record with a reuse, extend or build decision. Use when a team asks which dataset to use, whether data exist for a place and time, or whether a capability already exists before writing new code.
license: Apache-2.0
compatibility: Requires network access and the public Earthdata MCP server (https://cmr.earthdata.nasa.gov/mcp/v1) connected as "earthdata". Catalog search reads files in this repository. Written for Claude Code, GitHub Copilot and Codex; docs/compatibility.md records what was tested.
allowed-tools: mcp__earthdata__get_keywords mcp__earthdata__get_collections mcp__earthdata__get_granules mcp__earthdata__get_variables mcp__earthdata__get_services mcp__earthdata__get_tools mcp__earthdata__get_citations Read Grep Glob
metadata:
  version: "0.1.0"
  catalog-id: earth-data-discovery
---

# Discovery first

Before a team writes a new MCP tool, establish (A) that suitable data exist and are available for the requested region and period, and (B) that the capability does not already exist. The result is a filled-in discovery record (structure in `templates/discovery-record.md` at the repository root).

## When to use

- "Is there monthly 2 m temperature for central California in 2020?"
- "Which dataset should we use for soil moisture over the Sahel?"
- "Does a tool for X already exist in the hackathon catalog?"
- At the start of any team project, before editing code.

## When not to use

- Comparing the bundled sample datasets: use `obs-model-comparison`.
- Downloading data. This skill does metadata discovery only. Downloading needs an Earthdata Login account and is a separate, explicit step.

## Required tools

From the MCP server **`earthdata`** (NASA Earthdata MCP):

| Tool | Use |
|---|---|
| `get_keywords` | translate everyday words ("rain") into official GCMD science keywords |
| `get_collections` | find candidate collections (datasets); always set `has_granules: true` |
| `get_granules` | verify actual files exist for the region and period |
| `get_variables` | variable names, units, fill values, scale/offset |
| `get_services` | subsetting/access services (OPeNDAP, Harmony, WMS) |
| `get_tools` | portals and software (Giovanni, Worldview, Panoply) |
| `get_citations` | publications associated with a collection |

Plus the assistant's own file search and read tools for `catalog/entries/` and `catalog/index.md`. Each assistant shows MCP tools with its own prefix (for example `mcp__earthdata__get_granules` in Claude Code and Codex, `earthdata-get_granules` in GitHub Copilot). The `allowed-tools` header uses Claude Code names; other assistants ignore it.

If the Earthdata tools are unavailable (offline, server down), say so, continue with part B, and mark part A **blocked** in the record. The file `examples/data/cached/earthdata_discovery_merra2_t2m.json` is a dated cached example for practice only; never present it as current availability.

## Procedure

### A. Data discovery with Earthdata MCP

1. Restate the scientific question, variable, region and period. Convert the region to WKT with **longitude first** and a counter-clockwise ring, e.g. `POLYGON((-121 33,-117 33,-117 38,-121 38,-121 33))`. Convert dates to ISO 8601.
2. If the variable is described in everyday words, call `get_keywords` first.
3. Call `get_collections` with `has_granules: true`, a keyword or short name, and the period. Keep `limit` small (3–5). Record `concept_id`, short name, version, DOI, time and spatial coverage, processing level.
4. For the best one or two collections, call `get_granules` with `collection_concept_id`, the WKT geometry and the period. Record `total_hits` and the first and last granule time. A collection that claims global coverage can still have gaps; only granules prove availability.
5. Call `get_variables` (keyword = variable name) for units, fill values, scale and offset. Call `get_services` and `get_tools` for access and subsetting options. Call `get_citations` if publications are useful.
6. Record the DOI from the collection record as the dataset citation. `get_citations` returns publications that use the dataset, not the dataset citation itself.

### Model data not indexed in Earthdata

Many Earth system model outputs (for example CMIP via ESGF, Copernicus CDS reanalyses, institutional model archives, local runs) are not in NASA CMR. Do not conclude "no data" from an empty Earthdata result. Instead record the source manually: archive or catalog name, experiment/run identifier, model version, variable name and units, grid and calendar, time-stamp convention, access method and license. Mark availability as "verified by <method>" (for example a catalog listing or a file header) or "unverified".

### B. Existing capability search

7. Search this repository's catalog: search `catalog/entries/*.yaml` for the variable, method and dataset names, and read `catalog/index.md`. List matching servers and skills with their ids and `status.review`.
8. Note relevant external servers the team knows of (for example the Earthdata MCP tools themselves, or registry servers). Earthdata MCP is a dataset search service, not a registry of MCP servers or skills.

### C. Decision

9. Decide **reuse** (an existing tool does it), **extend** (add a tool or option to an existing server), or **build** (new server), and state the specific, small contribution.

## Expected output

A filled discovery record with these headings, in Markdown:

1. Scientific question
2. Dataset or model source
3. Collection or source identifiers (concept ids, DOIs, run ids)
4. Spatial and temporal requirements (WKT, ISO dates, resolution)
5. Availability verification (tool, arguments, `total_hits`, first/last granule, date checked) — or "blocked"/"unverified" with reason
6. Variables, units, fill values, services and software found
7. Existing capabilities considered (catalog ids and external servers)
8. Decision: reuse, extend or build, with justification
9. Specific contribution the team intends to make
10. Tool trace (tool names and arguments)

## Assumptions

- Metadata in CMR are accurate enough for planning; values are not inspected.
- Discovery results are a snapshot; record the date.

## Limitations

- Metadata discovery does not download or open data and does not prove the data are scientifically suitable.
- Earthdata MCP covers NASA CMR holdings only.
- Catalog search finds only contributions registered in this repository.

## Example tasks

- `/earth-data-discovery` (Claude Code, Copilot) or `$earth-data-discovery` (Codex): monthly 2 m air temperature, central California, 2020.
- "Before we build a precipitation tool for the Sahel 2010–2020, check data availability and whether something similar exists."
- Not applicable: "Compute model A bias at SYN-VALLEY" → use `obs-model-comparison`.
