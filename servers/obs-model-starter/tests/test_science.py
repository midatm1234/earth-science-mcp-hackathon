"""Science tests: no MCP involved. Expected numbers are computed independently."""

from __future__ import annotations

import csv
import json
import math
import shutil
from pathlib import Path

import pytest
import science

DATA = Path(__file__).resolve().parents[1] / "data"


def _tiny_catalog(tmp_path: Path, obs_rows: str, model_rows: str, model_units: str = "K") -> science.Catalog:
    """Write a 3-month hand-checkable dataset pair."""
    manifest = json.loads((DATA / "datasets.json").read_text())
    manifest["datasets"] = [d for d in manifest["datasets"] if d["id"] in
                            ("syn-station-tas-monthly", "syn-model-a-tas-monthly")]
    manifest["datasets"][0]["file"] = "obs.csv"
    manifest["datasets"][1]["file"] = "model.csv"
    manifest["datasets"][1]["units"] = model_units
    (tmp_path / "datasets.json").write_text(json.dumps(manifest))
    shutil.copy(DATA / "sites.csv", tmp_path / "sites.csv")
    (tmp_path / "obs.csv").write_text("site_id,time,tas,qc_flag\n" + obs_rows)
    (tmp_path / "model.csv").write_text("site_id,time,tas\n" + model_rows)
    return science.load_catalog(tmp_path)


def test_hand_computed_bias_and_rmse(tmp_path):
    # obs 10, 20, 30 degC; model 11, 19, 33 degC given in K -> diffs +1, -1, +3
    cat = _tiny_catalog(
        tmp_path,
        "SYN-COAST,2020-01-01,10,good\nSYN-COAST,2020-02-01,20,good\nSYN-COAST,2020-03-01,30,good\n",
        "SYN-COAST,2020-01-15,284.15\nSYN-COAST,2020-02-15,292.15\nSYN-COAST,2020-03-15,306.15\n",
    )
    out = science.compare_model_to_obs(cat, "syn-station-tas-monthly", "syn-model-a-tas-monthly", "SYN-COAST")
    assert out["n_valid_pairs"] == 3
    assert out["units"] == "degC"
    assert out["matched_months"] == ["2020-01", "2020-02", "2020-03"]
    assert out["mean_bias"] == pytest.approx(1.0)  # (1 - 1 + 3) / 3
    assert out["rmse"] == pytest.approx(round(math.sqrt(11 / 3), 3))  # sqrt((1+1+9)/3)


def test_missing_qc_and_unmatched_months_are_reported(tmp_path):
    cat = _tiny_catalog(
        tmp_path,
        "SYN-COAST,2020-01-01,,good\nSYN-COAST,2020-02-01,20,suspect\nSYN-COAST,2020-03-01,30,good\n"
        "SYN-COAST,2020-05-01,15,good\n",
        "SYN-COAST,2020-01-15,284.15\nSYN-COAST,2020-02-15,292.15\nSYN-COAST,2020-03-15,-9999\n"
        "SYN-COAST,2020-04-15,290.0\nSYN-COAST,2020-06-15,290.0\n",
    )
    with pytest.raises(science.DataError, match="No valid"):
        science.compare_model_to_obs(cat, "syn-station-tas-monthly", "syn-model-a-tas-monthly", "SYN-COAST")
    out = science.compare_model_to_obs(cat, "syn-station-tas-monthly", "syn-model-a-tas-monthly", "SYN-COAST",
                                       include_suspect=True)
    assert out["n_valid_pairs"] == 1
    assert out["mean_bias"] == pytest.approx(-1.0)
    ex = out["excluded"]
    assert ex["obs_missing_value"] == ["2020-01"]
    assert ex["model_missing_value"] == ["2020-03"]
    assert ex["month_absent_from_obs"] == ["2020-04", "2020-06"]
    assert ex["month_absent_from_model"] == ["2020-05"]
    assert any("Only 1 valid pairs" in w for w in out["warnings"])


def test_duplicate_month_is_rejected(tmp_path):
    cat = _tiny_catalog(
        tmp_path,
        "SYN-COAST,2020-01-01,10,good\nSYN-COAST,2020-01-20,11,good\n",
        "SYN-COAST,2020-01-15,284.15\n",
    )
    with pytest.raises(science.DataError, match="more than one value"):
        science.compare_model_to_obs(cat, "syn-station-tas-monthly", "syn-model-a-tas-monthly", "SYN-COAST")


