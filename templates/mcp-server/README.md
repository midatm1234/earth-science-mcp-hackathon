# __SERVER_NAME__

<!-- Fill in every section. Delete these comments before submitting. -->

One sentence: what scientific question this server helps answer.

| Item | Value |
|---|---|
| Catalog id | `__SERVER_NAME__` |
| Team | __TEAM__ |
| Version | 0.1.0 |
| Transports | stdio (default), Streamable HTTP (`--transport http`, `http://127.0.0.1:8766/mcp`) |
| Credentials | none <!-- or: NAME (what it is, how to get it free, read from environment) --> |
| Network | none <!-- or: which public services are called --> |
| Data volume | <!-- e.g. 20 KB fixture; no downloads --> |
| Typical runtime | <!-- e.g. under 2 seconds per call --> |
| Dependencies | `mcp==2.3.0` <!-- plus anything else, pinned --> |
| License | <!-- e.g. Apache-2.0 for code; data license per data/README.md --> |

## Tools

| Tool | Purpose | Key inputs | Key outputs |
|---|---|---|---|
| `summarize_values` | <!-- replace --> | `values`, `units`, `fill_value` | `n_valid`, `n_missing`, `mean`, `min`, `max`, `units` |

## Scientific conventions

| Topic | This server |
|---|---|
| Variables and units | |
| Coordinate convention | <!-- e.g. WGS84 lon/lat degrees, lon in [-180, 180] --> |
| Spatial support | <!-- point, grid cell (resolution), polygon mean ... --> |
| Temporal support | <!-- instantaneous, daily mean, monthly mean; time-stamp convention; calendar --> |
| Dataset / model version | |
| Missing data | <!-- fill values, QC flags, what is excluded --> |
| Processing choices | <!-- regridding, aggregation, thresholds --> |
| Provenance | <!-- source, DOI or run id, synthetic / cached / live --> |
| Interpretation limits | |

## Run it

```bash
uv run python servers/__SERVER_NAME__/server.py --transport http
uv run pytest servers/__SERVER_NAME__/tests
```

Add to Claude Code for this project (one time):

```bash
claude mcp add --scope local __SERVER_NAME__ -- uv run --quiet python servers/__SERVER_NAME__/server.py
```

## Example

Input:

```json
{"values": [1.0, null, 3.0], "units": "degC"}
```

Output (paste real output):

```json
{"n_total": 3, "n_valid": 2, "n_missing": 1, "mean": 2.0, "min": 1.0, "max": 3.0, "units": "degC"}
```

## Limitations

- <!-- what it cannot do; what a user must not conclude -->

See [CONTRIBUTING.md](../../CONTRIBUTING.md) and [the scientific quality checklist](../../docs/challenge-cards.md#scientific-quality-checklist).
