# octotools — Experiment Resources

Last verified: 2026-05-18. This file intentionally contains only URLs and local file references that matter to the octotools image-toolcards experiment; generic Simplement bootstrap links were removed.

## Source repositories and paper

- https://github.com/octotools/octotools — upstream octotools repository; source for the baseline architecture, tasks, tools, and README paper link.
- https://github.com/david-kijko/octotools — David's fork and push target for `research/imagegen-toolcards`, `exp/img-toolcards`, and `exp/img-toolcards-adv-plan`.
- https://arxiv.org/abs/2502.11271 — OctoTools paper linked from the upstream README.

## Benchmark datasets

- https://huggingface.co/datasets/AI4Math/MathVista — MathVista dataset source for the MathVista branch of the 90-query grid.
- https://github.com/jind11/MedQA — MedQA dataset source for the MedQA branch of the 90-query grid.
- https://huggingface.co/datasets/gaia-benchmark/GAIA — GAIA dataset source for GAIA-Text.

## Model and pricing references

- https://developers.openai.com/api/docs/models/gpt-4o-mini — OpenAI model page; verified to list `gpt-4o-mini-2024-07-18`, text+image input, and `gpt-4o-mini` pricing.
- https://developers.openai.com/api/docs/pricing — OpenAI API pricing page; verified to include `gpt-4o-mini-2024-07-18` pricing rows.

## Local runner and skill contracts

- file:///home/david/.claude/skills/imagegen/SKILL.md — local `/imagegen` skill; required by B-1 and C-1 because image creation must route through `hephaestus --file <brief> --dangerous`, not a custom OpenAI SDK script.
- file:///home/david/.claude/skills/Simplement/templates/plan.md — structural template used for this plan shape.
- file:///home/david/.claude/skills/Simplement/templates/slice_NN.md — structural template used for `slices/slice_B1_image_toolcards.md`, `slices/slice_C1_runtime_wrappers.md`, and `slices/slice_C2_plan_review.md`.
- file:///home/david/.claude/skills/Simplement/templates/slices_README.md — structural template used for `slices/README.md`.

## Local source files that constrain implementation

- `docs/superpowers/specs/2026-05-17-imagegen-toolcards-design.md` — ground-truth experiment hypothesis, branch layout, benchmark protocol, and non-goals.
- `octotools/solver.py` — package-level per-query loop and named plan-review insertion point.
- `tasks/solve.py` — benchmark-level per-query loop used by `run_octotools.sh`; see GOTCHA-01.
- `octotools/models/planner.py` — three planner prompt sites that currently interpolate `toolbox_metadata` text.
- `octotools/models/executor.py` — single-tool command-generation prompt site that currently receives one text metadata dict.
- `tasks/mathvista/run_octotools.sh`, `tasks/medqa/run_octotools.sh`, `tasks/gaia-text/run_octotools.sh` — enabled-tools and benchmark script surfaces for MathVista, MedQA, and GAIA-Text.
