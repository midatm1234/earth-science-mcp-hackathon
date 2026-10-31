# obs-model-starter

A small, credential-free MCP server that compares **monthly model values with observations** at a few sites. It is the pretested starter every team extends.

> **All bundled data are SYNTHETIC teaching fixtures.** The numbers are invented by [generate_sample_data.py](../../scripts/generate_sample_data.py). Results say nothing about real climate or any real model. See [data/README.md](data/README.md).

| Item | Value |
|---|---|
| Catalog id | `obs-model-starter` ([catalog entry](../../catalog/entries/obs-model-starter.yaml)) |
| Version | 0.1.0 |
| Transports | stdio (default), Streamable HTTP (`--transport http`, `http://127.0.0.1:8765/mcp`) |
| Credentials | none |
| Network | none (reads local CSV files) |
| Data volume | about 8 KB |
| Typical runtime | under 1 second per call |
| Python | 3.11–3.14 (tested: see [validation report](../../docs/validation-report.md)) |
| Dependencies | `mcp==2.3.0` (see [requirements.txt](requirements.txt)) |
| License | Apache-2.0 (code), CC0-1.0 (synthetic data) |

## Tools

| Tool | Purpose | Key inputs | Key outputs |
|---|---|---|---|
| `list_datasets` | Show available datasets | none | `dataset_id`, `kind`, `variable`, `units`, `provenance_class` |
| `describe_dataset` | Check metadata before use | `dataset_id` | units, time convention, coverage, spatial support, missing values, QC rule, per-site counts and mean/min/max, provenance, license |
| `compare_model_to_obs` | Model–observation statistics at one site | `obs_dataset_id`, `model_dataset_id`, `site_id`, optional `start`, `end` (`YYYY-MM`), `include_suspect` | `n_valid_pairs`, `matched_months`, `mean_bias`, `rmse`, `units`, `unit_conversion`, `excluded` (by reason), `alignment_rule`, `warnings`, `provenance` |

All tools are read-only and idempotent. Errors come back as MCP tool errors (`isError: true`) with a sentence explaining what to fix, for example a list of valid dataset ids.

## Scientific conventions

| Topic | Rule |
|---|---|
| Variable | `tas`, near-surface (2 m) air temperature, calendar-month mean |
| Units | Observations in `degC`. Model A in `K`; model B in `degC`. Model values are converted to observation units before comparison (`K → degC`: subtract 273.15). |
| Time | Each time stamp is reduced to its calendar month (`YYYY-MM`). Observation stamps are the 1st of the month; model A stamps are the 15th. Matching on month is valid **only because** both datasets declare calendar-month means. Duplicate months in one dataset are rejected. |
| Alignment | Pairs are matched on `(site_id, YYYY-MM)`. Months present in only one dataset are listed in `excluded`; nothing is interpolated. |
| Missing data | A value is missing if it equals a declared missing value (`""`, `NaN`, `-9999`) or is not a finite number. Observations whose `qc_flag` is not `good` are excluded unless `include_suspect=true`. |
| Statistics | `mean_bias = mean(model − observation)`; `rmse = sqrt(mean((model − observation)²))`. Both in observation units, rounded to 3 decimals. A warning is added when fewer than 6 pairs remain. |
| Coordinates | WGS84 latitude/longitude in decimal degrees, longitude in [−180, 180], east positive. |
| Spatial support | Observations are points; model values represent a grid-cell area mean. Part of any difference is representativeness, not model error. |

## Run it

From the repository root, after [setup](../../docs/setup.md):

```bash
uv run python scripts/first_call.py                                   # client starts server over stdio
uv run python servers/obs-model-starter/server.py --transport http     # terminal 1: HTTP server
uv run python scripts/first_call.py --http http://127.0.0.1:8765/mcp   # terminal 2: client over HTTP
uv run pytest servers/obs-model-starter/tests                         # tests
```

Claude Code picks it up from the repository's [.mcp.json](../../.mcp.json); see [tutorial 00](../../tutorials/00-first-tool-call.md).

## Example

Input (`compare_model_to_obs`):

```json
{"obs_dataset_id": "syn-station-tas-monthly", "model_dataset_id": "syn-model-a-tas-monthly", "site_id": "SYN-VALLEY"}
```

Output (abridged, real output of version 0.1.0):

```json
{
  "site_id": "SYN-VALLEY",
  "units": "degC",
  "unit_conversion": {"model": "K -> degC by subtracting 273.15", "observation": "none"},
  "n_valid_pairs": 23,
  "mean_bias": -1.054,
  "rmse": 1.212,
  "excluded": {"obs_missing_value": ["2020-07"], "obs_qc_rejected": [], "model_missing_value": [],
               "month_absent_from_obs": [], "month_absent_from_model": []},
  "warnings": ["Point observation compared with a grid-cell mean: ...", "'syn-station-tas-monthly' is SYNTHETIC teaching data; ..."]
}
```

## Limitations

- Monthly means of one variable only; no daily data, no climatologies, no significance tests.
- One site per call; no spatial aggregation.
- Unit conversion covers temperature units only (`K`, `degC`, `degF`).
- Bias and RMSE do not separate model error from observation error or point-versus-grid representativeness.
- The fixtures are synthetic. Replacing them with real data requires checking license, provenance and the time-stamp convention of the new source.

## Files

| File | Role |
|---|---|
| [science.py](science.py) | Pure scientific functions; no MCP imports |
| [server.py](server.py) | Thin MCP wrapper: typed inputs, descriptions, error translation, transports |
| [data/](data/) | Synthetic fixtures, `datasets.json` manifest, provenance card |
| [tests/](tests/) | Hand-computed and independently recomputed statistics; in-process, stdio and HTTP protocol tests |
| [requirements.txt](requirements.txt) | Pinned runtime dependency for pip or container installs |
