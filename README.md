# AgentRadar

Minimal scanner for public Python projects that use LangGraph.

It treats two fields as authoritative:

- `langgraph_status=confirmed` means Python source imports `langgraph`.
- `github_stars` comes directly from the GitHub repository API.

Everything else is a conservative static-analysis attempt. Unknown or dynamic values stay unknown.

## Run

GitHub CLI authentication or `GITHUB_TOKEN` is recommended.

```bash
python3 agentradar.py scan --limit 20
```

Outputs:

```text
data/catalog.json
data/catalog.csv
data/provider_candidates.json
data/scan_cache.json
data/repositories_seen.json
```

Static counts are confirmed lower bounds, not claims about runtime totals. The scan cache
reuses analysis when a repository's `pushed_at` value is unchanged; stars still refresh.
`repositories_seen.json` keeps every discovered candidate, including filtered and failed scans.
Cache and seen-repository state are checkpointed after every candidate, so an interrupted
large scan can resume without losing completed repository analysis.

Prepare ten new or changed projects for a lightweight Codex host review:

```bash
python3 agentradar.py prepare-review --limit 10
```

This writes `data/review_queue.json`. Host-agent judgments live separately in
`data/agent_reviews.json` and never replace LangGraph or GitHub Star facts.

Use a custom repository search when needed:

```bash
python3 agentradar.py scan \
  --query 'langgraph agent in:readme language:Python archived:false fork:false' \
  --limit 50
```

## Test

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q agentradar.py tests
```

The scanner downloads repository tarballs but never extracts them to disk, imports target code, installs target dependencies, or runs target commands.
