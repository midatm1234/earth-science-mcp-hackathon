"""Scientific functions for __SERVER_NAME__. No MCP imports here.

Replace summarize_values with your own science. Keep functions:
- pure (inputs in, results out; no global state),
- explicit about units, missing data and assumptions,
- raising DataError with a sentence the user can act on.
"""

from __future__ import annotations

import math
from typing import Any


class DataError(ValueError):
    """An expected, explainable problem with inputs or data."""


def summarize_values(values: list[float | None], units: str, fill_value: float | None = None) -> dict[str, Any]:
    """Count valid and missing values and return mean/min/max in the given units.

    Missing: None, NaN, infinity, or a value equal to fill_value.
    """
    if not values:
        raise DataError("values is empty; provide at least one number.")
    if not units.strip():
        raise DataError("units is empty; state the units of the values (e.g. 'degC', 'mm/day').")
    valid = [v for v in values
             if v is not None and math.isfinite(v) and (fill_value is None or v != fill_value)]
    if not valid:
        raise DataError(f"All {len(values)} values are missing or equal to the fill value {fill_value}.")
    return {
        "n_total": len(values),
        "n_valid": len(valid),
        "n_missing": len(values) - len(valid),
        "mean": round(sum(valid) / len(valid), 6),
        "min": min(valid),
        "max": max(valid),
        "units": units,
        "missing_rule": "None, NaN, infinite, or equal to fill_value",
    }
