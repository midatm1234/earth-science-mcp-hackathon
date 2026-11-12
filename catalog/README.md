# Catalog

Records of every MCP server and agent skill contributed to (or referenced by) the hackathon. Browse the generated [index](index.md), or search:

```bash
uv run python scripts/catalog.py search <words>
uv run python scripts/catalog.py show <id>
```

One YAML file per artifact in [entries/](entries/); peer-test reports in [peer-tests/](peer-tests/). After editing entries run `uv run python scripts/catalog.py index`. The validator (`scripts/validate_repo.py --only catalog`) enforces the fields below.

## Fields

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | Stable identifier = file name = folder name in `servers/` or `skills/`. Lowercase, hyphens. |
| `type` | yes | `mcp-server` or `agent-skill` |
| `origin` | yes | `event` (contributed here) or `external` (listed for discovery, not reviewed by the event) |
| `title` | yes | Short title |
| `scientific_purpose` | yes | The scientific question it helps answer |
| `team`, `authors` | yes | Author team and members (names or initials, as they choose) |
| `version` | yes | Semantic version |
| `source.path`, `source.ref` | yes | Folder and immutable reference: commit SHA (`TBD-at-freeze` before freezing) |
| `license`, `attribution` | yes | License of the artifact; anything reused and its license |
| `data.classes`, `data.volume`, `data.provenance` | yes | `synthetic`, `cached live response`, `recorded demonstration`, `live call`, `real public data`, `user-supplied`; size; where provenance is documented |
| `credentials` | yes | `none`, or each account/key needed and how to obtain it (never the value) |
| `network` | yes | `none` or which services are called |
| `dependencies` | yes | Python range and pinned packages |
| `client_name` | servers | Server name used in `.mcp.json` and `.codex/config.toml` |
| `tools` | servers | Tool names offered |
| `requires_mcp_tools` | skills | `<client_name>/<tool>` for each MCP tool the skill needs (validated against server entries). Each assistant adds its own prefix when it shows the tool. |
| `transports` | servers | `stdio`, `streamable-http` |
| `install`, `run` | yes | Exact commands |
| `runtime` | yes | Typical time per call or per agent task |
| `example` | yes | Example input/prompt and expected output |
| `tests.command`, `tests.evidence` | yes | How to test; where the evidence is |
| `status.review` | yes | Organizers' decision: draft, submitted, in-review, changes-requested, accepted, withdrawn, external |
| `status.local_verification` | yes | Authors' own verification: `result` (pass/partial/fail/not-run), date, by, platform, evidence |
| `status.peer_testing` | yes | List of `{report: catalog/peer-tests/<file>.md, result: pass/partial/fail/blocked}` |
| `status.hosting` | yes | not-hosted, planned, hosted (needs a real `endpoint`), external, not-applicable |

The four `status` fields are deliberately separate. Accepting or merging an entry does not mean a service is running, and a passing local verification is not a peer test.
