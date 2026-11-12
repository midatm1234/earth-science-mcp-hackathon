"""Scientific functions for swot-ssh. No MCP imports here.

Finds SWOT L2 KaRIn Low Rate SSH (Version D, Basic product) passes over a region from public NASA CMR metadata
(no login), downloads ONE pass with an Earthdata Login user token, and cuts out the region after dropping
fill values and flagged points. The network calls (fetch_json, download_file) are separate from the parsing
and subsetting so tests can use saved responses and a small synthetic NetCDF file.
"""

from __future__ import annotations

import base64
import http.cookiejar
import json
import netrc
import os
import re
import shutil
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np

CMR_SEARCH = "https://cmr.earthdata.nasa.gov/search"
COLLECTION_ID = "C3233945000-POCLOUD"  # SWOT_L2_LR_SSH_D, Version D
ARCHIVE = "https://archive.swot.podaac.earthdata.nasa.gov/podaac-swot-ops-cumulus-protected/SWOT_L2_LR_SSH_D"
LOGIN_URL = "https://urs.earthdata.nasa.gov"
TOKEN_VAR = "EARTHDATA_TOKEN"  # noqa: S105 - the NAME of the environment variable, not a secret
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "swot_output"  # git-ignored
VARIABLES = ("ssh_karin", "ssha_karin")
MAX_DAYS = 30
MAX_BOX_DEGREES = 40.0
MAX_REDIRECTS = 5
TIMEOUT_S = 120
PASS_RE = re.compile(r"^SWOT_L2_LR_SSH_Basic_(\d{3})_(\d{3})_(\d{8}T\d{6})_(\d{8}T\d{6})_PID0_\d{2}$")
NETRC_HOST = "urs.earthdata.nasa.gov"
NO_TOKEN_MESSAGE = (
    f"No Earthdata Login found. Either (1) sign in at {LOGIN_URL}, open your profile, click Generate Token, "
    f"set it as the environment variable {TOKEN_VAR} in your own terminal, and start a new session; or "
    f"(2) put a 'machine {NETRC_HOST}' entry in ~/.netrc (chmod 600). Never paste a token or password into the chat."
)
SOURCE = "NASA PO.DAAC SWOT_L2_LR_SSH_D (Version D, Basic), KaRIn Low Rate sea surface height"

Fetcher = Callable[[str], dict[str, Any]]


class DataError(ValueError):
    """An expected, explainable problem with inputs or data."""


def get_token() -> str | None:
    """Return the Earthdata user token from the environment, or None. The value is never logged or returned."""
    return os.environ.get(TOKEN_VAR, "").strip() or None


def get_netrc_login() -> tuple[str, str] | None:
    """Return (login, password) for the Earthdata Login host from ~/.netrc, or None. Never logged or returned."""
    try:
        entry = netrc.netrc().authenticators(NETRC_HOST)
    except (FileNotFoundError, netrc.NetrcParseError, OSError):
        return None
    return (entry[0], entry[2]) if entry and entry[0] and entry[2] else None


def _iso_z(moment: datetime) -> str:
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_stamp(text: str) -> datetime:
    return datetime.strptime(text, "%Y%m%dT%H%M%S").replace(tzinfo=UTC)


def check_region(south: float, north: float, west: float, east: float) -> None:
    if not (-90 <= south < north <= 90):
        raise DataError("Latitudes must satisfy -90 <= south < north <= 90 (degrees north).")
    if not (-180 <= west < east <= 180):
        raise DataError("Longitudes must satisfy -180 <= west < east <= 180 (degrees east); regions across the dateline are not supported.")
    if (north - south) > MAX_BOX_DEGREES or (east - west) > MAX_BOX_DEGREES:
        raise DataError(f"Region too large: keep each side at {MAX_BOX_DEGREES:g} degrees or less.")


def fetch_json(url: str) -> dict[str, Any]:
    """GET a public CMR search URL (no login) and return parsed JSON."""
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310 - fixed https host
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raise DataError(f"NASA CMR returned HTTP {exc.code}. Try again later.") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise DataError(f"Could not reach NASA CMR ({exc}). Check your network connection.") from exc


