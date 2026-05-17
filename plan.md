# octotools — Architecture-as-text

**Status:** planning — Phase 0 bootstrap draft; implementation has not started
**Date:** 2026-05-17
**Template:** materialized from Simplement `templates/plan.md`
**Target runtime:** GitHub REST/Actions API wrapped by Simplement's daemon-free Claude orchestrator + hephaestus2 workflow

All URLs referenced below appear in [`resources.md`](./resources.md).
All operator-facing parity claims appear in [`docs/parity-matrix.md`](./docs/parity-matrix.md).
Architecture visuals live at [`docs/octotools-architecture.png`](./docs/octotools-architecture.png) and [`docs/octotools-implementation-path.png`](./docs/octotools-implementation-path.png).
The slice dependency manifest is [`slices/README.md`](./slices/README.md).

> **Shape note.** This plan is target-specific seed content derived from the bootstrap goal and first-party URLs. Later slices must replace conservative placeholders with implementation evidence.

---

## 1. Why octotools exists

Goal: Run early-sample 90-query benchmark (3 branches x 3 tasks x 10 indices) comparing vanilla octotools vs image-tool-cards (replace text toolbox_metadata with /imagegen PNGs) vs image-cards-plus-adversarial-plan-review (planner emits plan, /imagegen renders combined flow+tree+DAG diagram, hephaestus2 critiques up to 2 rounds, then execute). Per docs/superpowers/specs/2026-05-17-imagegen-toolcards-design.md. Done = verdict.md with per-branch accuracy/avg_steps/tokens/wall-clock/cost deltas vs control, plus escalate-or-kill decision against the 3pp-on-2-tasks gate.

Simplement bootstraps this target so a future hephaestus2 slice can build the first vertical against GitHub REST/Actions API with documented URLs, explicit Gotchas, parity rows, and a deterministic verification gate. The initial evidence set points at `github.com` and related upstream hosts rather than third-party tutorials, so implementers start from primary-source behavior.

---

## 2. Issues to address

- Convert the bootstrap goal into a narrow first vertical before authoring implementation files.
- Preserve first-party evidence in `resources.md`; do not cite dropped blogs, forums, or SEO mirrors.
- Keep all Phase 1 implementation on short-lived `slice/<NN>-<shortname>` branches with literal verification output.
- Treat any undocumented limit, permission, pagination, or auth surprise as a Gotcha before continuing.

---

## 3. Important notes

### `.octotools/events.ndjson` is the state-transition log

Future slice execution should use a local append-only event stream or an equivalent file-backed log. Phase 0 does not create that state directory; it records the expected shape for later slices.

### Capturing the worker/session identity

Each future slice should bind the slice id, branch, worker output path, event stream id, and verification transcript in one run record so a reviewer can replay the work.

### Session states

| State | Trigger | Evidence |
|---|---|---|
| Planned | Phase 0 harness exists | these seven harness files |
| Working | hephaestus2 starts a slice | event stream + branch |
| Verified | verification gate exits 0 | pasted stdout |
| Blocked | new L5 Gotcha changes the plan | Gotchas.md + blocked note |

### Monitor and fallback notification path

Use the Simplement monitor shape when a later slice adds execution: `tail -F .simplement/events.ndjson | grep --line-buffered -E '\[simplement\]'`. If Monitor is unavailable, poll the event file and verification log directly.

### Event-stream contract

No event stream is written in Phase 0. Later slices should emit bracketed, grep-friendly lines plus JSON payloads, matching the Simplement bridge contract.

### Path, permission, and auth boundaries

Bootstrap validated a clean git work tree and local research branch before writing files. Live Exa requires `EXA_API_KEY`; fixture mode bypasses network credentials for deterministic tests.

### What octotools does NOT do

- Does not create implementation source files during Phase 0.
- Does not create `slice_01_define-first-vertical.md`; only the placeholder manifest row exists.
- Does not push, merge, or overwrite existing harness files.

Primary-source seed URLs:

