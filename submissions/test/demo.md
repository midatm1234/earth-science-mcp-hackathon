# Demo plan (5 minutes)

Adapted from the EVE hackathon demonstration format. Show observable evidence: tool names, arguments, outputs and errors. Do not show slides of code you did not run.

| Part | Time | Content |
|---|---|---|
| 1. Scientific problem and user question | 30 s | |
| 2. Tools and skill used | 30 s | MCP server(s) and tool names; skill name; existing capabilities reused (e.g. Earthdata MCP) |
| 3. Inputs and outputs | 30 s | data sources, versions, units; output fields |
| 4. Concrete question 1 (live) | 60 s | prompt → tool calls → answer |
| 5. Concrete question 2 (live) | 60 s | prompt → tool calls → answer |
| 6. One error case (live) | 30 s | invalid input → readable error → how the agent recovers |
| 7. Provenance and limitations | 30 s | synthetic/cached/live; what must not be concluded |
| 8. Catalog entry and peer-test result | 30 s | `catalog/entries/<id>.yaml`; reviewer team; pass/partial/fail/blocked |

## Prompts we will use

1. Question 1:
2. Question 2:
3. Error case:

## Fallback if the live agent is unavailable

Run the same tool calls with a plain MCP client and say clearly that the agent part is **not** being shown live. A recording may be shown only if it is labelled "recorded demonstration" with its date.
