# Discovery record

Complete this **before** writing code. Both checks (A and B) are required. Mentors sign off at the bottom. Guidance: [docs/discovery-first.md](../../docs/discovery-first.md).

| Field | Value |
|---|---|
| Team | |
| Date checked | YYYY-MM-DD |
| Completed with | AI assistant (Copilot / Claude Code / Codex) + `earth-data-discovery` skill / plain MCP client (`scripts/earthdata_probe.py`) / manual |

## 1. Scientific question

<!-- One or two sentences a scientist would ask. Include variable, region, period. -->

## 2. Dataset or model source

<!-- e.g. "NASA MERRA-2 reanalysis via Earthdata (CMR)", "CMIP6 via ESGF (not in CMR)", "our group's WRF run on a lab server" -->

## 3. Collection or source identifiers

| Kind | Identifier | Version | DOI / citation |
|---|---|---|---|
| CMR collection concept id | e.g. C1276812859-GES_DISC | 5.12.4 | 10.5067/AP1B0BA5PD2K |
| Model run / ESGF dataset id / file path | | | |

## 4. Spatial and temporal requirements

| Item | Value |
|---|---|
| Region (WKT, **longitude first**) | e.g. `POLYGON((-121 33,-117 33,-117 38,-121 38,-121 33))` |
| Period (ISO 8601) | e.g. 2020-01-01 to 2020-12-31 |
| Spatial resolution / support needed | point, grid cell size, area mean |
| Temporal resolution / support needed | hourly, daily mean, monthly mean |

## 5. Availability verification

A collection's advertised coverage is not proof. Record the granule search (or, for data outside CMR, how you checked).

| Item | Value |
|---|---|
| Tool and arguments | e.g. `get_granules {collection_concept_id: ..., spatial_wkt_geometry: ..., temporal_start_date: ..., temporal_end_date: ...}` |
| Result | e.g. `total_hits: 12`; first `...202001.nc4`; last `...202012.nc4` |
| Status | verified / partially available (gaps: ...) / unverified (reason) / blocked (reason) |
| Access needs for the data itself | none / Earthdata Login (free) / other account / large download (size) |

## 6. Variables, services, software, citations

| Item | Value |
|---|---|
| Variable name(s) and units | e.g. `T2M`, K |
| Fill value, scale, offset | |
| Services (OPeNDAP, Harmony, WMS) | |
| Software / portals (Giovanni, Worldview, Panoply) | |
| Publications using the dataset (`get_citations`) | optional |

## 7. Existing capabilities considered

| Capability | Where | Does it already do what we need? |
|---|---|---|
| | hackathon catalog (`uv run python scripts/catalog.py search ...`) | |
| | Earthdata MCP tools | |
| | other MCP servers or skills you know | |

## 8. Decision

- [ ] **Reuse** – an existing tool/skill does it; we will write a skill or workflow around it.
- [ ] **Extend** – add a tool or option to an existing server (name it).
- [ ] **Build** – new small server, because (justify the gap).

## 9. Specific contribution

| Artifact | Name | One-line purpose |
|---|---|---|
| MCP tool(s) | | |
| Agent skill | | |
| Fixture data (≤ 1 MB, redistributable) | | |

## 10. Tool trace

<!-- Paste tool names and arguments used (or attach the probe JSON). Mark cached results as cached. -->

---

Mentor sign-off: ______  Date: ______  Notes: ______
