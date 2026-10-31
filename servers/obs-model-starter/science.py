"""Scientific core for the obs-model-starter server.

This module has no MCP imports. Everything here is ordinary Python that can be
tested, reused in a notebook, or wrapped by a different interface. The MCP
wrapper lives in server.py.

Alignment and missing-data rules (also returned with every comparison):

1. Both inputs must describe the same variable at monthly resolution.
2. Each time stamp is reduced to its calendar month (YYYY-MM). A value stamped
   2020-07-15 and one stamped 2020-07-01 both represent July 2020. This is valid
   only because both datasets declare calendar-month means.
3. Pairs are matched on (site_id, YYYY-MM). Months present in only one dataset
   are reported, not interpolated.
4. A value is missing if its cell equals one of the dataset's declared
   missing_values or is not a finite number. Observation rows whose QC flag is
   not in qc_good_values are excluded unless include_suspect=True.
5. Model values are converted to the observation units before comparison.
6. bias = mean(model - observation); rmse = sqrt(mean((model - observation)^2)).
"""

from __future__ import annotations

import csv
import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent / "data"
MAX_LISTED_TIMES = 60
MIN_RECOMMENDED_PAIRS = 6

_MONTH_RE = re.compile(r"^(\d{4})-(\d{2})(?:-(\d{2}))?$")

ALIGNMENT_RULE = (
    "Calendar-month matching on (site_id, YYYY-MM); day-of-month labels are ignored because both "
    "datasets declare calendar-month means. Unmatched months are reported, never interpolated. "
    "Missing values and non-good QC flags are excluded before pairing. Model values are converted "
    "to observation units. bias = mean(model - observation); rmse = sqrt(mean((model - observation)^2))."
)


class DataError(ValueError):
    """An expected, explainable problem with inputs or data (shown to the user)."""


@dataclass(frozen=True)
class DatasetMeta:
    id: str
    kind: str
    title: str
    file: str
    variable: str
    long_name: str
    units: str
    time_resolution: str
    time_convention: str
    spatial_support: str
    coordinates: str
    missing_values: tuple[str, ...]
    qc_column: str | None
    qc_good_values: tuple[str, ...]
    version: str
    provenance: dict[str, Any]
    license: str
    citation: str


@dataclass
class Record:
    site_id: str
    month: str
    raw_time: str
    value: float | None
    qc: str | None


@dataclass
class Catalog:
    datasets: dict[str, DatasetMeta]
    sites: dict[str, dict[str, Any]]
    data_dir: Path = field(default=DATA_DIR)


# --------------------------------------------------------------------------- loading


