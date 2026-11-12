"""Fetch a small regional SST subset, draw Cartopy maps and make a GIF. No MCP imports here.

Source: NOAA CoastWatch ERDDAP, dataset jplMURSST41 (the GHRSST MUR v4.1 L4 analysis), which needs no login.
Every fetch is a small regional subset on a coarse grid; whole global files are never requested.
The network call (fetch_text) is separate from parsing and plotting so tests can use a saved sample.
"""

from __future__ import annotations

import csv
import io
import math
import re
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")  # no display: draw straight to files
import cartopy.crs as ccrs  # noqa: E402
import cartopy.feature as cfeature  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from PIL import Image  # noqa: E402

ERDDAP = "https://coastwatch.pfeg.noaa.gov/erddap/griddap/jplMURSST41"
SOURCE = "NOAA CoastWatch ERDDAP, dataset jplMURSST41 (GHRSST MUR v4.1 L4 analysis), no login"
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "sst_output"  # git-ignored
MAX_DAYS = 31
MAX_BOX_DEGREES = 40.0
MAX_POINTS = 60_000
TIMEOUT_S = 60
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,40}$")

Fetcher = Callable[[str], str]


class DataError(ValueError):
    """An expected, explainable problem with inputs or data."""


def fetch_text(url: str) -> str:
    """GET an ERDDAP URL and return the text. The only function here that uses the network."""
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT_S) as response:  # noqa: S310 - fixed https host
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise DataError(f"NOAA ERDDAP returned HTTP {exc.code}. Check the region and dates, or try again later.") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise DataError(f"Could not reach NOAA ERDDAP ({exc}). Check your network connection and try again.") from exc


def _iso_z(moment: datetime) -> str:
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def check_region(south: float, north: float, west: float, east: float) -> None:
    if not (-90 <= south < north <= 90):
        raise DataError("Latitudes must satisfy -90 <= south < north <= 90 (degrees north).")
    if not (-180 <= west < east <= 180):
        raise DataError("Longitudes must satisfy -180 <= west < east <= 180 (degrees east); regions across the dateline are not supported.")
    if (north - south) > MAX_BOX_DEGREES or (east - west) > MAX_BOX_DEGREES:
        raise DataError(f"Region too large: keep each side at {MAX_BOX_DEGREES:g} degrees or less to avoid big downloads.")


def _stride(south: float, north: float, west: float, east: float) -> int:
    """Grid stride (MUR is 0.01 degree) that keeps one day under MAX_POINTS."""
    full = ((north - south) / 0.01 + 1) * ((east - west) / 0.01 + 1)
    return max(1, math.ceil(math.sqrt(full / (MAX_POINTS / 2))))


def newest_available_dates(days: int = 10, fetch: Fetcher = fetch_text) -> dict[str, Any]:
    """Return the newest `days` daily time stamps (UTC) the dataset has, oldest first."""
    if not 1 <= days <= MAX_DAYS:
        raise DataError(f"days must be between 1 and {MAX_DAYS}.")
    url = f"{ERDDAP}.csv?" + f"time[last-{days - 1}:1:last]"
    rows = list(csv.reader(io.StringIO(fetch(url))))[2:]
    stamps = [r[0] for r in rows if r]
    if not stamps:
        raise DataError("NOAA ERDDAP returned no time stamps for this dataset.")
    return {
        "dates": [s[:10] for s in stamps], "time_stamps": stamps, "newest": stamps[-1],
        "date_checked": _iso_z(datetime.now(UTC)), "source": SOURCE, "query": url,
    }


