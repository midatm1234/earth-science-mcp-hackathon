# Submission form

This form is submitted with your pull request. See [tutorial 05](../../tutorials/05-submit-and-test-a-peer.md).

| Field | Value |
|---|---|
| Team name (slug) | test |
| Team members (names or initials) | team test |
| MCP server id | `servers/sst-latest`, `servers/swot-ssh` |
| Agent skill id | `skills/sst-latest-check`, `skills/sst-map-workflow`, `skills/swot-ssh-workflow` |
| Version | 0.1.0 |
| Frozen reference | git commit SHA, recorded as `source.ref` in each catalog entry |
| Discovery record | `submissions/<team>/discovery-record.md` |

## Checklist (all must be ticked before the freeze)

- [x] `uv run python scripts/check_all.py` passes on our machine (paste the last line below): `ALL CHECKS PASSED`.
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
| Tests | `uv run pytest servers/<name>/tests` (run inside `check_all.py`) | pass | `server:sst-latest` and `server:swot-ssh` PASS |
| Repository checks | `uv run python scripts/check_all.py` | pass | `ALL CHECKS PASSED` |
| MCP tool call (no AI) | not run | pending | |
| Skill, explicit | `/sst-map-workflow` and `/swot-ssh-workflow`, eastern tropical Pacific (10S to 10N, 120W to 80W) | pass (Claude Code) | sst-latest: get_newest_sst_dates, fetch_sst_subset x10, draw_sst_map, make_sst_gif, list_sst_output_files; swot-ssh: find_swot_passes, fetch_swot_pass, draw_swot_map, list_swot_output_files |
| Skill, natural trigger | not run | pending | |
| Skill, should not apply | not run | pending | |
| Platform | macOS (Darwin), Claude Code in VS Code; Copilot and Codex not tested | partial | Python and assistant versions not recorded |

## Notes for reviewers

- `swot-ssh` needs a free Earthdata Login (`EARTHDATA_TOKEN` or a `~/.netrc` entry) for `fetch_swot_pass`. Peer testers without one can run `find_swot_passes` only.
- Both servers need network access (NASA CMR, NOAA ERDDAP, PO.DAAC). Cartopy downloads coastlines on first map.
- `sst-latest-check` was not exercised in this session's end-to-end run.
- The discovery record (`discovery-record.md`) and demo plan (`demo.md`) are still the blank templates: pending.
- Not peer-tested, not hosted.
