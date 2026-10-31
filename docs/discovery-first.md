# Discovery first

Every team completes two checks **before** writing code, and records them in a [discovery record](../templates/discovery-record.md) that a mentor signs off. The [`earth-data-discovery`](../skills/earth-data-discovery/SKILL.md) skill and [tutorial 01](../tutorials/01-discover-existing-capabilities.md) walk through it.

## Why

- A collection that advertises global, multi-decade coverage can still have no files for your region or period. Only a granule search proves availability.
- Building a tool that already exists wastes the day; extending one is usually the better contribution.
- Writing down identifiers, versions and dates makes the result reproducible and citable.

## Check A – Data discovery with Earthdata MCP

Earthdata MCP is NASA's public MCP server over the Common Metadata Repository (CMR), at `https://cmr.earthdata.nasa.gov/mcp/v1` (no account needed for search). It is already configured in [.mcp.json](../.mcp.json) as `earthdata`.

| Step | Tool | Record |
|---|---|---|
| Translate everyday words to science keywords | `get_keywords` | the GCMD keyword used |
| Find candidate collections (with `has_granules: true`) | `get_collections` | concept id, short name, version, DOI, coverage, processing level |
| **Verify availability** for region and period | `get_granules` | `total_hits`, first/last granule, date checked |
| Inspect variables | `get_variables` | name, units, fill value, scale/offset |
| Access and subsetting services | `get_services` | OPeNDAP, Harmony, WMS |
| Software and portals | `get_tools` | Giovanni, Worldview, Panoply, … |
| Publications using the dataset | `get_citations` | optional; the dataset's own citation is the DOI from the collection |

Conventions: WKT geometry is **longitude first** with a counter-clockwise, closed ring; dates are ISO 8601 (`2020-01-01T00:00:00Z`).

Worked example (live on 2026-10-30, saved as a dated cached response in [examples/data/cached/](../examples/data/cached/earthdata_discovery_merra2_t2m.json)): MERRA-2 `M2TMNXSLV` (`C1276812859-GES_DISC`, DOI 10.5067/AP1B0BA5PD2K) has 12 monthly granules for 2020 intersecting `POLYGON((-121 33,-117 33,-117 38,-121 38,-121 33))`; variable `T2M` is in K with a fill value of about 1e15; Harmony and OPeNDAP services are available.

## Check B – Existing capabilities

| Where | How |
|---|---|
| Hackathon catalog | `uv run python scripts/catalog.py search <words>`; [catalog/index.md](../catalog/index.md) |
| Earthdata MCP tools themselves | Do they already answer the question (e.g. availability)? |
| Other MCP servers and skills the team knows | For example servers in the [EVE MCP tool registry](https://github.com/eve-esa/mcp-tool-registry) |

Earthdata MCP finds **datasets**. It is not a registry of MCP servers or agent skills; use the catalog for that.

Decision: **reuse** (existing tool suffices; contribute a skill or workflow), **extend** (add a tool or option to an existing server), or **build** (new small server, justified gap).

## Model data not indexed in Earthdata

Many Earth system model outputs are not in CMR: CMIP6 (ESGF nodes), Copernicus Climate Data Store reanalyses and projections, institutional archives, and a group's own runs. An empty Earthdata search does not mean "no data". Record instead:

| Field | Example |
|---|---|
| Archive or catalog | ESGF (CMIP6), Copernicus CDS, lab THREDDS server, local disk |
| Identifiers | CMIP6 `source_id`, `experiment_id`, `variant_label`, `table_id`; CDS dataset name; run id |
| Model and version | e.g. model name + version, configuration |
| Variable, units, grid, calendar | `tas`, K, 1° lat-lon, `noleap` calendar |
| Time-stamp convention | mid-month stamps, period bounds (`time_bnds`) |
| How availability was verified | catalog listing, file header (`ncdump -h`), STAC search, or "unverified" |
| Access and license | account needed? license and citation text |

Use a small, redistributable extract (≤ 1 MB) or a synthetic stand-in as the tool's fixture. Keep the real-data access path in the README.

## Metadata discovery is not data access

| | Metadata discovery | Authenticated data access |
|---|---|---|
| What | Search descriptions of datasets and files | Download or stream the files themselves |
| Account | none | free Earthdata Login (most NASA data); other archives have their own |
| Tooling here | Earthdata MCP, `earthdata_probe.py`, the discovery skill | Not part of the core workshop; `earthaccess` Python library is the usual route |
| Size | kilobytes | megabytes to terabytes |

Do not put Earthdata credentials in files or in tests. If a team needs downloads, do them interactively (`earthaccess.login()`), keep the data out of the repository, and bundle only a small redistributable extract with provenance.
