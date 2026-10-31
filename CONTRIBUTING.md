# Contributing

Each team contributes **one small MCP server change (new server or extension) and one related agent skill**, plus a discovery record and a submission form. Two routes lead to the same review:

| Route | For | Steps |
|---|---|---|
| Pull request | Participants with a GitHub account | branch → commit → push → PR (tutorial 05, [part A, step 3a](tutorials/05-submit-and-test-a-peer.md#3a-pull-request-route-if-you-use-github)) |
| Mentor-assisted | Anyone, no GitHub needed | package ZIP → mentor verifies and opens the PR ([part A, step 3b](tutorials/05-submit-and-test-a-peer.md#3b-mentor-assisted-route-no-github-needed)) |

The required files and metadata are identical for both routes.

## Start

```bash
uv run python scripts/new_contribution.py --team <team-slug> --server <server-name> --skill <skill-name>
```

Names: 3–40 characters, lowercase letters and digits separated by single hyphens, starting with a letter.

## Required files

| Path | Required content |
|---|---|
| `servers/<server>/server.py` | MCP wrapper: `@mcp.tool` functions, `--transport stdio\|http`, logs to stderr only |
| `servers/<server>/science.py` (or other modules) | Scientific functions with no MCP imports |
| `servers/<server>/requirements.txt` | Exact pins (`==`) matching `uv.lock` |
| `servers/<server>/tests/test_*.py` | Hand-checked science tests; at least one real MCP `call_tool` via `mcp.Client`; one invalid-input test checking `is_error` |
| `servers/<server>/README.md` | Purpose, tools, scientific conventions, run commands, example input/output, limitations |
| `servers/<server>/data/README.md` | If data are bundled: provenance, class (synthetic/cached/real), license, ≤ 1 MB per file |
| `skills/<skill>/SKILL.md` | Valid frontmatter; sections When to use, When not to use, Required tools, Procedure, Expected output, Assumptions, Limitations, Example tasks |
| `catalog/entries/<server>.yaml`, `catalog/entries/<skill>.yaml` | All fields ([catalog/README.md](catalog/README.md)) |
| `submissions/<team>/discovery-record.md` | Both discovery checks and the decision |
| `submissions/<team>/submission.md` | Checklist and verification evidence |

Extending `obs-model-starter` instead of creating a server: edit its files, add tests, add the new tool to its catalog entry, and describe the change in your submission.

## Rules

- **No credentials** in any file, test, fixture or image. Read secrets from environment variables; describe them in the catalog entry. `.env` is never committed.
- **No large data.** ≤ 1 MB per fixture, ≤ 5 MB per file. Link to sources; generate synthetic stand-ins when redistribution is unclear.
- **Dependencies** must be pinned, added to `pyproject.toml` (`uv add pkg==X.Y.Z`) and locked (`uv lock`). Prefer the standard library.
- **Automated checks must not need** Claude, LLM credentials, paid APIs or network access. Live checks go in scripts that are run manually and recorded.
- **Scientific quality:** state units, coordinate conventions, spatial and temporal support, dataset/model version, missing-data handling, processing choices, provenance and interpretation limits ([checklist](docs/challenge-cards.md#scientific-quality-checklist)).
- **Labels:** distinguish synthetic data, cached responses, recorded demonstrations and live calls everywhere.
- **Licenses:** contributions default to Apache-2.0 for code. Reuse only material whose license allows it, and record attribution.

## Checks

```bash
uv run python scripts/catalog.py index
uv run python scripts/check_all.py
```

`check_all.py` runs: metadata/catalog validation, required files, skill syntax, dependency pins vs lock, secret scan, file sizes, relative links and anchors, presence of meaningful tool tests, fixture reproducibility, each server's tests in isolation, and tooling tests. The same runs in CI ([checks.yml](.github/workflows/checks.yml)) on pull requests, without secrets.

## Review and status

Catalog status fields are independent; changing one never changes another:

| Field | Set by | Values |
|---|---|---|
| `status.review` | organizers | draft, submitted, in-review, changes-requested, accepted, withdrawn |
| `status.local_verification` | authors | pass, partial, fail, not-run + date, platform, evidence |
| `status.peer_testing` | reviewers | list of reports with pass, partial, fail, blocked |
| `status.hosting` | organizers, after deployment | not-hosted, planned, hosted (+ endpoint), external, not-applicable |

A merged pull request or an accepted entry does **not** mean a service is running. Nothing is deployed on merge ([deployment plan](docs/server-deployment-plan.md)).

## Freezing a version

Before peer testing: `uv run python scripts/package.py contribution <id>` for each artifact; record the SHA-256 (or commit SHA) as `source.ref`. Changes after the freeze require a new version.
