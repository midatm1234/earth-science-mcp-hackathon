## Contribution

<!-- One MCP server and/or one related skill per pull request. Mentor-assisted
submissions use the same form: templates/submission.md -->

| Field | Value |
|---|---|
| Team | |
| MCP server | `servers/<name>` |
| Agent skill | `skills/<name>` |
| Discovery record | `submissions/<team>/discovery-record.md` |
| Route | pull request / mentor-assisted (opened by mentor on behalf of team) |

## Checklist

- [ ] `uv run python scripts/check_all.py` passes locally (paste last line):
- [ ] Catalog entries filled in; `uv run python scripts/catalog.py index` re-run
- [ ] Server README: scientific conventions (units, coordinates, spatial/temporal support, version, missing data, processing, provenance, limits)
- [ ] No credentials or `.env` files; fixtures ≤ 1 MB with provenance and license
- [ ] Skill checked: explicit invocation, natural trigger, should-not-apply case (in `submissions/<team>/submission.md`)

## Notes for reviewers

<!-- Status fields are separate: merging this PR sets review status only. It does
not mean the server is hosted, and it is not a peer test. -->
