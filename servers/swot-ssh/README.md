# swot-ssh

Finds SWOT KaRIn sea surface height passes over a region (public NASA CMR metadata), downloads one pass with an Earthdata Login, cuts out the region and draws a Cartopy map of the swath.

| Item | Value |
|---|---|
| Catalog id | `swot-ssh` |
| Team | test |
| Version | 0.1.0 |
| Transports | stdio (default), Streamable HTTP (`--transport http`, `http://127.0.0.1:8766/mcp`) |
| Credentials | Earthdata Login: user token in the environment variable `EARTHDATA_TOKEN`, or a `machine urs.earthdata.nasa.gov` entry in `~/.netrc` (`chmod 600`). Free account at https://urs.earthdata.nasa.gov. Only `fetch_swot_pass` needs it. Never stored in the repository, logged or returned |
| Network | NASA CMR search API (public) and NASA PO.DAAC SWOT archive (login). Cartopy also downloads Natural Earth coastlines once, on first map |
| Data volume | one pass is about 9 MB to download and is deleted after the region is cut out; the saved subset is a few hundred KB; files go to `swot_output/` (git-ignored) |
| Typical runtime | tens of seconds per pass, network dependent (not measured) |
| Dependencies | `mcp==2.3.0`; `netcdf4==1.7.5.1.post1` (reads SWOT NetCDF), `cartopy==0.26.0`, `matplotlib==3.11.2` (maps) |
| License | Apache-2.0 for code; test data are invented, see `data/README.md` |

## Tools

| Tool | Purpose | Key inputs | Key outputs |
|---|---|---|---|
| `find_swot_passes` | List Basic passes whose footprint overlaps a box in the last days (no login) | `south`, `north`, `west`, `east`, `days` (1 to 30, default 10) | `passes` (name, cycle, pass, start, end, size MB), `date_checked`, `query` |
| `fetch_swot_pass` | Download one pass, keep the region's valid points, save them | `pass_name`, box, `variable` (`ssh_karin` or `ssha_karin`) | saved file path and size, point counts (in region, fill dropped, flag dropped, kept), min and max in m, rules |
| `draw_swot_map` | Draw a fetched pass as coloured swath points on a Cartopy map | `pass_name`, `variable` | PNG path and size, point count, value range in m, `drawn_as` |
| `list_swot_output_files` | List the files written so far | none | paths and sizes |

Order: `find_swot_passes`, then `fetch_swot_pass` for a pass, then `draw_swot_map`.

## Scientific conventions

| Topic | This server |
|---|---|
| Variables and units | `ssh_karin`: sea surface height above the reference ellipsoid, **includes the geoid**, metres (values around -30 m off California are geoid, not ocean signal). `ssha_karin`: height anomaly after removing mean sea surface, tides and the dynamic atmospheric correction, metres. Use `ssha_karin` to look at eddies and fronts |
| Product | SWOT_L2_LR_SSH_D, Version D, **Basic** (smoothed, 2 km) only; the Expert, WindWave and Unsmoothed products are ignored |
| Coordinate convention | WGS84 degrees; SWOT longitudes (0 to 360) are converted to -180 to 180, east positive; boxes may not cross the dateline |
| Spatial support | irregular swath pixels on 2 km along- and across-track spacing, left and right swaths; drawn as points, not interpolated onto a grid |
| Temporal support | one pass is about 50 minutes; times are the granule start and end from the file name, UTC. A box is revisited only every few days |
| Dataset / model version | Version D, collection `C3233945000-POCLOUD` |
| Missing data | the file's own fill value is masked; points with any `ssh_karin_qual` flag set (value not 0) are dropped; masked flags count as flagged. Counts of what was dropped are returned |
| Processing choices | the full pass is deleted after the region is saved; no tide, geoid or other corrections are added or removed here |
| Provenance | NASA PO.DAAC SWOT_L2_LR_SSH_D; request URL returned by `find_swot_passes`; live calls |
| Interpretation limits | swath snapshots, not daily maps; a pass listed for a box may touch only a corner; the flag rule is deliberately strict (any flag) |

## Run it

```bash
uv run python servers/swot-ssh/server.py --transport http
uv run pytest servers/swot-ssh/tests
```

## Example

Input to `fetch_swot_pass` (California coast, one pass from `find_swot_passes`):

```json
{"pass_name": "SWOT_L2_LR_SSH_Basic_058_373_20261104T192133_20261104T201301_PID0_01",
 "south": 32, "north": 42, "west": -128, "east": -117}
```

Output (shortened; real values from a live call on 2026-11-12):

```json
{"points": {"n_in_region": 10334, "dropped_fill_value": 1195, "dropped_quality_flag": 1193, "n_kept": 7946},
 "units": "m", "min_m": -38.329, "max_m": -29.172, "variable": "ssh_karin"}
```

## Limitations

- Needs network access and an Earthdata Login at run time; the tests need neither.
- The sign-in pop-up (`elicit_url`) failed with `NoBackChannelError` in my test over stdio, so the server falls back to a plain message saying what to set.
- `ssh_karin` includes the geoid; do not read it as ocean dynamics.
- One pass, one box at a time. No SSH-minus-SST comparison, no gridding, no animation.

See [CONTRIBUTING.md](../../CONTRIBUTING.md) and [the scientific quality checklist](../../docs/challenge-cards.md#scientific-quality-checklist).
