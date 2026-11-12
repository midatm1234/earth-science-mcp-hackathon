"""Science tests with hand-computed values. They use a saved CMR response and a tiny synthetic NetCDF file,
and never touch the network."""

import io
import json
import urllib.error
from datetime import UTC, datetime
from pathlib import Path

import make_sample
import pytest
import science

DATA = Path(__file__).resolve().parent / "data"
NOW = datetime(2026, 11, 8, 0, 0, tzinfo=UTC)
PASS = "SWOT_L2_LR_SSH_Basic_058_424_20261106T150521_20261106T155607_PID0_01"
BOX = dict(south=33.0, north=39.0, west=-126.0, east=-124.0)


def saved_fetch(url: str) -> dict:
    return json.loads((DATA / "cmr_swot_passes.json").read_text(encoding="utf-8"))


def test_find_passes_lists_basic_passes_newest_first():
    out = science.find_passes(**BOX, days=10, fetch=saved_fetch, now=NOW)
    assert out["n_passes"] == 4
    assert out["passes"][0]["pass_name"] == PASS
    assert out["passes"][0]["time_start"] == "2026-11-06T15:05:06Z"
    assert out["passes"][0]["cycle"] == "058" and out["passes"][0]["pass"] == "424"
    assert out["date_checked"] == "2026-11-08T00:00:00Z"
    assert "bounding_box=-126.0%2C33.0%2C-124.0%2C39.0" in out["query"]
    assert "temporal=2026-10-29T00%3A00%3A00Z%2C2026-11-08T00%3A00%3A00Z" in out["query"]  # exactly 10 days


@pytest.mark.parametrize("kwargs, message", [
    (dict(south=-91, north=37, west=-125, east=-120), "Latitudes"),
    (dict(south=33, north=37, west=-125, east=190), "Longitudes"),
    (dict(south=0, north=60, west=-170, east=-120), "too large"),
])
def test_bad_regions_give_helpful_errors(kwargs, message):
    with pytest.raises(science.DataError, match=message):
        science.find_passes(**kwargs, fetch=saved_fetch)


def test_subset_drops_fill_and_flagged_points_by_hand_count(tmp_path):
    make_sample.build(tmp_path / "s.nc")
    data = science.read_swath(tmp_path / "s.nc")
    assert data["value"].size == 24  # 2 swaths x 4 lines x 3 pixels
    sub = science.subset_swath(data, **BOX)
    # All 24 points lie inside the box (lat 34..37, lon -125.0..-124.4 after the 0..360 conversion).
    # Hand count: 1 fill value (left[0,0]) and 1 flagged point (left[1,1]) are dropped -> 22 kept.
    assert sub["counts"] == {"n_in_region": 24, "dropped_fill_value": 1, "dropped_quality_flag": 1, "n_kept": 22}
    assert float(sub["lon"].min()) == pytest.approx(-125.0)
    # Values are 0.100, 0.110, ... 0.210 m in each swath. left[0,0] (0.100) is the fill value, but right[0,0] (0.100) is valid,
    # so the smallest kept value is still 0.100; the largest is 0.210.
    assert float(sub["value"].min()) == pytest.approx(0.1)
    assert float(sub["value"].max()) == pytest.approx(0.21)
    assert sorted(set(sub["value"].round(3)))[:2] == [0.1, 0.11]  # scale_factor applied: raw 100 -> 0.1 m, not 100


def test_region_clips_points(tmp_path):
    make_sample.build(tmp_path / "s.nc")
    sub = science.subset_swath(science.read_swath(tmp_path / "s.nc"), 34.5, 36.5, -126, -124)
    assert sub["counts"]["n_in_region"] == 12  # lat 35 and 36 only: 2 lines x 3 pixels x 2 swaths


