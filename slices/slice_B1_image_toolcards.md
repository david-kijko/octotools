# Slice B-1 — Image tool cards and planner/executor wiring

**Depends on:** `research/imagegen-toolcards`
**Bundled?** no
**Estimated effort:** 4–6 hours
**Target branch:** `exp/img-toolcards`
**Worktree path:** `/home/david/Projects/octotools-img-toolcards`

## Required reading (in order)

1. `docs/superpowers/specs/2026-05-17-imagegen-toolcards-design.md` — defines Branch B: replace text `toolbox_metadata` with `/imagegen` PNG tool cards.
2. `plan.md` §§1–3 — explains the hypothesis, branch layout, and exact planner/executor hook sites.
3. `Gotchas.md` — especially GOTCHA-02, because the actual MathVista/MedQA/GAIA-Text tool union is eight tools, not five.
4. `resources.md` — local `/imagegen` skill contract and OpenAI `gpt-4o-mini` model/pricing references.
5. `slices/README.md` — dependency graph, branch convention, and S00 gate expectations.
6. `octotools/models/planner.py` — three prompt sites to rewire: `analyze_query`, `generate_next_step`, `verificate_context`.
7. `octotools/models/executor.py` — `generate_tool_command` attaches the selected tool's metadata today.
8. `octotools/solver.py` and `tasks/solve.py` — pass `toolbox_mode` through the path used by smoke tests; see GOTCHA-01 before touching solver flow.
9. `tasks/mathvista/run_octotools.sh`, `tasks/medqa/run_octotools.sh`, `tasks/gaia-text/run_octotools.sh` — source of `ENABLED_TOOLS` union.

## Role-split policy (HARD)

This slice MUST be implemented by hephaestus2 (gpt-5.5 high Codex). The orchestrator may dispatch the lane, monitor events, and run the verification gate, but must not author Branch B source code or PNG cards.

## Goal

Replace text `toolbox_metadata` with committed PNG tool cards at all three planner prompt sites and the executor command-generation site. Force planner calls that use cards onto a multimodal engine. Generate the tool-card PNGs offline once using the same `/imagegen` invocation pattern as Simplement bootstrap: subprocess `hephaestus --file <brief> --dangerous`, with an absolute output path written inside each brief.

## Tool-card set

Derive the set from the union of `ENABLED_TOOLS` in MathVista, MedQA, and GAIA-Text run scripts. As of S00 source reads, that union is:

1. `Relevant_Patch_Zoomer_Tool`
2. `Google_Search_Tool`
3. `Python_Code_Generator_Tool`
4. `Image_Captioner_Tool`
5. `Generalist_Solution_Generator_Tool`
6. `Pubmed_Search_Tool`
7. `Wikipedia_Knowledge_Searcher_Tool`
8. `URL_Text_Extractor_Tool`

If the orchestrator explicitly narrows this back to five cards, append/resolve GOTCHA-02 before changing the gate.

## Files to create or modify

```text
/home/david/Projects/octotools-img-toolcards/
├── octotools/models/toolbox_renderer.py      # NEW — loads text metadata or PNG card payloads
├── octotools/tools/_cards/*.png              # NEW — one committed card per tool in the enabled-tools union
├── scripts/generate_tool_cards.py            # NEW — offline card generator using hephaestus + /imagegen briefs
├── octotools/models/planner.py               # MODIFY — image-card payloads at analyze/next-step/verification sites
├── octotools/models/executor.py              # MODIFY — selected tool card in command generation
├── octotools/solver.py                       # MODIFY — pass toolbox_mode through package solver if needed
├── tasks/solve.py                            # MODIFY IF NEEDED — benchmark smoke path must see toolbox_mode; see GOTCHA-01
└── octotools/models/initializer.py           # MODIFY IF NEEDED — engine/toolbox wiring only, no refactor
```

## Public interface

```python
def get_toolbox_payload(toolbox_metadata: dict, available_tools: list[str], mode: str = "text"):
    """Return text metadata for mode='text' or image-card attachments for mode='image'."""
```

Planner/Executor constructors may accept `toolbox_mode: Literal["text", "image"] = "text"` for back compatibility, but Branch B's benchmark path must set `image`.

## CLI contract

```bash
cd /home/david/Projects/octotools-img-toolcards
python scripts/generate_tool_cards.py \
  --output-dir /home/david/Projects/octotools-img-toolcards/octotools/tools/_cards \
  --enabled-tools "Relevant_Patch_Zoomer_Tool,Google_Search_Tool,Python_Code_Generator_Tool,Image_Captioner_Tool,Generalist_Solution_Generator_Tool,Pubmed_Search_Tool,Wikipedia_Knowledge_Searcher_Tool,URL_Text_Extractor_Tool"
```

