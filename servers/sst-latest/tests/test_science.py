"""Science tests. They use saved CMR responses in tests/data/ and never touch the network."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
import science

DATA = Path(__file__).resolve().parent / "data"
NOW = datetime(2026, 11, 11, 21, 0, tzinfo=UTC)  # exactly 24 h after the saved granule's end time


def saved_fetch(url: str) -> dict:
    name = "cmr_collections_mur.json" if "collections.json" in url else "cmr_granules_mur.json"
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def test_latest_granule_hand_computed():
    out = science.latest_granule(fetch=saved_fetch, now=NOW)
    assert out["collection"]["concept_id"] == "C1996881146-POCLOUD"
    assert out["collection"]["short_name"] == "MUR-JPL-L4-GLOB-v4.1"
    granule = out["newest_granule"]
    assert granule["name"] == "20261110090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1"
    assert granule["time_start"] == "2026-11-09T21:00:00Z"
    assert granule["time_end"] == "2026-11-10T21:00:00Z"
    assert granule["age_hours_since_end"] == 24.0  # 2026-11-10T21:00Z -> 2026-11-11T21:00Z
    assert out["date_checked"] == "2026-11-11T21:00:00Z"
    assert out["provenance"]["class"] == "live call"


def test_asks_cmr_for_newest_first_one_granule():
    urls = []

    def spy(url: str) -> dict:
        urls.append(url)
        return saved_fetch(url)

    science.latest_granule(fetch=spy, now=NOW)
    assert any("sort_key=-start_date" in u and "page_size=1" in u for u in urls)


def test_malformed_id_is_an_error():
    with pytest.raises(science.DataError, match="concept id"):
        science.latest_granule("sea surface temperature", fetch=saved_fetch)


def test_unknown_collection_is_an_error():
    with pytest.raises(science.DataError, match="No CMR collection"):
        science.latest_granule(fetch=lambda url: {"feed": {"entry": []}}, now=NOW)


def test_collection_without_granules_is_an_error():
    def fetch(url: str) -> dict:
        return saved_fetch(url) if "collections.json" in url else {"feed": {"entry": []}}

    with pytest.raises(science.DataError, match="no granules"):
        science.latest_granule(fetch=fetch, now=NOW)
