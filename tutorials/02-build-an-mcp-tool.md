# Tutorial 02 – Build an MCP tool

| | |
|---|---|
| **Scientific purpose** | Turn one well-defined scientific calculation or data lookup into a tool an agent can call reproducibly, with units, missing-data rules and provenance in the result. |
| **Learning objective** | Write a science function separate from its MCP wrapper; give the tool typed inputs, a useful description, a compact structured result and clear errors; test it in-process and over stdio; run it over HTTP. |
| **Estimated time** | 90 minutes (team work) |
| **Starting state** | Discovery record signed off ([tutorial 01](01-discover-existing-capabilities.md)). Either your scaffolded `servers/<server-name>/` or the decision to extend `servers/obs-model-starter/`. |
| **Credentials** | None for the core track. If your tool calls a service that needs a key, read it from an environment variable and document it; never put it in a file. |

## How a tool is built

Open [servers/obs-model-starter/](../servers/obs-model-starter/) side by side with your server.

| Layer | File | Rule |
|---|---|---|
| Science | `science.py` | Plain Python. No MCP imports. Explicit units, missing-data rules, assumptions. Raises `DataError` with an actionable sentence. |
| MCP wrapper | `server.py` | `@mcp.tool()` function: typed parameters with `Field(description=...)`, a docstring that says what it returns and how it fails, converts `DataError` to `ToolError`. Logs to stderr. |
| Data | `data/` + `data/README.md` | Small (≤ 1 MB per file), redistributable, with provenance. |
| Tests | `tests/test_science.py`, `tests/test_server.py` | Hand-computed expected values; one real MCP call; one invalid-input case checking `is_error`. |

## Step 1 – Run the template as-is (5 minutes)

```bash
uv run pytest servers/<server-name>/tests
```

Expected: `5 passed`. The template tool `summarize_values` already works. Now replace it.

## Step 2 – Write the science function (30 minutes)

Worked example (extending the starter with a seasonal bias). Add to `servers/obs-model-starter/science.py`:

```python
SEASONS = {"DJF": (12, 1, 2), "MAM": (3, 4, 5), "JJA": (6, 7, 8), "SON": (9, 10, 11)}


def seasonal_bias(catalog, obs_dataset_id, model_dataset_id, site_id, start=None, end=None):
    """Mean bias (model - obs) per meteorological season, using the same pairing rules."""
    base = compare_model_to_obs(catalog, obs_dataset_id, model_dataset_id, site_id, start, end)
    obs_meta, model_meta = get_dataset(catalog, obs_dataset_id), get_dataset(catalog, model_dataset_id)
    obs = {r.month: r.value for r in read_records(catalog, obs_meta) if r.site_id == site_id}
    mod = {r.month: r.value for r in read_records(catalog, model_meta) if r.site_id == site_id}
    out = {}
    for season, months in SEASONS.items():
        diffs = [convert(mod[m], model_meta.units, obs_meta.units) - obs[m]
                 for m in base["matched_months"] if int(m[5:7]) in months]
        out[season] = {"n_pairs": len(diffs),
                       "mean_bias": round(sum(diffs) / len(diffs), 3) if diffs else None}
    return {"site_id": site_id, "units": base["units"], "seasons": out,
            "pairing": base["alignment_rule"], "excluded": base["excluded"],
            "provenance": base["provenance"], "warnings": base["warnings"]}
```

Note: DJF here groups calendar months 12, 1, 2 regardless of year; say so in the description.

## Step 3 – Wrap it as a tool (15 minutes)

Add to `server.py`:

