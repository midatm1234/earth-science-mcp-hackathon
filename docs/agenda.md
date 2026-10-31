# Agenda (provisional)

> **Provisional.** Date, venue, duration and registration are **TBD**. This is a proposed one-day, in-person format. If the organizer confirms a different duration, keep the proportions and keep the final substantive block for peer testing.

| Time | Block | Content | Materials |
|---|---|---|---|
| 08:00–08:45 | Setup clinic (doors open) | Mentors run the [setup checks](setup.md#what-the-setup-clinic-checks) with every participant | [START_HERE](../START_HERE.md), [troubleshooting](troubleshooting.md) |
| 08:45–09:00 | Welcome | Goals, teams, code of conduct, how the day ends (peer testing) | this page |
| 09:00–09:30 | First tool call | Everyone completes stdio, HTTP and Claude Code calls | [Tutorial 00](../tutorials/00-first-tool-call.md) |
| 09:30–09:50 | Concepts | Host, client, server, tool, catalog, skill; transports; hosting vs installing | [MCP and skills](mcp-and-skills.md) |
| 09:50–10:05 | Break | | |
| 10:05–10:50 | Discovery first | Teams pick a challenge card, run both checks, decision signed off by mentor | [Tutorial 01](../tutorials/01-discover-existing-capabilities.md), [challenge cards](challenge-cards.md) |
| 10:50–12:20 | Build | Team work on one tool with tests | [Tutorial 02](../tutorials/02-build-an-mcp-tool.md) |
| 12:20–13:05 | Lunch | Mentors check each team runs `check_all.py --fast` | |
| 13:05–13:50 | Skill | Write, install and test the skill (explicit, natural, negative) | [Tutorial 03](../tutorials/03-create-an-agent-skill.md) |
| 13:50–14:20 | Combine | Earthdata MCP + team tool + skill in one session | [Tutorial 04](../tutorials/04-combine-tools-and-skills.md) |
| 14:20–14:40 | Freeze and submit | `check_all.py`, package, record SHA-256, PR or mentor-assisted | [Tutorial 05 part A](../tutorials/05-submit-and-test-a-peer.md#part-a--freeze-and-submit-20-minutes-before-the-peer-testing-block) |
| 14:40–14:55 | Break + mentor freeze check | Mentors verify frozen version, package, setup command, fixture, 5-minute example | [Peer testing](peer-testing.md#before-the-block-freeze-check) |
| **14:55–16:25** | **Peer testing (90 min, protected)** | 10 handoff · 25 round 1 · 25 round 2 · 20 repair and retest · 10 record outcomes | [Peer testing](peer-testing.md), [report template](../templates/peer-test-report.md) |
| 16:25–17:10 | Closing session | 4-minute demos that include the independent peer-test result; no development | [Demo template](../templates/demo.md) |
| 17:10–17:30 | Wrap-up | Catalog status, what happens to contributions, feedback form (**TBD**) | [catalog/index.md](../catalog/index.md) |

Rules for the protected block:

- Development stops at the freeze (14:40). Only fixes to blockers reported by reviewers are allowed, during the 20-minute repair window, as a new frozen version.
- Presentations happen only in the closing session. If the day runs late, the closing session is shortened or demos are cut – never the peer-testing block.
- With 10+ teams, run demos in parallel rooms or as a poster round.

Setup clinic: also offered as a remote or drop-in session before the event (date **TBD**) so participants arrive with step 4 of START_HERE done.