def fetch_regional_subset(date: str, south: float, north: float, west: float, east: float,
                          fetch: Fetcher = fetch_text) -> dict[str, Any]:
    """Fetch one day of analysed SST (degC) for a small region on a coarse grid."""
    if not DATE_RE.match(date):
        raise DataError(f"date '{date}' must look like YYYY-MM-DD, e.g. '2026-11-10'.")
    check_region(south, north, west, east)
    step = _stride(south, north, west, east)
    when = f"{date}T09:00:00Z"  # the MUR analysis is stamped 09:00 UTC each day
    query = (f"analysed_sst[({when})][({south}):{step}:({north})][({west}):{step}:({east})]")
    url = f"{ERDDAP}.csv?" + urllib.parse.quote(query, safe="[]():,")
    rows = list(csv.reader(io.StringIO(fetch(url))))[2:]
    lats, lons, vals = [], [], []
    for r in rows:
        if len(r) >= 4 and r[3] not in ("", "NaN"):
            lats.append(float(r[1]))
            lons.append(float(r[2]))
            vals.append(float(r[3]))
    if not vals:
        raise DataError(f"No SST values for {date} in this region (all missing, or the date is not available).")
    return {
        "date": date, "lats": lats, "lons": lons, "values": vals, "units": "degC",
        "grid_step_degrees": round(step * 0.01, 2), "n_points": len(vals),
        "bounds": {"south": south, "north": north, "west": west, "east": east},
        "source": SOURCE, "query": url,
    }


def _grid(subset: dict[str, Any]):
    import numpy as np

    lats = sorted(set(subset["lats"]))
    lons = sorted(set(subset["lons"]))
    grid = np.full((len(lats), len(lons)), np.nan)
    li = {v: i for i, v in enumerate(lats)}
    oi = {v: i for i, v in enumerate(lons)}
    for la, lo, v in zip(subset["lats"], subset["lons"], subset["values"], strict=True):
        grid[li[la], oi[lo]] = v
    return lons, lats, grid


def _add_basemap(ax) -> None:
    """Add land and coastlines. Cartopy downloads this Natural Earth data once, on first use (needs network)."""
    ax.add_feature(cfeature.LAND, facecolor="0.85", zorder=2)
    ax.coastlines(resolution="50m", linewidth=0.7, zorder=3)


def _draw(ax, subset: dict[str, Any], vmin: float, vmax: float):
    lons, lats, grid = _grid(subset)
    mesh = ax.pcolormesh(lons, lats, grid, vmin=vmin, vmax=vmax, cmap="turbo", transform=ccrs.PlateCarree(), shading="auto")
    _add_basemap(ax)
    b = subset["bounds"]
    ax.set_extent([b["west"], b["east"], b["south"], b["north"]], crs=ccrs.PlateCarree())
    gl = ax.gridlines(draw_labels=True, linewidth=0.3, alpha=0.5)
    gl.top_labels = gl.right_labels = False
    return mesh


def _out_dir(output_dir: Path | None) -> Path:
    out = (output_dir or OUTPUT_DIR)
    out.mkdir(parents=True, exist_ok=True)
    return out


def _file_info(path: Path) -> dict[str, Any]:
    return {"path": str(path), "size_bytes": path.stat().st_size}