```python
@mcp.tool(annotations=READ_ONLY)
def seasonal_bias(
    obs_dataset_id: Annotated[str, Field(description="Observation dataset id.")],
    model_dataset_id: Annotated[str, Field(description="Model dataset id.")],
    site_id: Annotated[str, Field(description="Site id, e.g. 'SYN-VALLEY'.")],
    start: Annotated[str | None, Field(description="First month 'YYYY-MM'.")] = None,
    end: Annotated[str | None, Field(description="Last month 'YYYY-MM'.")] = None,
) -> dict[str, Any]:
    """Mean bias (model - observation) per season DJF/MAM/JJA/SON at one site.

    Uses the same pairing, unit conversion and exclusion rules as compare_model_to_obs.
    DJF pools December, January and February of any year in the period.
    Returns per-season n_pairs and mean_bias in observation units; a season with no pairs has mean_bias null.
    """
    return _run(science.seasonal_bias, obs_dataset_id, model_dataset_id, site_id, start, end)
```

Good descriptions say **what is returned, in which units, and how it fails**. The model chooses tools and builds arguments from this text.

## Step 4 – Test it (25 minutes)

Science test with a hand-computed value (in `tests/test_science.py`), reusing the `_tiny_catalog` helper:

```python
def test_seasonal_bias_hand_computed(tmp_path):
    cat = _tiny_catalog(tmp_path,
        "SYN-COAST,2020-01-01,10,good\nSYN-COAST,2020-07-01,20,good\n",
        "SYN-COAST,2020-01-15,284.15\nSYN-COAST,2020-07-15,292.15\n")   # +1 in DJF, -1 in JJA
    out = science.seasonal_bias(cat, "syn-station-tas-monthly", "syn-model-a-tas-monthly", "SYN-COAST")
    assert out["seasons"]["DJF"] == {"n_pairs": 1, "mean_bias": 1.0}
    assert out["seasons"]["JJA"] == {"n_pairs": 1, "mean_bias": -1.0}
    assert out["seasons"]["MAM"]["mean_bias"] is None
```

Protocol test (in `tests/test_server.py`): add `"seasonal_bias"` to `EXPECTED_TOOLS` and a call that checks `is_error` for a bad site. Then:

```bash
uv run pytest servers/obs-model-starter/tests
uv run python scripts/check_all.py --fast
```

Update the tool list in `catalog/entries/<server>.yaml` and run `uv run python scripts/catalog.py index`.

## Step 5 – Try it with your AI assistant (10 minutes)

Start a new chat/session (assistants start MCP servers when a session begins; in VS Code you can also use **MCP: List Servers** → Restart), then:

```text
Which season has the largest model A bias at SYN-MOUNTAIN?
```

Expected: a call to `seasonal_bias` and an answer with per-season bias in °C and pair counts.

A new server created with `scripts/new_contribution.py` is already registered for all assistants (in `.mcp.json` and `.codex/config.toml`). If you created the folder by hand, register it:

```bash
uv run python scripts/client_config.py register <server-name>
```

Over HTTP for a second client: `uv run python servers/<server-name>/server.py --transport http` (template port 8766).

## Design checklist

- Inputs typed and described; optional inputs have safe defaults.
- Output is compact JSON: numbers, short lists, ids – not raw arrays or files.
- Units, time convention, pairing/missing-data rules and provenance are in the output.
- Errors are sentences that say what to change.
- No `print()` to stdout. No network calls in tests. No credentials in code.
- Science separate from the wrapper; tests use hand-computed values.

## Exercise

Make one invalid input produce a helpful error, e.g. `start` after `end`, or an unknown site. Add a test that checks `result.is_error` and the message.

## Common errors and recovery

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: science` in tests | `tests/conftest.py` missing | Copy it from the template |
| Assistant does not see the new tool | Session started before the change | New chat/session; Copilot: **MCP: List Servers** → Restart; Claude Code: `/mcp`; Codex: new chat |
| Server fails only in the assistant, works in pytest | Something prints to stdout | Use `log.info(...)`; never `print()` |
| `Input validation error` | Wrong argument type | Check the schema with `first_call.py`-style client or the Inspector |
| Validator: "pin an exact version" | Added a dependency without `==` | `uv add package==X.Y.Z`; update `requirements.txt` to match |
| Tool returns huge output | Returning raw data | Summarise; return counts, statistics, ids, URLs |

Next: [Tutorial 03 – Create an agent skill](03-create-an-agent-skill.md)
