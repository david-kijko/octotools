# octotools — Imagegen Tool Cards & Adversarial Plan Review

**Date:** 2026-05-17
**Base commit:** `fddbc9d` (https://github.com/octotools/octotools)
**Execution skill:** `/simplement` (Claude orchestrates, hephaestus2 implements every slice)

---

## Hypothesis

Replacing octotools' text-JSON `toolbox_metadata` with `/imagegen`-rendered tool cards (one PNG per tool) — and optionally adding an adversarial plan-review phase using `/imagegen` + `hephaestus2` — will measurably change end-to-end task accuracy and/or efficiency on MathVista, MedQA, and GAIA-Text. We do not know the sign of the delta. This is an empirical test.

---

## Branches and Worktrees

All three off `fddbc9d`.

| Label | Path | Branch | Change |
|---|---|---|---|
| **A — control** | `/home/david/Projects/octotools` | `main` | none |
| **B — image tool cards** | `/home/david/Projects/octotools-img-toolcards` | `exp/img-toolcards` | replace text `toolbox_metadata` with PNG tool cards |
| **C — img-cards + adversarial plan** | `/home/david/Projects/octotools-img-toolcards-adv-plan` | `exp/img-toolcards-adv-plan` | B + plan diagram + hephaestus2 review loop |

C is forked from B (inherits the tool-card machinery), not from main.

---

## Branch B — Image Tool Cards

### Cards (generated offline, once)
- One PNG per tool, rendered by Claude invoking `/imagegen` via the existing hephaestus runner
- Stored at `octotools/tools/_cards/<Tool_Name>.png`, committed to branch
- Each card depicts: tool name + 1-line purpose, I/O schema (visual boxes), 1–2 worked example flows, limitations callout
- Initial card set covers the union of `ENABLED_TOOLS` across MathVista, MedQA, GAIA-Text run scripts

### Runtime wiring
- New module `octotools/models/toolbox_renderer.py`
  - `get_toolbox_payload(tools, mode="image" | "text")` returns either text JSON or `list[(caption, image_bytes)]`
- `Planner.__init__` accepts `toolbox_mode: Literal["text","image"]` (default `"text"` for back-compat; B sets `"image"`)
- All three planner prompt sites that currently interpolate `{self.toolbox_metadata}` attach images instead when mode is `"image"`:
  - `Planner.analyze_query` (planner.py L52)
  - `Planner.generate_next_step` (planner.py L138)
  - `Planner.verificate_context` (planner.py L212)
- `Executor.generate_tool_command` attaches the single relevant tool's card image
- Text-only engine path (`self.llm_engine`) removed in B — everything routes through `llm_engine_mm`
- Replace, do not augment: text metadata is gone in mode `"image"`

---

## Branch C — Image Cards + Adversarial Plan Review

Inherits all of B. Adds a new phase in `solver.py` between `analyze_query` (L73) and the main step loop (L83):

```
analyze_query
    ↓
[NEW] plan_review_loop  (max 2 rounds)
    ↓
    1. Planner.generate_plan(question, image, query_analysis)
       → structured plan: ordered (tool, sub_goal, depends_on) triples
    2. plan_to_diagram(plan) → calls /imagegen via hephaestus runner subprocess
       → produces ONE PNG combining three views:
           - left-to-right execution flow
           - decision tree (fallback branches)
           - dependency DAG (tool-output dependencies)
    3. adversarial_review(plan_text, diagram_png) → calls hephaestus2
       (gpt-5.5 high via existing runner subprocess)
       → returns critique text (empty = approved)
    4. if critique non-empty AND round < 2: revise plan, goto 2
       else: commit finalized plan to memory, exit loop
    ↓
main step loop  (unchanged from B)
    ↓
direct_output
```

### Runtime integration — TRUE runners
- `/imagegen`: subprocess call to the existing hephaestus runner CLI, same invocation path Claude uses. New module `octotools/integrations/imagegen_runner.py` wraps it.
- `hephaestus2`: subprocess call to the existing hephaestus2 runner CLI. New module `octotools/integrations/hephaestus2_runner.py` wraps it.
- Both are blocking; planner reads result (PNG path / critique text) from runner stdout or designated output path.
- No API substitution. No mocking at integration time.

---

## Benchmark Protocol — Early Sample Only

| Dimension | Value |
|---|---|
| Tasks | `mathvista`, `medqa`, `gaia-text` |
| Indices per task | 10 (indices `100, 110, 120, 130, 140, 150, 160, 170, 180, 190` — same set across branches) |
| Queries per branch | 30 |
| Total queries | 90 |
| Planner LLM | `gpt-4o-mini-2024-07-18` (pinned snapshot) |
| Scorer LLM | `gpt-4o-mini-2024-07-18` (pinned in `calculate_score.py`) |
| Output type | `direct` only |
| `--max_steps` | 10 |
| `--max_time` | 300 |
| Parallelism | `-j 4` (lower than canonical `-j 8` to avoid runner contention in C) |
| Enabled tools | exact `ENABLED_TOOLS` from each task's `run_octotools.sh` |

### Reporting grid

For each `(branch × task)` cell, record:

| Metric | Source |
|---|---|
| accuracy (direct_output) | `final_results_direct_output.json` |
| avg_steps | `step_stats.avg_steps` |
| avg LLM calls / query | derived from per-query JSON |
| avg total tokens / query | `--verbose` logs |
| avg wall-clock / query | execution_time field |
| $ per query | tokens × pinned-model pricing |
| tool_usage distribution | `tool_usage` field |

### Decision gate
- If `max(|Δaccuracy|) ≥ 3pp` on at least 2 tasks for any non-control branch → escalate to Tier-1 (100 indices/task, single seed)
- Otherwise → write verdict report, mark experiment closed

---

## Execution via /simplement (4 phases)

### Phase 1 — Bootstrap
- Create both worktrees (`exp/img-toolcards`, `exp/img-toolcards-adv-plan`)
- Verify `/imagegen` runner reachable; smoke-test by generating 1 card
- Verify `hephaestus2` runner reachable; smoke-test with a trivial prompt
- Generate full tool-card set on branch B and commit
- Confirm `main` (branch A) runs end-to-end on 3 MathVista queries unchanged

### Phase 2 — Slices (hephaestus2 implements each)
- **Slice B-1:** `toolbox_renderer.py` + planner wiring on `exp/img-toolcards`; passes smoke test (3 MathVista queries return direct_output without errors)
- **Slice C-1:** `imagegen_runner.py` + `hephaestus2_runner.py` integration wrappers
- **Slice C-2:** `plan_review` phase wired into `solver.py` on `exp/img-toolcards-adv-plan`; passes smoke test

### Phase 3 — Parity
- Re-run baseline A on 3 fixed MathVista queries; accuracies must match published numbers within 1pp (sanity that the env/model pinning is correct)
- Confirm B and C produce structurally-valid output JSONs

### Phase 4 — Self-host (the actual benchmark)
- Run A on 30 queries (3 tasks × 10) → record metrics
- Run B on 30 queries → record metrics → A↔B comparison
- Run C on 30 queries → record metrics → A↔B↔C comparison
- Write `verdict.md` with the reporting grid and a recommended next action (escalate / kill / iterate on cards)

---

## Cost Ceiling (early-sample only)

| Item | Estimate |
|---|---|
| Tool-card generation (one-time, ~5–8 cards) | $0.50 |
| A: 30 queries × $0.01 | $0.30 |
| B: 30 queries × $0.012 (image tokens added) | $0.36 |
| C: 30 queries + ~60 plan-diagram regenerations + ~60 hephaestus2 critiques | ~$10 |
| **Total** | **~$11** |

Wall-clock budget: roughly **2–4 hours** for the full 90-query grid at `-j 4`, dominated by C's hephaestus2 round-trips.

---

## Risks

1. **gpt-4o-mini vision weakness** — a single combined plan diagram (flow + tree + DAG in one PNG) may exceed what gpt-4o-mini can parse, hurting C disproportionately. Mitigation: if C tanks badly, generate three separate diagrams on a follow-up branch C′.
2. **hephaestus2 latency dominates C's wall-clock** — minutes per critique. 60 critiques serial would be hours; `-j 4` partially hides this but adds runner-process contention.
3. **/imagegen runner contention** — if multiple parallel queries call /imagegen concurrently, the runner may serialize them anyway. Acceptable for early-sample.
4. **Tool-card legibility** — if a tool's behavior (e.g. `Python_Code_Generator_Tool`) is too rich to fit in one image, iterate the imagegen prompt before locking in the card set.
5. **Determinism** — `gpt-image-1` output is non-deterministic per call; same plan → different diagram each time. Acceptable; we're measuring the wrapper, not the pixels.

---

## What this spec is NOT

- Not a full Tier-1 or Tier-2 benchmark. That's a decision-gated follow-up.
- Not a perf-optimization play (no prompt caching, no async tool exec, no verifier merging). Those are separate experiments.
- Not a refactor of octotools. Surgical changes only — touch what the experiment requires.
