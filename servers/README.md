# Servers

One folder per MCP server. Each folder is self-contained: `server.py` (MCP wrapper), science module(s), pinned `requirements.txt`, `tests/`, `README.md`, and optional `data/` with a data card.

| Server | Purpose | Credentials | Transports |
|---|---|---|---|
| [obs-model-starter](obs-model-starter/README.md) | Monthly model-vs-observation bias and RMSE at a site (synthetic sample data) | none | stdio, Streamable HTTP |

Create a new one with `uv run python scripts/new_contribution.py --team <team> --server <name>`; rules in [CONTRIBUTING.md](../CONTRIBUTING.md). Each server's tests run in their own process (`scripts/check_all.py`), so contributions stay isolated.