- `https://github.com/obra/superpowers/issues/87` — Optimize plan generation: Modular task files + orchestrator for 90%+ token reduction in subagent-driven   development · Issue #87 · obra/superpowers
- `https://github.com/cmudrc/design-research-agents/issues/17` — Image output (text → image) tool interface + artifact attachments · Issue #17 · cmudrc/design-research-agents
- `https://github.com/mainahq/maina/commit/fb97edd43e959f326dc31c560aaa28db4bb7b36b` — docs: add Sprint 10 benchmark — Claude+Superpowers vs Claude+Maina · fb97edd · mainahq/maina
- `https://github.com/openclaw/openclaw/issues/77386` — image_generate via OpenAI Codex OAuth hits hardcoded 30s dynamic tool watchdog and loses result · Issue #77386 · openclaw/openclaw
- `https://github.com/openclaw/openclaw/commit/4c569ce` — docs(tokens): document image dimension token tradeoffs · 4c569ce · openclaw/openclaw
- `https://github.com/obra/superpowers/issues/1152` — Codex: Implementation of relatively simple plan with subagent-driven development consumes full 5h token budget in a single run (PLUS plan) · Issue #1152 · obra/superpowers

---

## 4. Architecture

The target starts with a file-backed harness: `plan.md`, `Gotchas.md`, `resources.md`, `slices/README.md`, `docs/parity-matrix.md`, and two PNG diagrams. A future Simplement orchestrator reads those files, dispatches hephaestus2 for concrete slices, and updates Gotchas/resources before retrying whenever evidence contradicts assumptions.

### Modules

- `plan.md` — target architecture and seed implementation strategy.
- `Gotchas.md` — evidence-backed surprises; initially empty unless primary evidence justified an entry.
- `resources.md` — primary-source URLs discovered by Exa or fixtures.
- `slices/README.md` — placeholder manifest for the first vertical slice.
- `docs/parity-matrix.md` — operator-facing parity rows to fill during Phase 2.

### Persistent state

There is no database in the Phase 0 harness. Persistent state is the git-tracked markdown/PNG harness plus future `.simplement/` run artifacts created by later slices.

### Operator surface

| Surface | Outcome | Phase |
|---|---|---|
| `python scripts/simplement_bootstrap.py --target ...` | creates the seven-file harness | Phase 0 |
| `slices/README.md` | tells the orchestrator which slice to author next | Phase 1 seed |
| `docs/parity-matrix.md` | records parity expectations | Phase 2 seed |

### Orchestrator-facing surface

The orchestrator consumes this harness, writes one concrete slice file from the placeholder row, and requires literal verification stdout before accepting a slice.

### Template/materialization surface

| Target file | Source |
|---|---|
| `plan.md` | `templates/plan.md` |
| `Gotchas.md` | `templates/Gotchas.md` |
| `resources.md` | `templates/resources.md` |
| `slices/README.md` | `templates/slices_README.md` |
| `docs/parity-matrix.md` | `templates/parity-matrix.md` |
| `docs/octotools-architecture.png` | imagegen subprocess or placeholder fallback |
| `docs/octotools-implementation-path.png` | imagegen subprocess or placeholder fallback |

---

## 5. Implementation strategy

1. Define `slice_01_define-first-vertical.md` from the goal and primary URLs; gate: the slice brief names a single user-visible behavior.
2. Implement the smallest client/runtime vertical; gate: a live or fixture-backed command exercises the behavior.
3. Add error, auth, pagination, and rate-limit handling only when primary-source evidence or tests require it.
4. Update `docs/parity-matrix.md` after each operator-facing capability lands.

Minimum viable vertical: one command or API call that demonstrates `Run early-sample 90-query benchmark (3 branches x 3 tasks x 10 indices) comparing vanilla octotools vs image-tool-cards (replace text toolbox_metadata with /imagegen PNGs) vs image-cards-plus-adversarial-plan-review (planner emits plan, /imagegen renders combined flow+tree+DAG diagram, hephaestus2 critiques up to 2 rounds, then execute). Per docs/superpowers/specs/2026-05-17-imagegen-toolcards-design.md. Done = verdict.md with per-branch accuracy/avg_steps/tokens/wall-clock/cost deltas vs control, plus escalate-or-kill decision against the 3pp-on-2-tasks gate.` with deterministic verification.

---

## 6. Tests

- Unit tests for URL/auth/request construction at the boundary named by the first vertical.
- Fixture-backed integration tests for rate-limit, permission, pagination, and failure responses documented in `resources.md`.
- One user-visible smoke command whose stdout can be pasted into the slice report.

---

## 7. Open questions — see [Gotchas.md](Gotchas.md)

1. Which exact first vertical should `slice_01_define-first-vertical.md` implement? Bootstrap only knows the goal, not the operator's preferred API surface.
2. Which primary-source limits or permissions require Gotcha entries? The initial bootstrap found no contradiction unless `Gotchas.md` contains entries.
3. Which parity rows are native-only versus required for v1? Phase 2 must decide from first-party docs and implemented CLI/API surfaces.
