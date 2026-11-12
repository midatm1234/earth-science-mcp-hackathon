import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture(autouse=True)
def no_real_credentials(monkeypatch):
    """Tests must never use the developer's real Earthdata login or reach the network with it."""
    monkeypatch.delenv("EARTHDATA_TOKEN", raising=False)
    monkeypatch.setattr("science.get_netrc_login", lambda: None)
