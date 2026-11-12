"""Map tests: use the synthetic file and never touch the network (basemap download is switched off)."""

from pathlib import Path

import make_sample
import mapping
import pytest
import science

PASS = "SWOT_L2_LR_SSH_Basic_058_424_20261106T150521_20261106T155607_PID0_01"
BOX = dict(south=33.0, north=39.0, west=-126.0, east=-124.0)


@pytest.fixture(autouse=True)
def no_basemap_download(monkeypatch):
    """Cartopy fetches Natural Earth coastlines from the internet on first use; keep tests offline."""
    monkeypatch.setattr(mapping, "_add_basemap", lambda ax: None)


def test_map_is_a_png_and_files_are_listed(tmp_path):
    (tmp_path / "input").mkdir()
    make_sample.build(tmp_path / "input" / "s.nc")  # the synthetic input stays out of the output folder
    data = science.read_swath(tmp_path / "input" / "s.nc")
    sub = science.subset_swath(data, **BOX)
    import json

    import numpy as np
    meta = {"pass_name": PASS, "variable": "ssh_karin", "bounds": BOX, "units": "m",
            "time_start": "2026-11-06T15:05:21Z", "time_end": "2026-11-06T15:56:07Z", "counts": sub["counts"]}
    np.savez_compressed(science.saved_path(PASS, "ssh_karin", tmp_path / "out"), lat=sub["lat"], lon=sub["lon"],
                        value=sub["value"], meta=np.array(json.dumps(meta)))
    out = mapping.draw_map(PASS, "ssh_karin", tmp_path / "out")
    assert Path(out["map"]["path"]).read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
    assert out["n_points"] == 22 and out["value_range_m"] == [0.1, 0.21]
    assert out["drawn_as"].startswith("points along the swath")
    assert mapping.list_output_files(tmp_path / "out")["n_files"] == 2  # the .npz and the .png


def test_unfetched_pass_is_an_error(tmp_path):
    with pytest.raises(science.DataError, match="Fetch it first"):
        mapping.draw_map(PASS, "ssh_karin", tmp_path)
