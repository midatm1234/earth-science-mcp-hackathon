"""Draw Cartopy maps of saved SWOT subsets and list output files. No MCP imports here."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")  # no display: draw straight to files
import cartopy.crs as ccrs  # noqa: E402
import cartopy.feature as cfeature  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import science  # noqa: E402


def _add_basemap(ax: Any) -> None:
    """Add land and coastlines. Cartopy downloads this Natural Earth data once, on first use (needs network)."""
    ax.add_feature(cfeature.LAND, facecolor="0.85", zorder=2)
    ax.coastlines(resolution="50m", linewidth=0.7, zorder=3)


def draw_map(pass_name: str, variable: str = "ssh_karin", output_dir: Path | None = None) -> dict[str, Any]:
    """Draw one saved pass as coloured points (SWOT is a swath, not a grid) on a Cartopy map (PNG)."""
    science._check_pass(pass_name)
    if variable not in science.VARIABLES:
        raise science.DataError(f"variable must be one of {', '.join(science.VARIABLES)}.")
    path = science.saved_path(pass_name, variable, output_dir)
    if not path.exists():
        raise science.DataError(f"No saved subset for {pass_name} ({variable}). Fetch it first with fetch_swot_pass.")
    with np.load(path, allow_pickle=False) as saved:
        lat, lon, value = saved["lat"], saved["lon"], saved["value"]
        meta = json.loads(str(saved["meta"]))
    b = meta["bounds"]
    fig = plt.figure(figsize=(7, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())
    points = ax.scatter(lon, lat, c=value, s=4, marker="s", cmap="viridis", transform=ccrs.PlateCarree(), zorder=1)
    _add_basemap(ax)
    ax.set_extent([b["west"], b["east"], b["south"], b["north"]], crs=ccrs.PlateCarree())
    gl = ax.gridlines(draw_labels=True, linewidth=0.3, alpha=0.5)
    gl.top_labels = gl.right_labels = False
    fig.colorbar(points, ax=ax, shrink=0.8, label=f"{variable} (m)")
    ax.set_title(f"SWOT {variable}, swath points\n{meta['time_start']} to {meta['time_end']}", fontsize=10)
    out = science._out_dir(output_dir) / f"{pass_name}__{variable}.png"
    fig.savefig(out, dpi=100, bbox_inches="tight")
    plt.close(fig)
    return {
        "map": {"path": str(out), "size_bytes": out.stat().st_size}, "pass_name": pass_name, "variable": variable,
        "units": "m", "n_points": int(value.size), "value_range_m": [round(float(value.min()), 3), round(float(value.max()), 3)],
        "drawn_as": "points along the swath (not a regular grid)", "source": science.SOURCE,
        "date_checked": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def list_output_files(output_dir: Path | None = None) -> dict[str, Any]:
    """List the files this server has written to its output folder."""
    out = output_dir or science.OUTPUT_DIR
    files = [f for f in sorted(out.glob("*")) if f.is_file()] if out.exists() else []
    return {"output_dir": str(out), "n_files": len(files),
            "files": [{"path": str(f), "size_bytes": f.stat().st_size} for f in files]}
