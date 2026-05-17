# octotools Image-Toolcards Experiment — Parity Matrix

**Date:** 2026-05-18
**Native surface source:** `docs/superpowers/specs/2026-05-17-imagegen-toolcards-design.md`
**octotools status checked against:** `plan.md`, `slices/README.md`, `Gotchas.md`, and the three slice briefs.

Goal: enumerate the operator-visible experiment surfaces that must remain comparable across A/control, B/image tool cards, and C/image cards plus adversarial plan review. This is not GitHub Actions or REST API parity; it is branch and benchmark parity for the MathVista, MedQA, and GAIA-Text experiment using `gpt-4o-mini-2024-07-18`.

**Status legend:**

- **✓ Covered** — The harness or slice gate names a concrete user-visible verification command.
- **◐ Partial** — The surface is specified but has a known gotcha or future-slice dependency.
- **✗ Gap** — The surface is required but currently lacks a concrete implementation or gate.
- **⊘ N/A** — Not part of this experiment.

---

## 1. Branch and benchmark parity

| # | Capability | Control A | Branch B | Branch C | Status | Verification |
|---|---|---|---|---|---|---|
| 1.1 | Branch separation | `main` | `exp/img-toolcards` | `exp/img-toolcards-adv-plan` forked from B | ✓ Covered | `slices/README.md` branch/worktree rows |
| 1.2 | Benchmark task surface | MathVista, MedQA, GAIA-Text | Same tasks | Same tasks | ◐ Partial | GOTCHA-03: scripts need the spec's 10-index grid |
| 1.3 | Planner/scorer model pin | `gpt-4o-mini-2024-07-18` per spec | Same | Same plus hephaestus2 critique runner | ◐ Partial | `resources.md` OpenAI model/pricing links; implementation must pin aliases/snapshots |
| 1.4 | Output type | `direct` only | `direct` only | `direct` only plus `plan_review` evidence | ✓ Covered | Slice B-1 and C-2 smoke commands inspect `direct_output` |

## 2. Tool metadata parity

| # | Capability | Control A | Branch B | Branch C | Status | Verification |
|---|---|---|---|---|---|---|
| 2.1 | Planner query analysis metadata | Text `toolbox_metadata` | PNG card attachments | PNG card attachments | ✓ Covered | B-1 gate checks verbose multimodal attachments |
| 2.2 | Planner next-step metadata | Text `toolbox_metadata` | PNG card attachments via multimodal engine | Same | ✓ Covered | B-1 gate checks `generate_next_step` attachment evidence |
| 2.3 | Planner verification metadata | Text `toolbox_metadata` | PNG card attachments via multimodal engine | Same | ✓ Covered | B-1 gate checks `verificate_context` attachment evidence |
| 2.4 | Executor selected-tool metadata | Text metadata dict | Single selected tool card | Single selected tool card | ◐ Partial | B-1 gate includes executor diff; implementer must prove command generation still works |
| 2.5 | Tool-card inventory | None | One PNG per enabled-tool union | Same | ◐ Partial | GOTCHA-02: actual union is eight tools, not five |

## 3. Plan-review parity

| # | Capability | Control A | Branch B | Branch C | Status | Verification |
|---|---|---|---|---|---|---|
| 3.1 | Structured pre-plan | None | None | `Planner.generate_structured_plan(...)` | ✓ Covered | C-2 gate requires `plan_review` JSON field |
| 3.2 | Diagram generation | None | Offline static cards only | Runtime `/imagegen` diagram per query | ✓ Covered | C-1 runner smoke and C-2 diagram file check |
| 3.3 | Adversarial critique | None | None | `hephaestus2_runner.critique(...)` | ✓ Covered | C-1 critique smoke and C-2 stdout round marker |
| 3.4 | Benchmark visibility | No plan review | No plan review | Plan review before step loop | ◐ Partial | GOTCHA-01: must affect `tasks/solve.py` benchmark path |

## 4. Verdict parity

| # | Capability | Required evidence | Status | Verification |
|---|---|---|---|---|
| 4.1 | Metrics grid | accuracy, avg steps, LLM calls, tokens, wall-clock, cost, tool usage | ✗ Gap | Future verdict runner writes `verdict.md` |
| 4.2 | Escalation decision | ≥3pp accuracy delta on at least two tasks for B or C | ✗ Gap | Future `verdict.md` records escalate / close / iterate |
