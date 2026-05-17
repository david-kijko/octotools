# octotools — Gotchas

Living list of things that **were not what we expected** when building the octotools image-toolcards experiment harness. Findings must come from empirical probes, source reads, or docs that turned out to be stale; do not add speculative gotchas.

**Append rule for future findings:** new entries go at the **top** of `## Findings` (newest first), with the template below filled in. Do not edit historical entries except to add a `Resolved` note when an upstream change fixes the gotcha.

---

## Entry template

```markdown
### GOTCHA-NN — <one-line headline>

- **Date:** 2026-05-18
- **Discovered via:** empirical probe | doc read | source read | production incident | ...
- **Source:** path/to/probe-or-spec.md | URL | session-id | ...
- **Symptom:** what looked broken or surprising
- **Root cause:** what's actually happening
- **Workaround / fix:** what to do until/unless upstream changes
- **Affects:** plan.md §X, src/<project>/Y.py, plugin/hooks/hooks.json, ...
- **Severity:** L1 trivial | L2 light | L3 medium | L4 heavy | L5 blocking
- **Resolved:** (only when fixed upstream — note the version/commit)
```

---

## Findings

### GOTCHA-04 — Requested Simplement GitHub URL is not fetchable

- **Date:** 2026-05-18
- **Discovered via:** empirical probe
- **Source:** `curl -L -o /dev/null -s -w '%{http_code}' https://github.com/david-kijko/Simplement` returned `404` during S00 URL verification; local templates exist under `/home/david/.claude/skills/Simplement/`.
- **Symptom:** The S00 prompt asks `resources.md` to include `https://github.com/david-kijko/Simplement`, but also requires every new URL to be real and fetchable.
- **Root cause:** The requested GitHub URL is not publicly fetchable from this environment.
- **Workaround / fix:** Drop the GitHub URL from `resources.md` and cite local `file:///home/david/.claude/skills/Simplement/...` template references instead.
- **Affects:** `resources.md`, `plan.md` S00 source trail
- **Severity:** L2 light
- **Resolved:**

### GOTCHA-03 — Existing run scripts do not encode the spec's 90-query grid

- **Date:** 2026-05-18
- **Discovered via:** source read
- **Source:** `docs/superpowers/specs/2026-05-17-imagegen-toolcards-design.md` Benchmark Protocol; `tasks/mathvista/run_octotools.sh`; `tasks/medqa/run_octotools.sh`; `tasks/gaia-text/run_octotools.sh`
- **Symptom:** The spec says the early sample uses 10 indices per task (`100,110,120,130,140,150,160,170,180,190`) for a 90-query, 3-branch grid, but the checked-in scripts use different baked-in ranges.
- **Root cause:** `mathvista` uses `seq 100 199`, `medqa` uses `seq 100 107`, and `gaia-text` uses `seq 0 7`; none of those three scripts directly represents the spec's 10-index grid.
- **Workaround / fix:** The verdict runner or edited branch-local scripts must explicitly drive the spec's fixed 10 indices for all three tasks before claiming the 90-query grid ran.
- **Affects:** `plan.md` §4, `slices/README.md`, future benchmark/verdict runner work
- **Severity:** L3 medium
- **Resolved:**

### GOTCHA-02 — The MathVista/MedQA/GAIA-Text tool union is eight tools, not five

- **Date:** 2026-05-18
- **Discovered via:** source read
- **Source:** `tasks/mathvista/run_octotools.sh`, `tasks/medqa/run_octotools.sh`, `tasks/gaia-text/run_octotools.sh`
- **Symptom:** The S00 slice prompt asks B-1 to derive the union of `ENABLED_TOOLS` across the three task scripts, but also says the PNG gate should find five cards.
- **Root cause:** The actual union is eight tool classes: `Relevant_Patch_Zoomer_Tool`, `Google_Search_Tool`, `Python_Code_Generator_Tool`, `Image_Captioner_Tool`, `Generalist_Solution_Generator_Tool`, `Pubmed_Search_Tool`, `Wikipedia_Knowledge_Searcher_Tool`, and `URL_Text_Extractor_Tool`.
- **Workaround / fix:** B-1 should generate and verify one PNG per tool in the actual union unless the orchestrator explicitly narrows the experiment back to MathVista-only cards.
- **Affects:** `slices/slice_B1_image_toolcards.md`, `slices/README.md`, `plan.md` §3
- **Severity:** L3 medium
- **Resolved:**

### GOTCHA-01 — Benchmark smoke commands execute `tasks/solve.py`, not `octotools/solver.py`

- **Date:** 2026-05-18
- **Discovered via:** source read
- **Source:** `tasks/mathvista/run_octotools.sh` invokes `python solve.py`; `tasks/solve.py` defines its own `Solver`; `octotools/solver.py` contains the package-level loop named in the design spec.
- **Symptom:** The spec names `octotools/solver.py:80` as the C-2 plan-review insertion point, but the required smoke command runs `python tasks/solve.py`, whose local `Solver.solve()` has a separate `analyze_query` → step-loop implementation.
- **Root cause:** The benchmark harness is not a thin wrapper around `octotools/solver.py`; it duplicates the solver loop in `tasks/solve.py` and instantiates `Planner`, `Memory`, and `Executor` directly.
- **Workaround / fix:** C-2 must ensure the plan-review phase is observable from the benchmark command, either by patching `tasks/solve.py` as well or by refactoring it to call the package solver within the slice's strict scope.
- **Affects:** `plan.md` §3, `slices/slice_C2_plan_review.md`, C-2 verification gate
- **Severity:** L4 heavy
- **Resolved:**
