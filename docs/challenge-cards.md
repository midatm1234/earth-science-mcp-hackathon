# Challenge cards

Pick one card (or bring your own question in the same format). Every card produces **one small MCP contribution and one related skill**, extending the pretested starter where possible. Labels:

| Label | Values |
|---|---|
| Difficulty | ★ beginner · ★★ intermediate · ★★★ advanced (optional track) |
| Prerequisites | what you must have finished |
| Credentials | none, or what account (all core cards: **none**) |
| Data volume | what is read or bundled |
| Runtime | typical time per tool call on a laptop |
| Expected output | what the tool returns and what the skill reports |

All cards start with the [discovery record](../templates/discovery-record.md). None needs large downloads or a GPU.

## Observation cards

### O1 – Dataset discovery report ★

| | |
|---|---|
| Question | "Is there a suitable satellite or reanalysis product for variable X over region R in period P?" |
| Contribution | Skill only (reuse Earthdata MCP), or a tiny tool that turns a place name + bounding box into validated WKT (longitude first, closed ring, CCW) |
| Prerequisites | Tutorials 00–01 |
| Credentials | none |
| Data volume | metadata only (KB) |
| Runtime | 1–10 s per Earthdata call |
| Expected output | Filled discovery record with verified `total_hits`, identifiers, units; skill refuses to claim availability without a granule search |

### O2 – Regional station summary ★

| | |
|---|---|
| Question | "What is the mean, range and data completeness of observations at each site in a period?" |
| Contribution | `regional_summary(dataset_id, start, end, sites?)` on obs-model-starter: per-site n valid, % complete, mean/min/max with units; skill that flags sites below a completeness threshold |
| Prerequisites | Tutorials 00–02 |
| Credentials | none |
| Data volume | bundled fixture (8 KB) |
| Runtime | < 1 s |
| Expected output | Table per site with completeness and units; skill reports which sites are usable |

### O3 – Quality-control screen ★★

| | |
|---|---|
| Question | "Which observations look suspicious, and why?" |
| Contribution | `qc_screen(dataset_id, site_id, max_abs_anomaly)` returning months flagged by QC flag, missing value, or anomaly from the site's monthly climatology beyond a threshold; skill that explains flags and never deletes data silently |
| Prerequisites | Tutorials 00–02 |
| Credentials | none |
| Data volume | bundled fixture |
| Runtime | < 1 s |
| Expected output | List of flagged months with reason codes and thresholds used |

## Model cards

### M1 – Seasonal bias ★

| | |
|---|---|
| Question | "In which season is the model too warm or too cold?" |
| Contribution | `seasonal_bias` (worked example in [tutorial 02](../tutorials/02-build-an-mcp-tool.md)); skill that reports per-season bias with pair counts and warns about small samples |
| Prerequisites | Tutorials 00–02 |
| Credentials | none |
| Data volume | bundled fixture |
| Runtime | < 1 s |
| Expected output | DJF/MAM/JJA/SON bias in °C with n pairs |

### M2 – Compare two model runs ★★

| | |
|---|---|
| Question | "Is run B better than run A against observations, at every site?" |
| Contribution | `rank_models(obs_dataset_id, model_dataset_ids, sites)` returning bias/RMSE per run and site on a **common set of months** (pairs valid for all runs); skill that refuses to rank on different samples |
| Prerequisites | Tutorials 00–02 |
| Credentials | none |
| Data volume | bundled fixture |
| Runtime | < 1 s |
| Expected output | Table run × site with common n, bias, RMSE; statement of which run is closer and caveats |

### M3 – Bring your own model extract ★★

| | |
|---|---|
| Question | Your own model–observation question |
| Contribution | Add a dataset to the manifest from a small (≤ 1 MB), redistributable extract of your model and observations, with provenance; extend unit conversion if needed (e.g. precipitation kg m⁻² s⁻¹ → mm/day) |
| Prerequisites | Tutorials 00–02; data rights checked |
| Credentials | none in the repository (download outside it if needed) |
| Data volume | ≤ 1 MB per file |
| Runtime | < 2 s |
| Expected output | Comparison with correct units, time convention and provenance; data card filled |

### M4 – Earthdata-backed model check ★★★ (network)

| | |
|---|---|
| Question | "For a real reanalysis product, what spatial and temporal support and units would a comparison need?" |
| Contribution | Tool or skill that takes a CMR concept id and returns the comparison-relevant metadata (variable units, fill value, time resolution, grid from dimensions) using Earthdata MCP results, then checks compatibility with a local observation dataset |
| Prerequisites | Tutorials 00–04 |
| Credentials | none (metadata only) |
| Data volume | metadata only |
| Runtime | 2–10 s |
| Expected output | Compatibility report: unit conversion needed, time alignment rule, spatial support mismatch |

## Optional advanced card

### A1 – Spatial dependence and separation buffers ★★★ (optional)

| | |
|---|---|
| Question | "How far apart must training and test samples be so that spatial autocorrelation does not inflate test scores?" |
| Contribution | `estimate_spatial_dependence(grid, resolution_m, max_lag_m)` on a small synthetic or redistributable continuous field: empirical semivariogram in distance bins with pair counts, a fitted model (e.g. spherical: nugget, sill, practical range), and the correlation `rho(h) = 1 - gamma(h)/var` at a requested buffer; skill that proposes a buffer, reports evidence, and states limits |
| Prerequisites | Tutorials 00–03; comfort with NumPy (add `numpy==<version>` pinned) |
| Credentials | none |
| Data volume | ≤ 1 MB field (e.g. 200 × 200 float32) |
| Runtime | 1–10 s |
| Expected output | Binned semivariogram with counts, fitted range with fit diagnostics, rho at the buffer, recommendation with caveats |

Methods to estimate dependence: empirical semivariogram/correlogram with pair counts per lag bin; fitting a variogram model and reporting its practical range; Moran's I at increasing lags; comparing block cross-validation scores at increasing buffer widths. Assessing a separation buffer: report rho (or Moran's I) at the buffer distance, the fitted range, and how much data the buffer removes.

**Do not promise independence.** A buffer beyond the estimated range reduces, but does not guarantee the absence of, dependence: the estimate assumes approximate stationarity and isotropy, depends on the variable and season analysed, is affected by trends and by masked (cloudy) pixels, and a range estimated from one continuous band does not transfer automatically to labels or other bands. This card adapts ideas from the EVE Team 3 spatial-analysis project (see [reference review](reference-review.md#supplied-eve-materials)); its imagery, CNN training and large notebook are intentionally not part of the default starter.

## Scientific quality checklist

Every contribution's README and every skill's output must state:

| Item | Question to answer |
|---|---|
| Units | What units go in and come out? Are conversions applied and stated? |
| Coordinate conventions | Datum (WGS84?), longitude range (−180…180 or 0…360), lat/lon order |
| Spatial support | Point, grid cell (size), area mean, swath? Is a point compared with an area? |
| Temporal support | Instantaneous, daily, monthly mean? Time-stamp convention (start, middle, end)? Calendar? Time zone? |
| Dataset / model version | Version, DOI, run id, retrieval date |
| Missing data | Fill values, QC flags, what is excluded and reported |
| Processing choices | Aggregation, thresholds, regridding, pairing rules |
| Provenance | Synthetic, cached live response, recorded demonstration, or live call |
| Interpretation limits | What the result does **not** show (significance, representativeness, generalisation) |
