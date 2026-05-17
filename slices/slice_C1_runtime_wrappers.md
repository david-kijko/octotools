# Slice C-1 — Runtime /imagegen and hephaestus2 wrappers

**Depends on:** B-1 (`exp/img-toolcards`)
**Bundled?** no
**Estimated effort:** 2–3 hours
**Target branch:** `exp/img-toolcards-adv-plan`
**Worktree path:** `/home/david/Projects/octotools-img-toolcards-adv-plan`

## Required reading (in order)

1. `docs/superpowers/specs/2026-05-17-imagegen-toolcards-design.md` — Branch C runtime integration requires true subprocess runners, not mocks.
2. `plan.md` §§3–6 — explains C's plan-review architecture and why C forks from B.
3. `Gotchas.md` — current gotchas do not block wrapper creation, but C-2 depends on them.
4. `resources.md` — local `/imagegen` skill and Simplement template references define the brief-file contract.
5. `slices/README.md` — confirms C-1 depends on B-1 and must pass before C-2.
6. `/home/david/.claude/skills/imagegen/SKILL.md` — exact hephaestus invocation and required `output:` / `contents:` evidence.

## Role-split policy (HARD)

This slice MUST be implemented by hephaestus2 (gpt-5.5 high Codex). The orchestrator may dispatch and verify, but must not author the wrapper code.

## Goal

Add thin Python wrappers around the existing `hephaestus` CLI: one for `/imagegen` image creation and one for hephaestus2 adversarial critique. Both wrappers spawn subprocesses, write brief files to temp paths, and read results from disk or stdout. They must use the same contract as patched `simplement_bootstrap.py`: `hephaestus --file <brief> --dangerous`, with output paths inside the brief.

## Files to create or modify

```text
/home/david/Projects/octotools-img-toolcards-adv-plan/
└── octotools/
    └── integrations/
        ├── __init__.py                 # NEW — integration package marker
        ├── imagegen_runner.py          # NEW — generate_image(prompt, output_path) wrapper
        └── hephaestus2_runner.py       # NEW — critique(plan_text, diagram_path) wrapper
```

No existing octotools files should be modified in C-1; C-2 consumes these wrappers.

## Public interface

```python
def generate_image(prompt: str, output_path: str) -> str:
    """Generate an image through hephaestus + /imagegen and return output_path."""


def critique(plan_text: str, diagram_path: str | None) -> str:
    """Run hephaestus2 adversarial review and return critique text from stdout or result file."""
```

The critique wrapper must set `HEPHAESTUS_MODEL=gpt-5.5` and `HEPHAESTUS_REASONING_EFFORT=high` in the subprocess environment.

## CLI contract

No public CLI surface in this slice. The public surface is the Python import contract above.

## Constraints from Gotchas

- **GOTCHA-01** — Not directly fixed here, but C-2 must wire these wrappers into the benchmark-visible solver path.
- **GOTCHA-02** — Not applicable; cards are already inherited from B.
- **GOTCHA-03** — Not applicable; no benchmark grid runner is added in C-1.

## Idempotency / overwrite policy

1. `generate_image` may overwrite the requested `output_path` only because the caller explicitly names it.
2. Temporary brief files must be unique and may remain in `/tmp` only if needed for debugging; do not write persistent state inside the repo.

## Failure behavior

Stable exit codes are surfaced as Python exceptions:

- `0` subprocess return — wrapper returns output string/path.
- non-zero subprocess return — raise `RuntimeError` containing command, return code, stdout, and stderr.
- missing/too-small image output — raise `RuntimeError` with the expected path and byte count.

## Verification gate (MANDATORY)

The implementing agent must run this exact block and paste literal stdout in the final report:

```bash
set -euo pipefail
cd /home/david/Projects/octotools-img-toolcards-adv-plan
python -c "from octotools.integrations.imagegen_runner import generate_image; p = generate_image('a tiny test sketch of a flowchart with three boxes', '/tmp/c1-smoke.png'); import os; assert os.path.getsize(p) > 10000, f'too small: {os.path.getsize(p)}'; print(f'output: {p}'); print(f'contents: path={p}, bytes={os.path.getsize(p)}')"
python -c "from octotools.integrations.hephaestus2_runner import critique; out = critique('Plan: call Calculator then return.\nDiagram (text): (analyze) -> (calc) -> (answer)', None); assert isinstance(out, str) and len(out) > 0; print(f'critique-len: {len(out)}'); print(out[:200])"
```

Required pasted-stdout markers:

- `output: /tmp/c1-smoke.png`
- `contents: path=/tmp/c1-smoke.png, bytes=...`
- `critique-len: ...`

## On gate pass

Commit and push:

```bash
git add octotools/integrations/__init__.py octotools/integrations/imagegen_runner.py octotools/integrations/hephaestus2_runner.py
git commit -m "feat: add plan-review runner wrappers" -m "Co-authored-by: David <david@Kijko.nl>"
git push origin exp/img-toolcards-adv-plan
```

## Final report contract

```yaml
branch: exp/img-toolcards-adv-plan
worktree: /home/david/Projects/octotools-img-toolcards-adv-plan
head_commit: <SHA>
pushed_remote: origin/exp/img-toolcards-adv-plan
files_changed:
  - octotools/integrations/__init__.py
  - octotools/integrations/imagegen_runner.py
  - octotools/integrations/hephaestus2_runner.py
gate_output: |
  ---
  <literal verification gate stdout>
  ---
new_GOTCHAs:
  - <GOTCHA-NN or none>
open_questions:
  - <architectural concern or none>
```
