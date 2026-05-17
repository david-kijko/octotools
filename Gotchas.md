# octotools — Gotchas

Living list of things that **were not what we expected** when building
`octotools`. Sourced from empirical probes, docs that turned out to be
stale, and surprises in production. Bootstrap (Phase 0) materializes
this file from the canonical template at `templates/Gotchas.md`.

**Append rule for future findings:** new entries go at the **top** of
`## Findings` (newest first), with the template below filled in. Don't
edit historical entries except to add a "Resolved" note when an upstream
change fixes the gotcha.

---

## Entry template

```markdown
### GOTCHA-NN — <one-line headline>

- **Date:** 2026-05-17
- **Discovered via:** empirical probe | doc read | production incident | …
- **Source:** path/to/probe-or-spec.md | URL | session-id | …
- **Symptom:** what looked broken or surprising
- **Root cause:** what's actually happening
- **Workaround / fix:** what to do until/unless upstream changes
- **Affects:** plan.md §X, src/<project>/Y.py, plugin/hooks/hooks.json, …
- **Severity:** L1 trivial | L2 light | L3 medium | L4 heavy | L5 blocking
- **Resolved:** (only when fixed upstream — note the version/commit)
```

---

## Findings

<!-- Bootstrap found no evidence-backed Gotchas from the initial primary-source set. -->