def draw_map(subset: dict[str, Any], name: str = "sst_map", output_dir: Path | None = None) -> dict[str, Any]:
    """Draw one Cartopy map of a fetched subset to a PNG in the output folder."""
    if not NAME_RE.match(name):
        raise DataError("name may use letters, digits, '-' and '_' only (no paths), up to 41 characters.")
    vmin, vmax = min(subset["values"]), max(subset["values"])
    fig = plt.figure(figsize=(7, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())
    mesh = _draw(ax, subset, vmin, vmax)
    fig.colorbar(mesh, ax=ax, shrink=0.8, label="Sea surface temperature (degC)")
    ax.set_title(f"MUR analysed SST, {subset['date']}")
    path = _out_dir(output_dir) / f"{name}_{subset['date']}.png"
    fig.savefig(path, dpi=100, bbox_inches="tight")
    plt.close(fig)
    return {"map": _file_info(path), "date": subset["date"], "value_range_degC": [round(vmin, 2), round(vmax, 2)],
            "source": SOURCE, "date_checked": _iso_z(datetime.now(UTC))}


def make_gif(subsets: list[dict[str, Any]], name: str = "sst_animation", output_dir: Path | None = None,
             frame_ms: int = 600) -> dict[str, Any]:
    """Draw one frame per day with a shared colour scale and join them into an animated GIF."""
    if not NAME_RE.match(name):
        raise DataError("name may use letters, digits, '-' and '_' only (no paths), up to 41 characters.")
    if len(subsets) < 2:
        raise DataError("An animation needs at least 2 days; fetch more days first.")
    subsets = sorted(subsets, key=lambda s: s["date"])
    vmin = min(min(s["values"]) for s in subsets)
    vmax = max(max(s["values"]) for s in subsets)
    frames = []
    for s in subsets:
        fig = plt.figure(figsize=(6, 5))
        ax = plt.axes(projection=ccrs.PlateCarree())
        mesh = _draw(ax, s, vmin, vmax)
        fig.colorbar(mesh, ax=ax, shrink=0.8, label="degC")
        ax.set_title(f"MUR analysed SST, {s['date']}")
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=80, bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        frames.append(Image.open(buf).convert("P", palette=Image.ADAPTIVE))
    path = _out_dir(output_dir) / f"{name}.gif"
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=frame_ms, loop=0)
    return {"gif": _file_info(path), "n_frames": len(frames), "dates": [s["date"] for s in subsets],
            "colour_scale_degC": [round(vmin, 2), round(vmax, 2)], "frame_ms": frame_ms,
            "source": SOURCE, "date_checked": _iso_z(datetime.now(UTC))}


def list_output_files(output_dir: Path | None = None) -> dict[str, Any]:
    """List the files this server has written to its output folder."""
    out = output_dir or OUTPUT_DIR
    files = sorted(out.glob("*")) if out.exists() else []
    return {"output_dir": str(out), "files": [_file_info(f) for f in files if f.is_file()], "n_files": len(files)}


# --- storage: tools pass dates, not data arrays; subsets live as small JSON files in the output folder ---

def _subset_path(date: str, output_dir: Path | None) -> Path:
    return _out_dir(output_dir) / f"subset_{date}.json"


def fetch_and_save(date: str, south: float, north: float, west: float, east: float,
                   output_dir: Path | None = None, fetch: Fetcher = fetch_text) -> dict[str, Any]:
    """Fetch one day for a region, save it in the output folder and return a compact summary (no arrays)."""
    import json

    subset = fetch_regional_subset(date, south, north, west, east, fetch)
    path = _subset_path(date, output_dir)
    path.write_text(json.dumps(subset), encoding="utf-8")
    values = subset["values"]
    return {"date": date, "subset_file": _file_info(path), "n_points": subset["n_points"],
            "grid_step_degrees": subset["grid_step_degrees"], "units": "degC", "bounds": subset["bounds"],
            "min_degC": round(min(values), 2), "max_degC": round(max(values), 2),
            "source": SOURCE, "date_checked": _iso_z(datetime.now(UTC))}


def load_saved(date: str, output_dir: Path | None = None) -> dict[str, Any]:
    import json

    path = _subset_path(date, output_dir)
    if not DATE_RE.match(date) or not path.exists():
        raise DataError(f"No saved subset for '{date}'. Fetch that date first with fetch_sst_subset.")
    return json.loads(path.read_text(encoding="utf-8"))


def draw_saved_map(date: str, name: str = "sst_map", output_dir: Path | None = None) -> dict[str, Any]:
    return draw_map(load_saved(date, output_dir), name, output_dir)


def make_saved_gif(dates: list[str], name: str = "sst_animation", output_dir: Path | None = None,
                   frame_ms: int = 600) -> dict[str, Any]:
    if not 2 <= len(dates) <= MAX_DAYS:
        raise DataError(f"Give between 2 and {MAX_DAYS} dates for an animation.")
    subsets = [load_saved(d, output_dir) for d in dates]
    regions = {tuple(sorted(s["bounds"].items())) for s in subsets}
    if len(regions) > 1:
        raise DataError("The saved dates cover different regions; fetch all dates for the same region.")
    return make_gif(subsets, name, output_dir, frame_ms)
