# octotools Image-Toolcards Experiment — Implementation Slices

Three testable slices tailor octotools for the image-toolcards experiment. Each slice is a self-contained brief for a hephaestus2 (gpt-5.5 high Codex) implementer. Read this manifest once, then execute `slice_B1_image_toolcards.md`, `slice_C1_runtime_wrappers.md`, and `slice_C2_plan_review.md` in graph order.

## Required reading (the harness — every slice agent reads these)

1. **`docs/superpowers/specs/2026-05-17-imagegen-toolcards-design.md`** — hypothesis, branch design, benchmark grid, non-goals.
2. **`plan.md`** — architecture hooks, operator surface, and open questions.
3. **`Gotchas.md`** — empirical contradictions; every slice must respect current GOTCHA entries.
4. **`resources.md`** — verified primary URLs and local runner contracts.
5. **`docs/octotools-architecture.png`** — generated architecture visual; do not regenerate.
6. **`docs/octotools-implementation-path.png`** — generated dependency-path visual; do not regenerate.
7. **`docs/parity-matrix.md`** — branch/benchmark parity surface.

Each slice file adds slice-specific code references and verification gates on top.

## Dependency graph

```text
research/imagegen-toolcards
          |
          v
[B-1 image tool cards]  ->  [C-1 runtime wrappers]  ->  [C-2 plan review]
 exp/img-toolcards          exp/img-toolcards-adv-plan   exp/img-toolcards-adv-plan
```

B-1 forks from `research/imagegen-toolcards`. C-1 forks from `exp/img-toolcards` after B-1 passes. C-2 continues on `exp/img-toolcards-adv-plan` after C-1 passes.

## Bundling

None bundled. B-1, C-1, and C-2 each has an independent verification gate with literal stdout requirements. Do not combine C-1 and C-2: the runner wrappers must prove real `/imagegen` and hephaestus2 behavior before the solver consumes them.

## How to execute a slice

```bash
set -euo pipefail
cd /home/david/Projects/octotools
for slice in B1 C1 C2; do
  brief="slices/slice_${slice}_*.md"
  tmp="$(mktemp "/tmp/octotools-${slice}.XXXXXX.md")"
  cat $brief > "$tmp"
  COMPLETION_GUARD_TASK_TYPE=gap_analysis \
  HEPHAESTUS_MODEL=gpt-5.5 \
  HEPHAESTUS_REASONING_EFFORT=high \
  hephaestus --file "$tmp" --dir "$(pwd)" --dangerous
  # Then run the slice's own Verification gate exactly as written in the brief.
done
```

The orchestrator only advances after the slice gate passes and the branch is committed and pushed. For B-1 and C-2, benchmark smoke tests must inspect the actual `output_100.json` user-visible artifact. For C-1, the wrappers must create/read real runner outputs.

## Update protocol (every slice agent follows this)

Implementation must be authored by hephaestus2 (gpt-5.5 high Codex), not by the orchestrator. The orchestrator may draft briefs, dispatch lanes, monitor outputs, run verification, and merge reviewed work; it must not author source code or generated cards outside S00 harness documentation.

If execution discovers a fact that invalidates the harness:

1. Stop before claiming the slice complete.
2. Append a new `GOTCHA-NN` entry to `Gotchas.md`, newest first.
3. Update `plan.md`, `resources.md`, `docs/parity-matrix.md`, or the relevant slice brief only where the gotcha affects that artifact.
4. Do not regenerate `docs/octotools-architecture.png` or `docs/octotools-implementation-path.png` unless a future orchestrator explicitly requests diagram replacement.
5. Commit harness corrections before implementation corrections on the slice branch.
6. Mention every new Gotcha in the final report.

## Slice manifest

| # | File | Title | Depends on | Bundled? | Target branch/worktree | Verification gate |
|---|---|---|---|---|---|---|
| B-1 | `slice_B1_image_toolcards.md` | Image tool cards and planner/executor wiring | — | no | `exp/img-toolcards` at `/home/david/Projects/octotools-img-toolcards` | Diff stat, PNG card validity, MathVista index 100 smoke, multimodal attachment stdout |
| C-1 | `slice_C1_runtime_wrappers.md` | Runtime `/imagegen` and hephaestus2 subprocess wrappers | B-1 | no | `exp/img-toolcards-adv-plan` at `/home/david/Projects/octotools-img-toolcards-adv-plan` | Real PNG output from `imagegen_runner`; non-empty critique from `hephaestus2_runner` |
| C-2 | `slice_C2_plan_review.md` | Plan-review loop before solver step execution | C-1 | no | `exp/img-toolcards-adv-plan` at `/home/david/Projects/octotools-img-toolcards-adv-plan` | Diff stat, MathVista index 100 smoke with `plan_review`, stdout round marker, diagram file evidence |

## Acceptance

After C-2 passes, the implementation harness is ready for the 90-query A/B/C experiment and `verdict.md` generation. Any limitation that prevents apples-to-apples comparison must be documented in `Gotchas.md` and reflected in `docs/parity-matrix.md` before running the final grid.

## Branch convention

- S00 harness work lands on `research/imagegen-toolcards`.
- B-1 lands on `exp/img-toolcards` and pushes `origin/exp/img-toolcards`.
- C-1 and C-2 land on `exp/img-toolcards-adv-plan` and push `origin/exp/img-toolcards-adv-plan`.
- No implementation work lands directly on `main`.

## Implementation path diagram

See [`docs/octotools-implementation-path.png`](../docs/octotools-implementation-path.png) for the generated visual rendering of the B-1 → C-1 → C-2 path.