class FakeOpener:
    """Stands in for the network: first a redirect to another NASA host, then the file."""

    def __init__(self, payload: bytes, status_first: int = 302):
        self.payload, self.status_first, self.calls = payload, status_first, []

    def open(self, request, timeout=None):
        self.calls.append((request.full_url, request.get_header("Authorization")))
        if len(self.calls) == 1 and self.status_first in (301, 302):
            headers = {"Location": "https://data.example.org/file.nc"}
            raise urllib.error.HTTPError(request.full_url, self.status_first, "redirect", headers, io.BytesIO())
        if self.status_first in (401, 403):
            raise urllib.error.HTTPError(request.full_url, self.status_first, "no", {}, io.BytesIO())
        return io.BytesIO(self.payload)


def test_token_is_sent_only_to_nasa_hosts(tmp_path):
    opener = FakeOpener(b"abc")
    size = science.download_file(f"{science.ARCHIVE}/x.nc", tmp_path / "x.nc", "SECRET", opener)
    assert size == 3
    assert opener.calls[0] == (f"{science.ARCHIVE}/x.nc", "Bearer SECRET")  # NASA host: header sent
    assert opener.calls[1] == ("https://data.example.org/file.nc", None)  # other host: header NOT sent


def test_netrc_login_goes_only_to_the_earthdata_login_host(tmp_path):
    class TwoHop(FakeOpener):
        def open(self, request, timeout=None):
            self.calls.append((request.full_url, request.get_header("Authorization")))
            if len(self.calls) == 1:
                raise urllib.error.HTTPError(request.full_url, 302, "r", {"Location": "https://urs.earthdata.nasa.gov/oauth"}, io.BytesIO())
            if len(self.calls) == 2:
                raise urllib.error.HTTPError(request.full_url, 302, "r", {"Location": f"{science.ARCHIVE}/x.nc?code=1"}, io.BytesIO())
            return io.BytesIO(b"abc")

    opener = TwoHop(b"")
    science.download_file(f"{science.ARCHIVE}/x.nc", tmp_path / "x.nc", opener=opener, basic=("me", "pw"))
    # Authorization must be present only on the second call (urs.earthdata.nasa.gov), expected Basic base64("me:pw").
    assert [a for _, a in opener.calls] == [None, "Basic bWU6cHc=", None]


def test_no_credentials_stops_before_any_request(tmp_path):
    with pytest.raises(science.DataError, match="netrc"):
        science.download_file(f"{science.ARCHIVE}/x.nc", tmp_path / "x.nc", opener=FakeOpener(b""))


def test_rejected_token_gives_helpful_error_without_the_token(tmp_path):
    with pytest.raises(science.DataError) as err:
        science.download_file(f"{science.ARCHIVE}/x.nc", tmp_path / "x.nc", "SECRET", FakeOpener(b"", 401))
    assert "generate a new token" in str(err.value) and "SECRET" not in str(err.value)


def test_missing_token_stops_before_any_download(tmp_path):
    with pytest.raises(science.DataError, match="EARTHDATA_TOKEN"):
        science.fetch_pass(PASS, **BOX, token=None, output_dir=tmp_path, opener=FakeOpener(b""))


def test_fetch_pass_end_to_end_with_synthetic_file(tmp_path):
    make_sample.build(tmp_path / "sample.nc")
    opener = FakeOpener((tmp_path / "sample.nc").read_bytes(), status_first=200)
    out = science.fetch_pass(PASS, **BOX, token="SECRET", output_dir=tmp_path, opener=opener)
    assert out["points"]["n_kept"] == 22 and out["points"]["dropped_fill_value"] == 1
    assert out["units"] == "m" and out["min_m"] == 0.1 and out["max_m"] == 0.21
    assert "SECRET" not in json.dumps(out)
    assert not list(tmp_path.glob("*.part"))  # the full download is removed
    assert Path(out["subset_file"]["path"]).exists()


def test_bad_pass_name_and_variable_are_errors(tmp_path):
    with pytest.raises(science.DataError, match="pass name"):
        science.fetch_pass("../etc/passwd", **BOX, token="t", output_dir=tmp_path)
    with pytest.raises(science.DataError, match="variable"):
        science.fetch_pass(PASS, **BOX, variable="bogus", token="t", output_dir=tmp_path)
