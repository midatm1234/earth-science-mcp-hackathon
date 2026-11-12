# sst-latest

Answers "what is the latest sea surface temperature data available?" (NASA CMR metadata), and makes a Cartopy map and a GIF animation of the newest days of the MUR SST analysis for a small region.

| Item | Value |
|---|---|
| Catalog id | `sst-latest` |
| Team | test |
| Version | 0.1.0 |
| Transports | stdio (default), Streamable HTTP (`--transport http`, `http://127.0.0.1:8766/mcp`) |
| Credentials | none |
| Network | two public services, no login: NASA CMR search API (`https://cmr.earthdata.nasa.gov/search`) and NOAA CoastWatch ERDDAP (`https://coastwatch.pfeg.noaa.gov/erddap`). Cartopy also downloads Natural Earth coastlines once, on first map |
| Data volume | one regional day is about 0.3 MB (coarse grid, at most 60,000 points per request); files go to `sst_output/` (git-ignored) |
| Typical runtime | about 1 second per call (not measured; depends on the network) |
| Dependencies | `mcp==2.3.0`; `cartopy==0.26.0` (map projections, coastlines), `matplotlib==3.11.2` (drawing), `pillow==13.0.0` (GIF writer). HTTP calls use the Python standard library |
| License | Apache-2.0 for code; test fixtures are CMR metadata, see `data/README.md` |

## Tools

| Tool | Purpose | Key inputs | Key outputs |
|---|---|---|---|
| `get_latest_sst_granule` | Find the newest granule of an SST collection (metadata only) | `collection_concept_id` (optional, default `C1996881146-POCLOUD`) | `collection`, `newest_granule` (name, start, end, age in hours), `date_checked`, `rules`, `provenance` |
| `get_newest_sst_dates` | List the newest daily MUR analyses | `days` (1 to 31, default 10) | `dates`, `newest`, `date_checked`, `source` |
| `fetch_sst_subset` | Fetch one day for a region and save it to `sst_output/` | `date`, `south`, `north`, `west`, `east` | saved file path and size, `n_points`, `grid_step_degrees`, min and max in degC |
| `draw_sst_map` | Draw a Cartopy PNG map of one fetched day | `date` | PNG path and size, value range in degC |
| `make_sst_gif` | Animate fetched days into a GIF with one shared colour scale | `dates` (2 to 31, same region) | GIF path and size, `n_frames`, `dates`, colour scale |
| `list_sst_output_files` | List the files written so far | none | paths and sizes |

Order for a map: `get_newest_sst_dates`, then `fetch_sst_subset` for each date, then `draw_sst_map` and `make_sst_gif`.

## Scientific conventions

| Topic | This server |
|---|---|
| Variables and units | `analysed_sst`, sea surface temperature in degC (the `get_latest_sst_granule` tool reads no values) |
| Coordinate convention | WGS84 degrees; longitude -180 to 180, east positive; regions may not cross the dateline |
| Spatial support | MUR is a 0.01 degree global grid; subsets are thinned to a coarser grid (step reported in the result) |
| Temporal support | daily analyses stamped 09:00 UTC; granule times as declared in CMR, UTC, ISO 8601 |
| Dataset / model version | read from CMR at call time (MUR v4.1 by default) |
| Missing data | land and missing ocean points (NaN) are dropped; a region with no valid points gives an error |
| Processing choices | "newest" = latest granule start time (CMR `sort_key=-start_date`); age = hours from granule end to `date_checked` |
| Provenance | NASA CMR (granule metadata) and NOAA ERDDAP dataset `jplMURSST41` (GHRSST MUR v4.1 L4); live calls; request URLs are returned |
| Interpretation limits | a gridded analysis (interpolated from satellite and in situ data), not station measurements; thinned grids hide small features; CMR can lag the data centre |

## Run it

```bash
uv run python servers/sst-latest/server.py --transport http
uv run pytest servers/sst-latest/tests
```

## Example

Input (all defaults):

```json
{}
```

Output (shortened; real values from a live call on 2026-11-12):

```json
{"collection": {"concept_id": "C1996881146-POCLOUD", "short_name": "MUR-JPL-L4-GLOB-v4.1", "version": "4.1"},
 "newest_granule": {"name": "20261110090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1",
                    "time_start": "2026-11-09T21:00:00Z", "time_end": "2026-11-10T21:00:00Z"},
 "date_checked": "2026-11-12T06:23:00Z"}
```

## Limitations

- Needs network access at run time; the tests do not.
- `get_latest_sst_granule` is metadata only. The map tools use real values, but only for small regions on a coarse grid; do not use them for scientific analysis of fine-scale features.
- Files are written to `sst_output/` and are not cleaned up automatically.
- A granule being listed does not mean the file is complete or downloadable without an Earthdata Login account.

See [CONTRIBUTING.md](../../CONTRIBUTING.md) and [the scientific quality checklist](../../docs/challenge-cards.md#scientific-quality-checklist).