def load_catalog(data_dir: Path = DATA_DIR) -> Catalog:
    manifest_path = data_dir / "datasets.json"
    if not manifest_path.exists():
        raise DataError(f"Dataset manifest not found: {manifest_path.name} in the server data folder.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    datasets: dict[str, DatasetMeta] = {}
    for entry in manifest["datasets"]:
        meta = DatasetMeta(
            id=entry["id"],
            kind=entry["kind"],
            title=entry["title"],
            file=entry["file"],
            variable=entry["variable"],
            long_name=entry["long_name"],
            units=entry["units"],
            time_resolution=entry["time_resolution"],
            time_convention=entry["time_convention"],
            spatial_support=entry["spatial_support"],
            coordinates=entry["coordinates"],
            missing_values=tuple(entry.get("missing_values", [])),
            qc_column=entry.get("qc_column"),
            qc_good_values=tuple(entry.get("qc_good_values", [])),
            version=entry["version"],
            provenance=entry["provenance"],
            license=entry["license"],
            citation=entry["citation"],
        )
        datasets[meta.id] = meta
    sites: dict[str, dict[str, Any]] = {}
    sites_file = manifest.get("sites_file")
    if sites_file:
        with (data_dir / sites_file).open(newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                sites[row["site_id"]] = {
                    "site_id": row["site_id"],
                    "name": row["name"],
                    "lat": float(row["lat"]),
                    "lon": float(row["lon"]),
                    "elevation_m": float(row["elevation_m"]),
                }
    return Catalog(datasets=datasets, sites=sites, data_dir=data_dir)


def get_dataset(catalog: Catalog, dataset_id: str) -> DatasetMeta:
    if dataset_id not in catalog.datasets:
        available = ", ".join(sorted(catalog.datasets))
        raise DataError(f"Unknown dataset_id '{dataset_id}'. Available dataset ids: {available}.")
    return catalog.datasets[dataset_id]


def parse_month(text: str) -> str:
    """Return 'YYYY-MM' for 'YYYY-MM' or 'YYYY-MM-DD' input, or raise DataError."""
    match = _MONTH_RE.match(text.strip())
    if not match:
        raise DataError(f"Time '{text}' is not in YYYY-MM or YYYY-MM-DD format.")
    year, month = int(match.group(1)), int(match.group(2))
    if not 1 <= month <= 12:
        raise DataError(f"Time '{text}' has month {month}; expected 01-12.")
    return f"{year:04d}-{month:02d}"


def _parse_value(cell: str, missing_values: tuple[str, ...]) -> float | None:
    cell = cell.strip()
    if cell in missing_values:
        return None
    try:
        value = float(cell)
    except ValueError:
        return None
    return value if math.isfinite(value) else None


def read_records(catalog: Catalog, meta: DatasetMeta) -> list[Record]:
    path = catalog.data_dir / meta.file
    records: list[Record] = []
    seen: set[tuple[str, str]] = set()
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            month = parse_month(row["time"])
            key = (row["site_id"], month)
            if key in seen:
                raise DataError(
                    f"Dataset '{meta.id}' has more than one value for site {key[0]} in {month}; "
                    "monthly matching would be ambiguous."
                )
            seen.add(key)
            qc = row.get(meta.qc_column) if meta.qc_column else None
            records.append(
                Record(
                    site_id=row["site_id"],
                    month=month,
                    raw_time=row["time"],
                    value=_parse_value(row[meta.variable], meta.missing_values),
                    qc=qc,
                )
            )
    return records


# --------------------------------------------------------------------------- units

_TEMPERATURE_TO_K = {
    "K": (1.0, 0.0),
    "degC": (1.0, 273.15),
    "degF": (5.0 / 9.0, 273.15 - 32.0 * 5.0 / 9.0),
}
_UNIT_ALIASES = {"kelvin": "K", "k": "K", "c": "degC", "celsius": "degC", "°c": "degC", "degc": "degC",
                 "f": "degF", "fahrenheit": "degF", "°f": "degF", "degf": "degF"}


def normalize_unit(unit: str) -> str:
    return _UNIT_ALIASES.get(unit.strip().lower(), unit.strip())


def convert(value: float, from_unit: str, to_unit: str) -> float:
    src, dst = normalize_unit(from_unit), normalize_unit(to_unit)
    if src == dst:
        return value
    if src not in _TEMPERATURE_TO_K or dst not in _TEMPERATURE_TO_K:
        raise DataError(f"No conversion is defined from '{from_unit}' to '{to_unit}'.")
    scale, offset = _TEMPERATURE_TO_K[src]
    kelvin = value * scale + offset
    scale, offset = _TEMPERATURE_TO_K[dst]
    return (kelvin - offset) / scale


def describe_conversion(from_unit: str, to_unit: str) -> str:
    src, dst = normalize_unit(from_unit), normalize_unit(to_unit)
    if src == dst:
        return f"none (both in {dst})"
    if (src, dst) == ("K", "degC"):
        return "K -> degC by subtracting 273.15"
    if (src, dst) == ("degC", "K"):
        return "degC -> K by adding 273.15"
    return f"{src} -> {dst} via kelvin"


# --------------------------------------------------------------------------- summaries


def _round(value: float | None, digits: int = 3) -> float | None:
    return None if value is None else round(value, digits)


def list_datasets(catalog: Catalog) -> list[dict[str, Any]]:
    return [
        {
            "dataset_id": m.id,
            "kind": m.kind,
            "variable": m.variable,
            "units": m.units,
            "provenance_class": m.provenance.get("class", "unknown"),
            "title": m.title,
        }
        for m in sorted(catalog.datasets.values(), key=lambda d: d.id)
    ]


def summarize_dataset(catalog: Catalog, dataset_id: str) -> dict[str, Any]:
    meta = get_dataset(catalog, dataset_id)
    records = read_records(catalog, meta)
    per_site: dict[str, dict[str, Any]] = {}
    for rec in records:
        s = per_site.setdefault(rec.site_id, {"rows": 0, "valid": 0, "missing": 0, "qc_rejected": 0,
                                              "first_month": rec.month, "last_month": rec.month,
                                              "_values": []})
        s["rows"] += 1
        s["first_month"] = min(s["first_month"], rec.month)
        s["last_month"] = max(s["last_month"], rec.month)
        if rec.value is None:
            s["missing"] += 1
        elif meta.qc_column and rec.qc not in meta.qc_good_values:
            s["qc_rejected"] += 1
        else:
            s["valid"] += 1
            s["_values"].append(rec.value)
    sites_out = []
    for site_id in sorted(per_site):
        s = per_site[site_id]
        values = s.pop("_values")
        site_info = catalog.sites.get(site_id, {})
        sites_out.append({
            "site_id": site_id,
            "lat": site_info.get("lat"),
            "lon": site_info.get("lon"),
            **s,
            "mean": _round(sum(values) / len(values)) if values else None,
            "min": _round(min(values)) if values else None,
            "max": _round(max(values)) if values else None,
        })
    months = sorted({r.month for r in records})
    return {
        "dataset_id": meta.id,
        "kind": meta.kind,
        "title": meta.title,
        "variable": meta.variable,
        "long_name": meta.long_name,
        "units": meta.units,
        "time_resolution": meta.time_resolution,
        "time_convention": meta.time_convention,
        "time_coverage": {"first_month": months[0] if months else None,
                          "last_month": months[-1] if months else None},
        "spatial_support": meta.spatial_support,
        "coordinates": meta.coordinates,
        "missing_values": list(meta.missing_values),
        "qc": {"column": meta.qc_column, "good_values": list(meta.qc_good_values)},
        "sites": sites_out,
        "version": meta.version,
        "provenance": meta.provenance,
        "license": meta.license,
        "citation": meta.citation,
    }


# --------------------------------------------------------------------------- comparison


def compare_model_to_obs(
    catalog: Catalog,
    obs_dataset_id: str,
    model_dataset_id: str,
    site_id: str,
    start: str | None = None,
    end: str | None = None,
    include_suspect: bool = False,
) -> dict[str, Any]:
    obs_meta = get_dataset(catalog, obs_dataset_id)
    model_meta = get_dataset(catalog, model_dataset_id)
    if obs_meta.kind != "observation":
        raise DataError(f"obs_dataset_id '{obs_dataset_id}' is a {obs_meta.kind} dataset; choose an observation dataset.")
    if model_meta.kind != "model":
        raise DataError(f"model_dataset_id '{model_dataset_id}' is a {model_meta.kind} dataset; choose a model dataset.")
    if obs_meta.variable != model_meta.variable:
        raise DataError(
            f"Variables differ: observation has '{obs_meta.variable}', model has '{model_meta.variable}'."
        )
    if obs_meta.time_resolution != "monthly" or model_meta.time_resolution != "monthly":
        raise DataError("This tool only matches monthly means. Both datasets must declare time_resolution 'monthly'.")

    start_m = parse_month(start) if start else None
    end_m = parse_month(end) if end else None
    if start_m and end_m and start_m > end_m:
        raise DataError(f"start ({start_m}) is after end ({end_m}).")

    def in_window(month: str) -> bool:
        return (start_m is None or month >= start_m) and (end_m is None or month <= end_m)

    obs_records = [r for r in read_records(catalog, obs_meta) if r.site_id == site_id and in_window(r.month)]
    model_records = [r for r in read_records(catalog, model_meta) if r.site_id == site_id and in_window(r.month)]
    if not obs_records and not model_records:
        known = sorted({r.site_id for r in read_records(catalog, obs_meta)})
        raise DataError(
            f"No rows for site '{site_id}' in the requested period in either dataset. "
            f"Observation sites: {', '.join(known)}."
        )

    obs_by_month = {r.month: r for r in obs_records}
    model_by_month = {r.month: r for r in model_records}
    excluded: dict[str, list[str]] = {
        "obs_missing_value": [],
        "obs_qc_rejected": [],
        "model_missing_value": [],
        "month_absent_from_obs": [],
        "month_absent_from_model": [],
    }
    pairs: list[tuple[str, float, float]] = []
    for month in sorted(set(obs_by_month) | set(model_by_month)):
        o, m = obs_by_month.get(month), model_by_month.get(month)
        if o is None:
            excluded["month_absent_from_obs"].append(month)
            continue
        if m is None:
            excluded["month_absent_from_model"].append(month)
            continue
        if o.value is None:
            excluded["obs_missing_value"].append(month)
            continue
        if obs_meta.qc_column and o.qc not in obs_meta.qc_good_values and not include_suspect:
            excluded["obs_qc_rejected"].append(month)
            continue
        if m.value is None:
            excluded["model_missing_value"].append(month)
            continue
        model_value = convert(m.value, model_meta.units, obs_meta.units)
        pairs.append((month, model_value, o.value))

    n = len(pairs)
    if n == 0:
        reasons = {k: len(v) for k, v in excluded.items() if v}
        raise DataError(f"No valid model/observation pairs for site '{site_id}' in the requested period. Exclusions: {reasons}.")

    diffs = [mv - ov for _, mv, ov in pairs]
    bias = sum(diffs) / n
    rmse = math.sqrt(sum(d * d for d in diffs) / n)
    matched = [p[0] for p in pairs]
    warnings = []
    if n < MIN_RECOMMENDED_PAIRS:
        warnings.append(f"Only {n} valid pairs; statistics are not robust below {MIN_RECOMMENDED_PAIRS}.")
    if include_suspect:
        warnings.append("include_suspect=True: observations flagged suspect were used.")
    if "point" in obs_meta.spatial_support and "grid" in model_meta.spatial_support:
        warnings.append("Point observation compared with a grid-cell mean: part of the difference is representativeness, not model error.")
    for p in (obs_meta, model_meta):
        if p.provenance.get("class") == "synthetic":
            warnings.append(f"'{p.id}' is SYNTHETIC teaching data; results say nothing about real climate or real models.")

    return {
        "site_id": site_id,
        "site": catalog.sites.get(site_id),
        "variable": obs_meta.variable,
        "units": obs_meta.units,
        "unit_conversion": {"model": describe_conversion(model_meta.units, obs_meta.units), "observation": "none"},
        "period_requested": {"start": start_m, "end": end_m},
        "n_valid_pairs": n,
        "matched_months": matched[:MAX_LISTED_TIMES],
        "matched_months_truncated": n > MAX_LISTED_TIMES,
        "mean_bias": round(bias, 3),
        "rmse": round(rmse, 3),
        "bias_definition": "mean(model - observation), in the units above",
        "excluded": excluded,
        "alignment_rule": ALIGNMENT_RULE,
        "warnings": warnings,
        "provenance": {
            "observation": {"dataset_id": obs_meta.id, "version": obs_meta.version, **obs_meta.provenance,
                            "license": obs_meta.license, "time_convention": obs_meta.time_convention},
            "model": {"dataset_id": model_meta.id, "version": model_meta.version, **model_meta.provenance,
                      "license": model_meta.license, "time_convention": model_meta.time_convention},
        },
    }
