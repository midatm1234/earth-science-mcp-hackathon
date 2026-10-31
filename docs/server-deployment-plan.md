# Server deployment plan (future, provider-neutral)

**Status: not deployed. Deployment is disabled.** The core workshop runs entirely on laptops. This plan prepares an organizer-managed shared server for later; it does not choose a provider and does not assume that the EVE registry's AWS configuration provisions anything for this event. The endpoint is **TBD**.

Nothing in this repository deploys on merge. The only workflow, [.github/workflows/checks.yml](../.github/workflows/checks.yml), runs read-only checks with no secrets. A deployment workflow may be added only after the organizer provides and authorizes the host configuration, and it must be triggered manually per reviewed contribution.

## Goals

- Let participants or later users connect to reviewed contributions without installing Python.
- Keep every contribution isolated from the others and from deployment secrets.
- Make "hosted" an explicit, verified status in the catalog, separate from review and peer testing.

## Architecture

```text
client (Claude Code, MCP Inspector, scripts)
   │ HTTPS  (Streamable HTTP, POST /mcp/<server-id>)
   ▼
reverse proxy / gateway  ── TLS, auth, rate limits, request size limits, access logs
   │ internal network only
   ├─► container: obs-model-starter   (non-root, read-only FS, CPU/memory caps, no secrets)
   ├─► container: team-a-tools
   └─► container: team-b-tools
```

One container per contribution, built from the frozen reference (commit SHA or archive SHA-256) recorded in the catalog.

## Endpoint configuration

| Item | Plan |
|---|---|
| URL scheme | `https://<host TBD>/mcp/<server-id>` – one path per catalog id |
| Transport | Streamable HTTP only, stateless (`stateless_http=True`), JSON responses |
| Server start | `python server.py --transport http --host 0.0.0.0 --port 8000` inside the container (laptops keep `127.0.0.1`) |
| Client config | `claude mcp add --transport http <server-id> https://<host>/mcp/<server-id>`; `.env.example` reserves `HACKATHON_SHARED_MCP_URL` |
| Health | `GET /healthz` on the gateway; per-server readiness = successful `tools/list` |

## Authentication

| Option | When | Notes |
|---|---|---|
| Event bearer tokens (one per participant or team) | Event week | Issued by organizer; sent as `Authorization: Bearer ...` via `claude mcp add --header`; revoked after the event |
| OAuth 2.1 per the MCP authorization specification | Long-term public service | Requires an identity provider; more setup |
| No auth, IP allow-list | Venue-only network | Only for servers with no external calls and no costs |

Server code never sees deployment secrets. If a contribution needs its own upstream credential (e.g. an API key), it is injected at runtime by the platform's secret store, scoped to that container only, and never baked into images or available to CI.

## Resource limits

| Limit | Starting value |
|---|---|
| CPU / memory per container | 0.5 vCPU / 512 MB |
| Request body size | 1 MB |
| Tool execution timeout | 60 s |
| Rate limit | 60 requests/min per token |
| Concurrent requests per container | 8 |
| Outbound network | denied by default; allow-list per contribution (e.g. `cmr.earthdata.nasa.gov`) |
| Disk | read-only root FS; `/tmp` tmpfs 64 MB |

## Isolation between contributions

- Separate container, process, user and filesystem per contribution; no shared volumes.
- Images built in CI from the frozen reference, without network access to deployment secrets; scanned for secrets (same patterns as [validate_repo.py](../scripts/validate_repo.py)).
- No container can reach another container directly; only the gateway can.
- Contribution code is untrusted: review before deployment, least privilege, no host mounts.

## Health checks and logging

- Liveness: process up. Readiness: an MCP `tools/list` succeeds within 5 s.
- Gateway access logs: time, server id, token id (not the token), method, tool name, status, duration. No request bodies by default (may contain user data).
- Server logs to stderr, collected per container; retention 30 days (TBD by organizer policy).
- Alert when a server fails readiness for 5 minutes; mark catalog `hosting.status` accordingly after verification.

## Delivery of generated artifacts

A tool running on the shared server must not return a server-local path such as `/srv/out/plot.png` as if the participant could open it – that path exists only on the server.

| Output | Delivery |
|---|---|
| Small numbers, tables, ids | Directly in the structured tool result (preferred) |
| Small images (< 1 MB) | MCP image content in the result |
| Larger files | Upload to object storage and return a time-limited HTTPS download URL plus checksum, size and expiry |
| Very large data | Return the query/recipe (e.g. `earthaccess` search parameters) for the user to run, not the data |

For stdio servers on a laptop, writing to a local path is acceptable because client and server share the filesystem; document it in the tool description.

## Client reachability

- Claude Code on a laptop can reach the shared server if the laptop can reach its URL (venue network or internet).
- Claude web remote connectors connect from Anthropic's infrastructure: the endpoint must be publicly reachable over HTTPS with a valid certificate. A venue-only or `127.0.0.1` endpoint will not work there.
- Hosting a server does not install any skill; participants still install skills locally with `install_skills.py`.

## Promotion procedure (when enabled)

1. Contribution has `status.review: accepted` and at least one peer test with result `pass` or `partial`.
2. Organizer triggers a manual build of the frozen reference; image digest recorded.
3. Deploy to staging; run its documented example over HTTP with a plain client; record evidence.
4. Promote; set catalog `status.hosting: {status: hosted, endpoint: https://...}` with the date and evidence.
5. Removing or failing a server sets `hosting.status` back to `not-hosted`. Review and peer-test status are unaffected.

## Open items (organizer)

Host/provider, domain and TLS, authentication choice, data-protection policy for logs, budget, who operates it and for how long – all **TBD**.
