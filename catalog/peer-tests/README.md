# Peer-test reports

Save one report per artifact per reviewer per round, named `<artifact-id>--<reviewer-team>--<round>.md`, using [templates/peer-test-report.md](../../templates/peer-test-report.md). Then add it to the artifact's catalog entry:

```yaml
status:
  peer_testing:
    - {report: catalog/peer-tests/obs-model-starter--team-b--1.md, result: pass}
```

Procedure: [docs/peer-testing.md](../../docs/peer-testing.md). No reports exist yet: the starter has not been independently peer-tested by a non-author.
