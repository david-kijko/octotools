# octotools ↔ GitHub REST/Actions API — Parity Matrix

<!-- Replace octotools with the target project or skill name. -->
<!-- Replace GitHub REST/Actions API with the canonical runtime being ported. -->
<!-- Keep the ↔ separator so parity reports have a stable title shape. -->

**Date:** 2026-05-17
**Native surface source:** `https://github.com/obra/superpowers/issues/87`
**octotools status checked against:** `plan.md` + slice manifest at
`slices/README.md` + open probes in `Gotchas.md`

<!-- Native surface source: cite first-party docs, source files, or the
     authoritative local corpus used to enumerate native capabilities. -->
<!-- octotools status checked against: cite the local artifacts this matrix
     reads, especially plan.md, slices/README.md, and Gotchas.md. -->

Goal: enumerate every operator-facing capability of the native runtime,
then list the `octotools` CLI + MCP + skill mechanism that delivers
equivalent behaviour. Where there is a gap, name it explicitly so the
parity audit (Phase 2) can either close it or surface the missing
capability as a known limitation.

<!-- Goal: state what the matrix is for, not the project's marketing pitch.
     The populated matrix should make omitted native surfaces explicit. -->

**Status legend:**

- **✓ Covered** — `octotools` has a CLI verb + MCP tool that produces the
  same user-observable outcome as the native operation. Verifiable.
- **◐ Partial** — `octotools` covers the read side or one direction but
  not all semantics (e.g. lists but can't reorder).
- **✗ Gap** — No `octotools` equivalent. May or may not be addressable;
  GOTCHA-NN cross-referenced when applicable.
- **⊘ N/A (native-only)** — The capability is inherently a TUI / GUI
  rendering detail that doesn't translate to a headless / programmatic
  surface. `octotools` renders the **data** behind it instead.

<!-- If the project distinguishes gap subtypes, spell them out as separate
     legend bullets, for example "✗ Gap (intentional)" and "✗ Gap (open)".
     Do not flatten project-specific subtypes back to a generic gap. -->

---

## 1. Bootstrap seed surface

<!-- Number sections by operator-facing surface area. Keep a final
     "## N. Beyond-parity (octotools-only)" section when the project has
     capabilities the native runtime does not. -->

| # | Native capability | Native invocation | `octotools` equivalent | Status | Verification |
|---|---|---|---|---|---|
| 1.1 | Define first vertical from primary-source evidence | https://github.com/obra/superpowers/issues/87 | slice_01_define-first-vertical.md (placeholder) | ⊘ | Phase 1 writes the concrete slice and pastes its gate output |

<!-- Column meanings:
     # = stable row id within this section.
     Native capability = user-visible native operation.
     Native invocation = command, key, API, or automatic native trigger.
     octotools equivalent = concrete project mechanism or explicit dash.
     Status = one legend symbol/subtype only.
     Verification = concrete command, test gate, probe, or GOTCHA-NN ref. -->

<!-- Bootstrap (Phase 0) emits this empty table.
     Parity audit (Phase 2) fills it in by scraping the native docs
     surface and grepping the octotools CLI + MCP tool list. -->
