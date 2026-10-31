# Attribution

| What | Source | License | How it is used here |
|---|---|---|---|
| Secret-scanning regular expressions in [validate_repo.py](../scripts/validate_repo.py) | [eve-esa/mcp-tool-registry](https://github.com/eve-esa/mcp-tool-registry) `scripts/validate_pr.py` (reviewed at commit `a49119d`) | Apache-2.0 | Adapted (extended and modified). Notice in [NOTICE](../NOTICE). |
| One-folder-per-server layout, dual-transport `server.py`, pinned requirements, file-size limit, CODEOWNERS for infrastructure | same registry | Apache-2.0 | Patterns reimplemented in original code |
| Discover → Verify → Access workflow | [earthdata-mcp](https://github.com/midatm1234/earthdata-mcp) server instructions | no license file found | Idea described in original words; no text or code copied |
| Instructional progression (tool → agent → MCP → skills) | [Tutorial-Agentic-AI](https://github.com/midatm1234/Tutorial-Agentic-AI) | no license file found | Idea only; all exercises rewritten |
| Concept explanations (host/client/server, logs to stderr, compact outputs), demo format, recorded-vs-live labelling, spatial-dependence limits | EVE `MCP-Handbook.ipynb`, `START_HERE.ipynb` (Pi School / ESA Φ-lab EVE project) | not stated | Ideas summarised in original words; nothing copied; images not reused |
| Agent Skills format | [agentskills.io specification](https://agentskills.io/specification) | – | Followed as a format |
| Model Context Protocol | [modelcontextprotocol.io](https://modelcontextprotocol.io/) | – | Protocol; SDK `mcp` (MIT) used as a dependency |
| Live metadata in [examples/data/cached/](../examples/data/cached/) | NASA CMR via Earthdata MCP | NASA metadata, public | Dated cached response; cite dataset DOIs shown in it (e.g. MERRA-2 M2TMNXSLV, DOI 10.5067/AP1B0BA5PD2K) |
| Synthetic fixtures | generated here | CC0-1.0 | – |
| Apache License 2.0 text | apache.org | – | [LICENSE](../LICENSE) |

Please cite the EVE project when building on the registry patterns:

> Atrio, À. R. et al. (2026). EVE: A Domain-Specific LLM Framework for Earth Intelligence. arXiv:2604.13071.

Contributions keep their authors' copyright and the license stated in their catalog entry. Team members may appear by name or initials, as they choose ([mentor-assisted form](../.github/ISSUE_TEMPLATE/mentor-assisted-submission.md)).
