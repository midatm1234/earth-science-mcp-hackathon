# MCP and Agent Skill Hackathon for Earth Science Observations and Models

Starter repository for an in-person hackathon where teams of Earth scientists give an AI assistant new, well-documented scientific capabilities: one small **MCP tool** (access to data or a calculation) and one related **agent skill** (reusable instructions for a scientific workflow), then independently test another team's work.

**New here? Open [START_HERE.md](START_HERE.md).** It is the single path from an empty laptop to a successful tool call.

| Event detail | Status |
|---|---|
| Organizer | Hugo Kyo Lee |
| Format | In person only, teams, setup clinic before the start |
| Date, venue, duration, registration | **TBD** |
| Agenda | [Provisional one-day agenda](docs/agenda.md) |
| Repository destination (public URL) | **TBD** – this copy was built locally |
| Shared MCP server endpoint | **TBD** – not needed; everything runs on laptops ([plan](docs/server-deployment-plan.md)) |

## What you need

| Requirement | Cost | Notes |
|---|---|---|
| A laptop (macOS, Windows or Linux) | – | 4 GB RAM, ~1 GB free disk, administrator rights not required |
| A **Claude subscription** that includes Claude Code | paid (the only paid item) | Sign in with your Claude account. No API credits needed. |
| uv, Claude Code, optionally Git and VS Code | free | Step-by-step in [docs/setup.md](docs/setup.md) |

Not required: Anthropic API credits, Azure OpenAI, OpenAI credits, GitHub Copilot, a cloud account, a GPU, Docker, Jupyter, a GitHub account, or prior Git experience.

## What is in this repository

| Folder | Contents |
|---|---|
| [tutorials/](tutorials/) | Six step-by-step tutorials, from first tool call to peer testing |
| [docs/](docs/) | Setup, concepts, glossary, challenge cards, peer testing, troubleshooting, facilitator guide, plans and reports |
| [servers/obs-model-starter/](servers/obs-model-starter/) | Pretested, credential-free MCP server comparing model and observation values (synthetic data) |
| [skills/](skills/) | Canonical agent skills: [obs-model-comparison](skills/obs-model-comparison/SKILL.md), [earth-data-discovery](skills/earth-data-discovery/SKILL.md) |
| [templates/](templates/) | Starting points for a new server, a new skill, discovery record, submission, peer-test report and demo |
| [catalog/](catalog/) | Records of every MCP server and skill, with separate review, verification, peer-test and hosting status ([index](catalog/index.md)) |
| [examples/data/](examples/data/) | Index of example data, including a dated cached Earthdata response |
| [scripts/](scripts/) | First call, Earthdata probe, scaffold, skill installer, validation, packaging, Claude workflow checks |
| [tests/](tests/) | Tests of the repository tooling |
| [.github/](.github/) | Pull-request checks (no secrets, no deployment), templates |

## Learning path

| Step | Tutorial | You will |
|---|---|---|
| 0 | [First tool call](tutorials/00-first-tool-call.md) | Call an MCP tool from a script and from Claude Code |
| 1 | [Discover existing capabilities](tutorials/01-discover-existing-capabilities.md) | Use Earthdata MCP and the catalog; fill a discovery record |
| 2 | [Build an MCP tool](tutorials/02-build-an-mcp-tool.md) | Extend the starter or a new server with one tested tool |
| 3 | [Create an agent skill](tutorials/03-create-an-agent-skill.md) | Write and test a SKILL.md that guides your tools |
| 4 | [Combine tools and skills](tutorials/04-combine-tools-and-skills.md) | Run a workflow across Earthdata MCP, your server and your skill |
| 5 | [Submit and test a peer](tutorials/05-submit-and-test-a-peer.md) | Freeze, submit, then independently test another team's work |

Background: [MCP and skills explained](docs/mcp-and-skills.md) · [Glossary](docs/glossary.md) · [Discovery first](docs/discovery-first.md) · [Challenge cards](docs/challenge-cards.md) · [Troubleshooting](docs/troubleshooting.md)

## Quick check (after setup)

```bash
uv sync
uv run python scripts/first_call.py
uv run python scripts/check_all.py
```

## For organizers and mentors

[Facilitator guide and rehearsal checklist](docs/facilitator-guide.md) · [Peer testing](docs/peer-testing.md) · [Compatibility](docs/compatibility.md) · [Server deployment plan](docs/server-deployment-plan.md) · [Reference review](docs/reference-review.md) · [Validation report](docs/validation-report.md) · [Contributing](CONTRIBUTING.md)

## License and attribution

Code and documentation: Apache-2.0 ([LICENSE](LICENSE), [NOTICE](NOTICE)). Synthetic sample data: CC0-1.0. Reused patterns and references: [docs/attribution.md](docs/attribution.md).
