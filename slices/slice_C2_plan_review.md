# Slice C-2 — Adversarial plan-review loop

**Depends on:** C-1 (`exp/img-toolcards-adv-plan`)
**Bundled?** no
**Estimated effort:** 4–6 hours
**Target branch:** `exp/img-toolcards-adv-plan`
**Worktree path:** `/home/david/Projects/octotools-img-toolcards-adv-plan`

## Required reading (in order)

1. `docs/superpowers/specs/2026-05-17-imagegen-toolcards-design.md` — defines the Branch C plan-review phase and two-round limit.
2. `plan.md` §§3–8 — names solver insertion points, operator output, and open questions.
3. `Gotchas.md` — GOTCHA-01 is mandatory because the benchmark path uses `tasks/solve.py`.
4. `resources.md` — OpenAI `gpt-4o-mini`, `/imagegen`, and hephaestus2 runner references.
5. `slices/README.md` — confirms C-2 follows C-1 on `exp/img-toolcards-adv-plan`.
6. `octotools/solver.py` — package solver insertion point after `analyze_query` and before the main loop.
7. `tasks/solve.py` — benchmark solver path used by the required smoke command; see GOTCHA-01.
8. `octotools/models/planner.py` — add `generate_structured_plan` without refactoring unrelated planner methods.
9. `octotools/integrations/imagegen_runner.py` and `octotools/integrations/hephaestus2_runner.py` — wrappers produced by C-1.

## Role-split policy (HARD)

This slice MUST be implemented by hephaestus2 (gpt-5.5 high Codex). The orchestrator may dispatch and verify, but must not author the plan-review source code.

## Goal

Insert a `plan_review_loop(max_rounds=2)` phase between `analyze_query` and the main step loop. The loop emits a structured plan, renders one combined diagram with `/imagegen` (left-to-right flow + decision tree + dependency DAG), calls hephaestus2 for adversarial critique, revises and retries on non-empty critique up to two rounds, and stores the finalized plan-review record in `memory` and output JSON before normal octotools step execution continues.

## Files to create or modify

```text
/home/david/Projects/octotools-img-toolcards-adv-plan/
├── octotools/models/plan_review.py      # NEW — loop orchestration, diagram prompt, result schema
├── octotools/models/planner.py          # MODIFY — add generate_structured_plan(...)
├── octotools/solver.py                  # MODIFY — insert package-level plan-review phase
└── tasks/solve.py                       # MODIFY IF REQUIRED — benchmark smoke path must expose plan_review; see GOTCHA-01
```

Keep the touched set to four files or fewer unless a new GOTCHA proves a fifth file is necessary.

## Public interface

```python
def plan_review_loop(
    planner,
    question: str,
    image_path: str | None,
    query_analysis: str,
    memory,
    max_rounds: int = 2,
) -> dict:
    """Return a JSON-serializable plan_review record and store the final plan in memory."""
```

```python
class Planner:
    def generate_structured_plan(self, question: str, image: str | None, query_analysis: str, memory=None) -> list[tuple[str, str, list[str]]]:
        """Emit ordered (tool, sub_goal, depends_on) triples for plan review."""
```

## CLI contract

No new CLI surface. Existing benchmark invocation must keep working:

```bash
python tasks/solve.py --index 100 --task mathvista --data_file mathvista/data/data.json --llm_engine_name gpt-4o-mini --root_cache_dir mathvista/cache --output_json_dir mathvista/results/_smoke_c2 --output_types direct --enabled_tools "Relevant_Patch_Zoomer_Tool,Google_Search_Tool,Python_Code_Generator_Tool,Image_Captioner_Tool,Generalist_Solution_Generator_Tool" --max_time 600
```

## Constraints from Gotchas

- **GOTCHA-01** — The required smoke command uses `tasks/solve.py`; C-2 must make `plan_review` visible in that output JSON, not just in `octotools/solver.py`.
- **GOTCHA-02** — C inherits B's tool-card inventory; do not change cards in this slice.
- **GOTCHA-03** — C-2 smoke is a single-query gate and does not prove the full 90-query grid.

## Idempotency / overwrite policy

1. Runtime diagrams must be written under `/tmp/octotools-plan-diagrams/` or a similarly explicit temp directory, with unique filenames per query/round.
2. Re-running the smoke may overwrite `mathvista/results/_smoke_c2/output_100.json` because the output directory is a smoke-test target.
3. Do not mutate committed PNG tool cards in C-2.

## Failure behavior

Stable exit codes:

- `0` — smoke writes `direct_output`, records at least one `plan_review` round, and creates a non-empty diagram PNG.
- `10` — diff touches unexpected files or too many files.
- `20` — `plan_review` missing/empty in output JSON.
- `30` — no `[plan_review] round=N` marker or no diagram file evidence.

## Verification gate (MANDATORY)

The implementing agent must run this exact block and paste literal stdout in the final report:

```bash
set -euo pipefail
cd /home/david/Projects/octotools-img-toolcards-adv-plan
git diff --stat
python tasks/solve.py --index 100 --task mathvista --data_file mathvista/data/data.json --llm_engine_name gpt-4o-mini --root_cache_dir mathvista/cache --output_json_dir mathvista/results/_smoke_c2 --output_types direct --enabled_tools "Relevant_Patch_Zoomer_Tool,Google_Search_Tool,Python_Code_Generator_Tool,Image_Captioner_Tool,Generalist_Solution_Generator_Tool" --max_time 600 | tee /tmp/octotools-c2-smoke.stdout
python - <<'PY'
import json, glob, os
p='mathvista/results/_smoke_c2/output_100.json'
data=json.load(open(p))
assert data.get('direct_output'), data
pr=data.get('plan_review')
assert pr and pr.get('rounds'), pr
print(f'output: {p}')
print(f"contents: direct_output_len={len(data['direct_output'])}, plan_review_rounds={len(pr['rounds'])}")
paths=[x for x in glob.glob('/tmp/octotools-plan-diagrams/*.png') if os.path.getsize(x) > 0]
assert paths, 'no non-empty plan diagram png found'
for x in sorted(paths)[-3:]:
    print(f'contents: diagram={x}, bytes={os.path.getsize(x)}')
PY
grep -E "\[plan_review\] round=[0-9]+" /tmp/octotools-c2-smoke.stdout
```

Required pasted-stdout markers:

- `output: mathvista/results/_smoke_c2/output_100.json`
- `contents: direct_output_len=..., plan_review_rounds=...`
- at least one `contents: diagram=/tmp/octotools-plan-diagrams/...` line
- at least one `[plan_review] round=N` line

## On gate pass

Commit and push:

```bash
git add octotools/models/plan_review.py octotools/models/planner.py octotools/solver.py tasks/solve.py
git commit -m "feat: add adversarial plan review" -m "Co-authored-by: David <david@Kijko.nl>"
git push origin exp/img-toolcards-adv-plan
```

## Final report contract

```yaml
branch: exp/img-toolcards-adv-plan
worktree: /home/david/Projects/octotools-img-toolcards-adv-plan
head_commit: <SHA>
pushed_remote: origin/exp/img-toolcards-adv-plan
files_changed:
  - octotools/models/plan_review.py
  - octotools/models/planner.py
  - octotools/solver.py
  - tasks/solve.py
gate_output: |
  ---
  <literal verification gate stdout>
  ---
new_GOTCHAs:
  - <GOTCHA-NN or none>
open_questions:
  - <architectural concern or none>
```
