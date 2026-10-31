# Submission form

The same form is used for both routes: **pull request** and **mentor-assisted**. See [tutorial 05](../tutorials/05-submit-and-test-a-peer.md).

| Field | Value |
|---|---|
| Team name (slug) | |
| Team members (names or initials) | |
| Route | pull request / mentor-assisted |
| MCP server id | `servers/<name>` |
| Agent skill id | `skills/<name>` |
| Version | 0.1.0 |
| Frozen reference | git commit SHA or archive SHA-256 (from `scripts/package.py`) |
| Discovery record | `submissions/<team>/discovery-record.md` |

## Checklist (all must be ticked before the freeze)

- [ ] `uv run python scripts/check_all.py` passes on our machine (paste the last line below).
- [ ] Catalog entries `catalog/entries/<server>.yaml` and `<skill>.yaml` are filled in (no `REPLACE`).
- [ ] Server README has every section, including scientific conventions and limitations.
- [ ] Fixture data are ≤ 1 MB each, redistributable, and described in `data/README.md`.
- [ ] No credentials in any file. Any needed account is described in the catalog entry.
- [ ] Setup command tested from a clean session: ______________________
- [ ] Example runs in under five minutes, including setup on a laptop with common dependencies.
- [ ] Skill invoked explicitly, by a natural request, and correctly **not** used for an unrelated request (record below).
- [ ] Skill can reach its MCP tools (tool calls visible in the transcript).

## Verification evidence

| Check | Command or prompt | Result (pass/partial/fail/blocked) | Evidence |
|---|---|---|---|
| Tests | `uv run pytest servers/<name>/tests` | | e.g. "7 passed" |
| Repository checks | `uv run python scripts/check_all.py` | | last line |
| MCP tool call (no AI) | e.g. small client script or MCP Inspector | | |
| Skill, explicit | `/<skill> ...` | | tool names called |
| Skill, natural trigger | "..." | | |
| Skill, should not apply | "..." | | |
| Platform | OS, Python, AI assistant(s) and version(s) | | |

## Notes for reviewers

<!-- Anything a peer tester must know: setup quirks, expected warnings, known limitations. -->
