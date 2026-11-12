"""Tests for fetching, mapping and animating SST. They use saved ERDDAP responses and never touch the network."""

import json
from pathlib import Path

import mapping
import pytest

DATA = Path(__file__).resolve().parent / "data"
BOX = dict(south=33.0, north=37.0, west=-123.0, east=-119.0)


@pytest.fixture(autouse=True)
def no_basemap_download(monkeypatch):
    """Cartopy fetches Natural Earth coastlines from the internet on first use; keep tests offline."""
    monkeypatch.setattr(mapping, "_add_basemap", lambda ax: None)


def saved_fetch(url: str) -> str:
    if "analysed_sst" in url:
        day = "2026-11-10" if "2026-11-10" in url else "2026-11-09"
        return (DATA / f"erddap_sst_{day}.csv").read_text(encoding="utf-8")
    return (DATA / "erddap_times.csv").read_text(encoding="utf-8")


def test_newest_dates_hand_counted():
    out = mapping.newest_available_dates(10, fetch=saved_fetch)
    assert len(out["dates"]) == 10
    assert out["dates"][0] == "2026-11-01" and out["dates"][-1] == "2026-11-10"
    assert out["newest"] == "2026-11-10T09:00:00Z"
    assert "time[last-9:1:last]" in out["query"]


def test_subset_values_match_the_saved_file():
    out = mapping.fetch_regional_subset("2026-11-10", **BOX, fetch=saved_fetch)
    assert out["units"] == "degC"
    # The saved file has 9 x 9 = 81 grid points; 32 are land (NaN) and are dropped, leaving 49 (counted with grep).
    assert out["n_points"] == len(out["values"]) == 49
    assert (out["lats"][0], out["lons"][0], out["values"][0]) == (33.0, -123.0, 17.794)  # first data row, by eye


def test_request_is_a_thinned_regional_subset():
    seen = []

    def spy(url):
        seen.append(url)
        return saved_fetch(url)

    mapping.fetch_regional_subset("2026-11-10", **BOX, fetch=spy)
    assert "(33.0):" in seen[0] and "(-123.0):" in seen[0]  # a region, never the whole globe
    assert mapping._stride(0, 40, -180, -140) > mapping._stride(33, 37, -123, -119)  # bigger box, coarser grid


@pytest.mark.parametrize("args, message", [
    ((-91, 37, -123, -119), "Latitudes"),
    ((33, 37, -123, 190), "Longitudes"),
    ((0, 60, -170, -120), "too large"),
])
def test_bad_regions_give_helpful_errors(args, message):
    with pytest.raises(mapping.DataError, match=message):
        mapping.fetch_regional_subset("2026-11-10", *args, fetch=saved_fetch)


def test_bad_date_is_an_error():
    with pytest.raises(mapping.DataError, match="YYYY-MM-DD"):
        mapping.fetch_regional_subset("yesterday", **BOX, fetch=saved_fetch)


def test_map_and_gif_are_written(tmp_path):
    for day in ("2026-11-09", "2026-11-10"):
        out = mapping.fetch_and_save(day, **BOX, output_dir=tmp_path, fetch=saved_fetch)
        assert "values" not in out and out["subset_file"]["size_bytes"] > 0  # summary only, never arrays
    png = mapping.draw_saved_map("2026-11-10", output_dir=tmp_path)
    assert Path(png["map"]["path"]).read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
    gif = mapping.make_saved_gif(["2026-11-10", "2026-11-09"], output_dir=tmp_path)
    assert gif["n_frames"] == 2 and gif["dates"] == ["2026-11-09", "2026-11-10"]  # sorted oldest first
    from PIL import Image

    with Image.open(gif["gif"]["path"]) as im:
        assert im.format == "GIF" and im.n_frames == 2
    listed = mapping.list_output_files(tmp_path)
    assert {Path(f["path"]).suffix for f in listed["files"]} == {".json", ".png", ".gif"}


def test_unfetched_date_and_short_animation_are_errors(tmp_path):
    with pytest.raises(mapping.DataError, match="Fetch that date first"):
        mapping.draw_saved_map("2026-11-10", output_dir=tmp_path)
    with pytest.raises(mapping.DataError, match="between 2 and"):
        mapping.make_saved_gif(["2026-11-10"], output_dir=tmp_path)


def test_unsafe_file_name_is_refused(tmp_path):
    subset = json.loads(json.dumps(mapping.fetch_regional_subset("2026-11-10", **BOX, fetch=saved_fetch)))
    with pytest.raises(mapping.DataError, match="letters, digits"):
        mapping.draw_map(subset, name="../escape", output_dir=tmp_path)