def test_unit_conversion_round_trip():
    assert science.convert(273.15, "K", "degC") == pytest.approx(0.0)
    assert science.convert(32.0, "degF", "degC") == pytest.approx(0.0)
    assert science.convert(100.0, "celsius", "kelvin") == pytest.approx(373.15)
    with pytest.raises(science.DataError):
        science.convert(1.0, "mm/day", "degC")


def _independent_stats(model_file: str, model_in_kelvin: bool, site: str):
    """Recompute bias/RMSE from raw CSVs with a separate, deliberately simple method."""
    obs = {}
    with (DATA / "sample_obs_station_tas_monthly.csv").open() as fh:
        for r in csv.DictReader(fh):
            if r["site_id"] == site and r["tas"] and r["qc_flag"] == "good":
                obs[r["time"][:7]] = float(r["tas"])
    diffs = []
    with (DATA / model_file).open() as fh:
        for r in csv.DictReader(fh):
            if r["site_id"] != site or r["tas"] in ("", "NaN", "-9999"):
                continue
            month = r["time"][:7]
            if month in obs:
                value = float(r["tas"]) - (273.15 if model_in_kelvin else 0.0)
                diffs.append(value - obs[month])
    n = len(diffs)
    return n, sum(diffs) / n, math.sqrt(sum(d * d for d in diffs) / n)


@pytest.mark.parametrize("model_id,model_file,kelvin", [
    ("syn-model-a-tas-monthly", "sample_model_a_tas_monthly.csv", True),
    ("syn-model-b-tas-monthly", "sample_model_b_tas_monthly.csv", False),
])
@pytest.mark.parametrize("site", ["SYN-COAST", "SYN-VALLEY", "SYN-MOUNTAIN"])
def test_bundled_fixture_matches_independent_calculation(model_id, model_file, kelvin, site):
    cat = science.load_catalog()
    out = science.compare_model_to_obs(cat, "syn-station-tas-monthly", model_id, site)
    n, bias, rmse = _independent_stats(model_file, kelvin, site)
    assert out["n_valid_pairs"] == n
    assert out["mean_bias"] == pytest.approx(bias, abs=1e-3)
    assert out["rmse"] == pytest.approx(rmse, abs=1e-3)


def test_known_fixture_gaps():
    cat = science.load_catalog()
    out = science.compare_model_to_obs(cat, "syn-station-tas-monthly", "syn-model-a-tas-monthly", "SYN-MOUNTAIN")
    assert out["excluded"]["month_absent_from_obs"] == ["2020-12"]
    assert out["excluded"]["model_missing_value"] == ["2021-11"]
    assert out["n_valid_pairs"] == 22


def test_period_filter_and_errors():
    cat = science.load_catalog()
    out = science.compare_model_to_obs(cat, "syn-station-tas-monthly", "syn-model-b-tas-monthly", "SYN-COAST",
                                       start="2021-01", end="2021-03")
    assert out["matched_months"] == ["2021-01", "2021-03"]
    assert out["excluded"]["obs_qc_rejected"] == ["2021-02"]
    with pytest.raises(science.DataError, match="after end"):
        science.compare_model_to_obs(cat, "syn-station-tas-monthly", "syn-model-b-tas-monthly", "SYN-COAST",
                                     start="2021-05", end="2021-01")
    with pytest.raises(science.DataError, match="YYYY-MM"):
        science.compare_model_to_obs(cat, "syn-station-tas-monthly", "syn-model-b-tas-monthly", "SYN-COAST",
                                     start="May 2021")
    with pytest.raises(science.DataError, match="choose a model dataset"):
        science.compare_model_to_obs(cat, "syn-station-tas-monthly", "syn-station-tas-monthly", "SYN-COAST")
    with pytest.raises(science.DataError, match="No rows for site"):
        science.compare_model_to_obs(cat, "syn-station-tas-monthly", "syn-model-a-tas-monthly", "ATLANTIS")


def test_describe_dataset_counts():
    cat = science.load_catalog()
    out = science.summarize_dataset(cat, "syn-station-tas-monthly")
    sites = {s["site_id"]: s for s in out["sites"]}
    assert out["units"] == "degC"
    assert out["provenance"]["class"] == "synthetic"
    assert sites["SYN-VALLEY"]["missing"] == 1
    assert sites["SYN-COAST"]["qc_rejected"] == 1
    assert sites["SYN-MOUNTAIN"]["rows"] == 23
    assert out["time_coverage"] == {"first_month": "2020-01", "last_month": "2021-12"}