def find_passes(south: float, north: float, west: float, east: float, days: int = 10,
                fetch: Fetcher = fetch_json, now: datetime | None = None) -> dict[str, Any]:
    """List SWOT Basic passes whose footprint touches a region in the last `days` days (newest first)."""
    check_region(south, north, west, east)
    if not 1 <= days <= MAX_DAYS:
        raise DataError(f"days must be between 1 and {MAX_DAYS}.")
    checked = now or datetime.now(UTC)
    query = {
        "collection_concept_id": COLLECTION_ID, "bounding_box": f"{west},{south},{east},{north}",
        "temporal": f"{_iso_z(checked - timedelta(days=days))},{_iso_z(checked)}",
        "sort_key": "-start_date", "page_size": 200,
    }
    url = f"{CMR_SEARCH}/granules.json?" + urllib.parse.urlencode(query)
    passes = []
    for entry in fetch(url).get("feed", {}).get("entry", []):
        match = PASS_RE.match(entry["title"])
        if not match:
            continue  # other products (Expert, WindWave, Unsmoothed) are not used here
        passes.append({
            "pass_name": entry["title"], "cycle": match.group(1), "pass": match.group(2),
            "time_start": _iso_z(datetime.fromisoformat(entry["time_start"].replace("Z", "+00:00"))),
            "time_end": _iso_z(datetime.fromisoformat(entry["time_end"].replace("Z", "+00:00"))),
            "size_mb": round(float(entry["granule_size"]), 1) if entry.get("granule_size") else None,
        })
    return {
        "passes": passes, "n_passes": len(passes), "days": days,
        "bounds": {"south": south, "north": north, "west": west, "east": east},
        "date_checked": _iso_z(checked), "source": SOURCE, "query": url,
        "note": "Footprint overlaps the box; a pass may touch only a corner. Basic product only.",
    }


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Do not follow redirects automatically: download_file follows them itself so the token stays on NASA hosts."""

    def redirect_request(self, *args: Any, **kwargs: Any) -> None:
        return None


def _is_nasa_host(host: str) -> bool:
    return host == "earthdata.nasa.gov" or host.endswith(".earthdata.nasa.gov")


def download_file(url: str, dest: Path, token: str | None = None, opener: Any = None,
                  basic: tuple[str, str] | None = None) -> int:
    """Download one file, following redirects by hand so credentials only go where NASA says they may.

    - token: `Authorization: Bearer <token>`, sent only to *.earthdata.nasa.gov hosts.
    - basic: (login, password) from ~/.netrc, sent only to the Earthdata Login host (urs.earthdata.nasa.gov).
    A cookie jar keeps the Earthdata Login session between redirects, as NASA's Python guide describes.
    """
    if not token and not basic:
        raise DataError(NO_TOKEN_MESSAGE)
    opener = opener or urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()), _NoRedirect)
    current = url
    for _ in range(MAX_REDIRECTS + 1):
        parts = urllib.parse.urlsplit(current)
        host = parts.hostname or ""
        if parts.scheme != "https":
            raise DataError("Refusing a non-https redirect while downloading.")
        headers: dict[str, str] = {}
        if token and _is_nasa_host(host):
            headers["Authorization"] = f"Bearer {token}"
        elif basic and host == NETRC_HOST:
            headers["Authorization"] = "Basic " + base64.b64encode(f"{basic[0]}:{basic[1]}".encode()).decode()
        try:
            with opener.open(urllib.request.Request(current, headers=headers), timeout=TIMEOUT_S) as response, \
                    open(dest, "wb") as handle:
                shutil.copyfileobj(response, handle)
            return dest.stat().st_size
        except urllib.error.HTTPError as exc:
            location = exc.headers.get("Location") if exc.headers is not None else None
            if exc.code in (301, 302, 303, 307, 308) and location:
                current = urllib.parse.urljoin(current, location)
                continue
            if exc.code in (401, 403):
                raise DataError(
                    f"NASA rejected the Earthdata login (HTTP {exc.code}). Check ~/.netrc, or generate a new token at "
                    f"{LOGIN_URL}, set {TOKEN_VAR}, and start a new session."
                ) from None
            raise DataError(f"NASA returned HTTP {exc.code} for this pass; it may not be available yet.") from None
        except (urllib.error.URLError, TimeoutError) as exc:
            raise DataError(f"Could not reach NASA ({exc}). Check your network connection.") from None
    raise DataError("Too many redirects while downloading.")


def read_swath(path: Path, variable: str = "ssh_karin") -> dict[str, Any]:
    """Read latitude, longitude, the height variable and its quality flag from a SWOT Basic NetCDF file.

    Reads the 'left' and 'right' swath groups when present, otherwise the root group. Values are masked by the
    file's own _FillValue and scaled by its scale_factor (netCDF4 does both).
    """
    from netCDF4 import Dataset

    with Dataset(path) as ds:
        groups = [ds.groups[g] for g in ("left", "right") if g in ds.groups] or [ds]
        out: dict[str, list[Any]] = {"lat": [], "lon": [], "value": [], "qual": []}
        for group in groups:
            for key, name in (("lat", "latitude"), ("lon", "longitude"), ("value", variable), ("qual", "ssh_karin_qual")):
                out[key].append(np.ma.asarray(group.variables[name][:]).ravel())
    return {key: np.ma.concatenate(parts) for key, parts in out.items()}


def subset_swath(data: dict[str, Any], south: float, north: float, west: float, east: float) -> dict[str, Any]:
    """Keep valid, unflagged points inside the box. Counts every point dropped and why."""
    lat = np.ma.filled(data["lat"].astype(float), np.nan)
    lon = np.ma.filled(data["lon"].astype(float), np.nan)
    lon = ((lon + 180.0) % 360.0) - 180.0  # SWOT longitudes are 0..360
    value = np.ma.filled(data["value"].astype(float), np.nan)
    unflagged = np.ma.filled(data["qual"], 1) == 0  # a masked flag counts as flagged
    inside = np.isfinite(lat) & np.isfinite(lon) & (lat >= south) & (lat <= north) & (lon >= west) & (lon <= east)
    is_fill = ~np.isfinite(value)
    keep = inside & ~is_fill & unflagged
    return {
        "lat": lat[keep], "lon": lon[keep], "value": value[keep],
        "counts": {
            "n_in_region": int(inside.sum()), "dropped_fill_value": int((inside & is_fill).sum()),
            "dropped_quality_flag": int((inside & ~is_fill & ~unflagged).sum()), "n_kept": int(keep.sum()),
        },
    }


def _out_dir(output_dir: Path | None) -> Path:
    out = output_dir or OUTPUT_DIR
    out.mkdir(parents=True, exist_ok=True)
    return out


def saved_path(pass_name: str, variable: str, output_dir: Path | None = None) -> Path:
    return _out_dir(output_dir) / f"{pass_name}__{variable}.npz"


def _check_pass(pass_name: str) -> re.Match[str]:
    match = PASS_RE.match(pass_name)
    if not match:
        raise DataError(f"'{pass_name}' is not a SWOT Basic pass name. Use a pass_name from find_swot_passes.")
    return match


def fetch_pass(pass_name: str, south: float, north: float, west: float, east: float, variable: str = "ssh_karin",
               token: str | None = None, output_dir: Path | None = None, opener: Any = None,
               basic: tuple[str, str] | None = None) -> dict[str, Any]:
    """Download one pass, cut out the region, save the kept points and return a compact summary (no arrays)."""
    match = _check_pass(pass_name)
    check_region(south, north, west, east)
    if variable not in VARIABLES:
        raise DataError(f"variable must be one of {', '.join(VARIABLES)} (ssh_karin includes the geoid; ssha_karin is the anomaly).")
    if not token and not basic:
        raise DataError(NO_TOKEN_MESSAGE)
    raw = _out_dir(output_dir) / f"{pass_name}.nc.part"
    try:
        size = download_file(f"{ARCHIVE}/{pass_name}.nc", raw, token, opener, basic)
        try:
            data = read_swath(raw, variable)
        except (OSError, KeyError, RuntimeError) as exc:
            raise DataError(f"Downloaded file could not be read as a SWOT Basic file ({type(exc).__name__}: {exc}).") from None
    finally:
        raw.unlink(missing_ok=True)  # the full pass is not kept
    sub = subset_swath(data, south, north, west, east)
    counts = sub["counts"]
    if counts["n_kept"] == 0:
        raise DataError(f"No valid points inside the region for this pass ({counts}). Try a larger region or another pass.")
    bounds = {"south": south, "north": north, "west": west, "east": east}
    start, end = _parse_stamp(match.group(3)), _parse_stamp(match.group(4))
    meta = {"pass_name": pass_name, "variable": variable, "bounds": bounds, "units": "m",
            "time_start": _iso_z(start), "time_end": _iso_z(end), "counts": counts}
    path = saved_path(pass_name, variable, output_dir)
    np.savez_compressed(path, lat=sub["lat"], lon=sub["lon"], value=sub["value"], meta=np.array(json.dumps(meta)))
    return {
        "pass_name": pass_name, "variable": variable, "units": "m", "time_start": meta["time_start"], "time_end": meta["time_end"],
        "bounds": bounds, "points": counts, "min_m": round(float(sub["value"].min()), 3), "max_m": round(float(sub["value"].max()), 3),
        "subset_file": {"path": str(path), "size_bytes": path.stat().st_size}, "downloaded_bytes": size,
        "rules": "Kept points with fill values removed and ssh_karin_qual == 0 (no flag set); longitudes converted to -180..180.",
        "source": SOURCE, "date_checked": _iso_z(datetime.now(UTC)),
    }
