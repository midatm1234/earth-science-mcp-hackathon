"""Scientific functions for sst-latest. No MCP imports here.

Finds the newest granule of a sea surface temperature (SST) collection in NASA's Common Metadata
Repository (CMR). Metadata only: no data files are downloaded and no credentials are used.

The network call (fetch_json) is separate from the parsing (latest_granule), so tests can feed
saved CMR responses to the parser and never touch the network.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

CMR_SEARCH = "https://cmr.earthdata.nasa.gov/search"
DEFAULT_COLLECTION = "C1996881146-POCLOUD"  # GHRSST Level 4 MUR Global Foundation SST Analysis v4.1
CONCEPT_ID_RE = re.compile(r"^C\d+-[A-Z0-9_]+$")
TIMEOUT_S = 20

Fetcher = Callable[[str], dict[str, Any]]


class DataError(ValueError):
    """An expected, explainable problem with inputs or data."""


def fetch_json(url: str) -> dict[str, Any]:
    """GET a CMR search URL and return parsed JSON. The only function here that uses the network."""
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:  # noqa: S310 - fixed https host
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raise DataError(f"NASA CMR returned HTTP {exc.code} for this request. Check the collection id or try again later.") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise DataError(f"Could not reach NASA CMR ({exc}). Check your network connection and try again.") from exc


def _parse_time(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def _iso_z(moment: datetime) -> str:
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def latest_granule(
    collection_concept_id: str = DEFAULT_COLLECTION,
    fetch: Fetcher = fetch_json,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return metadata of the newest granule in a CMR collection.

    Newest means the latest granule start time (CMR sort key -start_date). Age is measured from the
    granule's end time to `now` (UTC). Nothing is downloaded.
    """
    cid = collection_concept_id.strip()
    if not CONCEPT_ID_RE.match(cid):
        raise DataError(
            f"'{collection_concept_id}' is not a CMR collection concept id. "
            f"Use the form C<number>-<PROVIDER>, e.g. '{DEFAULT_COLLECTION}'."
        )
    checked = now or datetime.now(UTC)

    coll_url = f"{CMR_SEARCH}/collections.json?" + urllib.parse.urlencode({"concept_id": cid})
    coll_entries = fetch(coll_url).get("feed", {}).get("entry", [])
    if not coll_entries:
        raise DataError(f"No CMR collection with concept id '{cid}'. Check the id with the earthdata MCP get_collections tool.")
    coll = coll_entries[0]

    gran_url = f"{CMR_SEARCH}/granules.json?" + urllib.parse.urlencode(
        {"collection_concept_id": cid, "sort_key": "-start_date", "page_size": 1}
    )
    gran_entries = fetch(gran_url).get("feed", {}).get("entry", [])
    if not gran_entries:
        raise DataError(f"Collection '{cid}' exists but has no granules, so there is no newest granule to report.")
    gran = gran_entries[0]

    start, end = gran["time_start"], gran.get("time_end") or gran["time_start"]
    age_hours = round((checked - _parse_time(end)).total_seconds() / 3600, 1)
    return {
        "collection": {
            "concept_id": cid,
            "short_name": coll.get("short_name"),
            "title": coll.get("dataset_id"),
            "version": coll.get("version_id"),
        },
        "newest_granule": {
            "name": gran.get("producer_granule_id") or gran["title"],
            "concept_id": gran.get("id"),
            "time_start": _iso_z(_parse_time(start)),
            "time_end": _iso_z(_parse_time(end)),
            "age_hours_since_end": age_hours,
        },
        "date_checked": _iso_z(checked),
        "rules": "Newest = latest granule start time. Age = hours from granule end time to date_checked (UTC).",
        "provenance": {
            "source": "NASA Common Metadata Repository (CMR) search API",
            "queries": [coll_url, gran_url],
            "class": "live call",
        },
        "limitations": "Metadata only: this says which data exist, not the temperature values. "
                       "Granule time spans are as declared in CMR.",
    }
