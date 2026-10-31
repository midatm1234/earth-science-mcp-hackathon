"""Regenerate the SYNTHETIC teaching fixtures used by servers/obs-model-starter.

Every value written by this script is invented. The numbers imitate monthly
near-surface air temperature so that the comparison workflow looks realistic,
but they are not observations and not output from any real model.

Usage:
    uv run python scripts/generate_sample_data.py          # rewrite fixtures
    uv run python scripts/generate_sample_data.py --check  # fail if fixtures differ

The output is deterministic (fixed seed), so --check is used by the test suite
to prove that the committed CSV files match this generator exactly.
"""

from __future__ import annotations

import argparse
import io
import math
import random
import sys
from pathlib import Path

SEED = 20261030
DATA_DIR = Path(__file__).resolve().parents[1] / "servers" / "obs-model-starter" / "data"

# Illustrative coordinates only. The values attached to these sites are synthetic.
SITES = [
    # site_id, name, lat, lon, elevation_m, annual_mean_degC, seasonal_amplitude_degC
    ("SYN-COAST", "Synthetic coastal site", 34.00, -118.50, 20, 17.5, 4.0),
    ("SYN-VALLEY", "Synthetic inland valley site", 36.50, -119.50, 100, 18.0, 9.5),
    ("SYN-MOUNTAIN", "Synthetic mountain site", 37.50, -118.50, 2500, 6.0, 8.0),
]
MODEL_A_BIAS = {"SYN-COAST": 0.8, "SYN-VALLEY": -1.2, "SYN-MOUNTAIN": 2.5}
MODEL_B_BIAS = {"SYN-COAST": 0.2, "SYN-VALLEY": 0.4, "SYN-MOUNTAIN": -0.6}
MONTHS = [(y, m) for y in (2020, 2021) for m in range(1, 13)]

# Deliberate data problems so learners can see the missing-data rules work.
OBS_EMPTY = {("SYN-VALLEY", 2020, 7)}  # value missing (empty cell)
OBS_SUSPECT = {("SYN-COAST", 2021, 2)}  # value present but qc_flag=suspect
OBS_ROW_ABSENT = {("SYN-MOUNTAIN", 2020, 12)}  # no row at all
MODEL_A_FILL = {("SYN-MOUNTAIN", 2021, 11)}  # model fill value -9999


def _truth(annual_mean: float, amplitude: float, month: int) -> float:
    # Peak in mid-July (month ~7), minimum in mid-January.
    return annual_mean + amplitude * math.sin(2 * math.pi * (month - 4) / 12)


def build() -> dict[str, str]:
    rng = random.Random(SEED)
    sites = io.StringIO()
    sites.write("site_id,name,lat,lon,elevation_m\n")
    obs = io.StringIO()
    obs.write("site_id,time,tas,qc_flag\n")
    model_a = io.StringIO()
    model_a.write("site_id,time,tas\n")
    model_b = io.StringIO()
    model_b.write("site_id,time,tas\n")

    for site_id, name, lat, lon, elev, mean, amp in SITES:
        sites.write(f"{site_id},{name},{lat:.2f},{lon:.2f},{elev}\n")
        for year, month in MONTHS:
            truth = _truth(mean, amp, month) + rng.gauss(0, 0.5)
            obs_value = truth + rng.gauss(0, 0.3)
            a_value = truth + MODEL_A_BIAS[site_id] + rng.gauss(0, 0.6)
            b_value = truth + MODEL_B_BIAS[site_id] + rng.gauss(0, 0.9)
            key = (site_id, year, month)

            if key not in OBS_ROW_ABSENT:
                cell = "" if key in OBS_EMPTY else f"{obs_value:.2f}"
                qc = "suspect" if key in OBS_SUSPECT else "good"
                obs.write(f"{site_id},{year:04d}-{month:02d}-01,{cell},{qc}\n")

            # Model A: Kelvin, timestamps at mid-month, -9999 fill value.
            a_cell = "-9999" if key in MODEL_A_FILL else f"{a_value + 273.15:.2f}"
            model_a.write(f"{site_id},{year:04d}-{month:02d}-15,{a_cell}\n")
            # Model B: degC, timestamps at first of month.
            model_b.write(f"{site_id},{year:04d}-{month:02d}-01,{b_value:.2f}\n")

    return {
        "sites.csv": sites.getvalue(),
        "sample_obs_station_tas_monthly.csv": obs.getvalue(),
        "sample_model_a_tas_monthly.csv": model_a.getvalue(),
        "sample_model_b_tas_monthly.csv": model_b.getvalue(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="verify fixtures instead of writing them")
    args = parser.parse_args(argv)

    files = build()
    stale = []
    for name, content in files.items():
        path = DATA_DIR / name
        if args.check:
            current = path.read_text(encoding="utf-8") if path.exists() else None
            if current != content:
                stale.append(name)
        else:
            path.write_text(content, encoding="utf-8", newline="\n")
            print(f"wrote {path.relative_to(DATA_DIR.parents[2])}")
    if stale:
        print("Fixtures differ from generator output: " + ", ".join(stale), file=sys.stderr)
        return 1
    if args.check:
        print("Fixtures match generator output.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