The generator must write absolute output paths into hephaestus `/imagegen` briefs and must not use browser automation or a direct OpenAI SDK image call.

## Constraints from Gotchas

- **GOTCHA-01** — The benchmark smoke command runs `tasks/solve.py`; Branch B wiring must be exercised by that path.
- **GOTCHA-02** — The enabled-tool union is currently eight tools, so the PNG gate should verify eight cards unless the orchestrator narrows scope.
- **GOTCHA-03** — Do not claim the 90-query grid is solved in B-1; this slice only runs a single MathVista smoke.

## Idempotency / overwrite policy

1. Refuse to overwrite existing non-generated files under `octotools/tools/_cards/` unless they match the expected card basename set.
2. Re-running `scripts/generate_tool_cards.py` may replace generated card PNGs on the private B worktree before commit, but the final commit must contain exactly the expected card inventory.

## Failure behavior

Stable exit codes:

- `0` — all cards generated and the MathVista smoke writes non-empty `direct_output`.
- `10` — card inventory/signature/size failure.
- `20` — solver smoke failure or missing `direct_output`.
- `30` — verbose output does not prove image attachments at planner sites.

## Verification gate (MANDATORY)

### Scope decision for B-1

For the B-1 implementation smoke, use **option (a), MathVista only**, at **index 100**. This honors the user's latest priority for a small, fast, cheap early delta signal while still exercising the benchmark path that matters for Branch B. Generate and commit **all eight** cards from the MathVista/MedQA/GAIA-Text enabled-tool union because card generation is a one-time setup cost and keeping the full inventory avoids rework before the eventual A/B/C run. The eventual early A/B/C comparison implied by this slice is **1 task × N chosen MathVista indices per branch** until the verdict runner broadens scope; with the smoke index only, that is **1 query per branch** for this gate.

The implementing agent must run this exact block and paste literal stdout in the final report:

```bash
set -euo pipefail
cd /home/david/Projects/octotools-img-toolcards
git diff --stat
python - <<'PY'
from pathlib import Path
cards = sorted(Path('octotools/tools/_cards').glob('*.png'))
print(f'card-count: {len(cards)}')
assert len(cards) == 8, [str(p) for p in cards]
for p in cards:
    data = p.read_bytes()
    assert data.startswith(b'\x89PNG\r\n\x1a\n'), p
    assert len(data) > 10000, (p, len(data))
    print(f'contents: path={p}, bytes={len(data)}, signature=png')
PY
python tasks/solve.py --index 100 --task mathvista --data_file mathvista/data/data.json --llm_engine_name gpt-4o-mini --root_cache_dir mathvista/cache --output_json_dir mathvista/results/_smoke_b1 --output_types direct --enabled_tools "Relevant_Patch_Zoomer_Tool,Google_Search_Tool,Python_Code_Generator_Tool,Image_Captioner_Tool,Generalist_Solution_Generator_Tool" --max_time 300 | tee /tmp/octotools-b1-smoke.stdout
python - <<'PY'
import json
p='mathvista/results/_smoke_b1/output_100.json'
data=json.load(open(p))
assert data.get('direct_output'), data
print(f'output: {p}')
print(f"contents: direct_output_len={len(data['direct_output'])}")
PY
grep -E "image attachment|tool card|multimodal|planner.py::(analyze_query|generate_next_step|verificate_context)" /tmp/octotools-b1-smoke.stdout
```

Required pasted-stdout markers:

- `card-count: 8`
- at least eight `contents: path=octotools/tools/_cards/...` lines
- `output: mathvista/results/_smoke_b1/output_100.json`
- a non-empty `contents: direct_output_len=...` line
- stdout evidence for image attachments at all three planner sites

## On gate pass

Commit and push:

```bash
git add octotools/models/toolbox_renderer.py octotools/tools/_cards scripts/generate_tool_cards.py octotools/models/planner.py octotools/models/executor.py octotools/solver.py tasks/solve.py octotools/models/initializer.py
git commit -m "feat: add image tool cards" -m "Co-authored-by: David <david@Kijko.nl>"
git push origin exp/img-toolcards
```

## Final report contract

```yaml
branch: exp/img-toolcards
worktree: /home/david/Projects/octotools-img-toolcards
head_commit: <SHA>
pushed_remote: origin/exp/img-toolcards
files_changed:
  - octotools/models/toolbox_renderer.py
  - octotools/tools/_cards/*.png
  - scripts/generate_tool_cards.py
  - octotools/models/planner.py
  - octotools/models/executor.py
  - octotools/solver.py
  - tasks/solve.py
  - octotools/models/initializer.py
gate_output: |
  ---
  <literal verification gate stdout>
  ---
new_GOTCHAs:
  - <GOTCHA-NN or none>
open_questions:
  - <architectural concern or none>
```
