# octotools — Implementation Slices

<!-- Replace octotools with the target project or skill name at bootstrap time. -->
1 placeholder testable slices that build `octotools` from scratch. Each slice is a
self-contained brief intended to be handed to a single executing subagent or
implementer process. Read this file once to understand the dependency shape,
then work through `slice_<NN>_<shortname>.md` in graph order.
<!-- Replace 1 placeholder with the final slice count. Replace <NN> / <shortname> with
     the target repo's concrete slice ID and filename convention. -->

## Required reading (the harness — every slice agent reads these)

1. **`plan.md`** — architecture, modules, surfaces
2. **`Gotchas.md`** — empirical corrections to the docs; the agent MUST
   respect these or the implementation will not work
3. **`resources.md`** — first-party URLs
4. **`docs/octotools-architecture.png.png`** — visual reference
5. **`docs/octotools-implementation-path.png.png`** — visual rendering of this manifest
6. **`docs/parity-matrix.md`** — operator-facing parity surface
7. No extra slice-specific reference yet — bootstrap creates only the placeholder manifest row

<!-- Replace octotools-architecture.png with the architecture diagram basename,
     octotools-implementation-path.png with the dependency-path diagram basename,
     and <slice-specific reference, if any> with either a real path or remove
     the row when no extra reference is needed. -->

Every future `slice_<NN>_<shortname>.md` adds its own slice-specific context on top.

## Dependency graph

<!-- Replace this fenced block with ASCII art or a markdown diagram generated
     from the manifest table below. Nodes are slice IDs; edges are "depends on"
     relations; annotate independent gates and any intentionally bundled nodes. -->

```
<dependency graph for octotools>
```

The slice executor parses this section together with the manifest table below
to derive the topological order for unattended dispatch. Keep the graph, the
`Depends on` column, and the concrete slice files synchronized.
<!-- Replace <dependency graph for octotools> with a graph that preserves the
     exact dependency topology selected during bootstrap. -->

## Bundling

Each slice has an independent verification gate. **None bundled by default.**
A slice is bundled with another only when the operator records a written
justification here because both slices share an unsplittable verification
surface.
<!-- If bootstrap discovers a required bundle, replace this paragraph with the
     bundle ID(s), the slices included, and the single verification surface that
     makes independent testing impossible. Otherwise leave "None bundled". -->

## How to execute a slice

The orchestrator walks the graph-derived topological order and dispatches one
implementer per slice:

```bash
# pseudo-orchestrator flow; replace placeholders during bootstrap
order=$(parse_slices_readme_for_topological_order slices/README.md)
for N in $order; do
  brief=$(mktemp "/tmp/octotools-${N}.XXXXXX.md")
  cat "slices/${N}_<shortname>.md" > "$brief"
  HEPHAESTUS_MODEL=gpt-5.5 HEPHAESTUS_REASONING_EFFORT=high hephaestus --file "$brief" --dir "$(pwd)"
  run the slice's Verification gate "$N" | tee ".octotools/runs/${N}.gate.stdout"
done
```

<!-- Replace HEPHAESTUS_MODEL=gpt-5.5 HEPHAESTUS_REASONING_EFFORT=high hephaestus with the project-approved dispatch command
     (for Simplement-shaped repos, the hephaestus2 wrapper); replace
     run the slice's Verification gate with the harness command that runs the slice's gate;
     replace octotools with the hidden state directory name. -->

Each slice file ends with a **Verification gate** that the executing agent MUST
pass with literal command output pasted before reporting success. The
orchestrator only moves on after the gate passes.

## Update protocol (every slice agent follows this)

### Role-split policy

Implementation must be authored by `hephaestus2 (gpt-5.5 high Codex)`, not by the
orchestrator. The orchestrator may draft briefs, dispatch workers, monitor
outputs, run verification, and merge reviewed work; it must not author source
code, tests, or generated target harness files unless the project explicitly
marks a scaffolding slice as orchestrator-owned.
<!-- Replace hephaestus2 (gpt-5.5 high Codex) with the authorized implementer, e.g.
     "hephaestus2 (gpt-5.5 high Codex)" for Simplement-shaped builds. -->

If during execution the agent discovers a fact that **invalidates an assumption
in the harness**, the agent must:

1. **Stop** before completing the slice.
2. **Append** a new `GOTCHA-NN` entry to `Gotchas.md` (newest first) per the
   template at the top of that file.
3. **Update** `plan.md` (any sections affected), `resources.md` (any new URLs),
   and `docs/octotools-architecture.png.png` / `docs/octotools-implementation-path.png.png`
   if the visual contract changes.
4. **Re-run the failing step** with the harness updated.
5. **Commit** harness changes on the slice branch BEFORE committing the slice's
   code, so reviewers see the assumption shift first.
6. **Note** the new GOTCHA-NN in the slice's PR/completion summary.

<!-- Replace visual placeholders with the concrete diagram names. If a project
     has a human-in-loop severity policy, add the pause/resume rule here. -->

If the discovered fact does not invalidate the harness but is useful context,
append it as an open probe or low-severity note in `Gotchas.md` instead.

## Slice manifest

| # | File | Title | Depends on | Bundled? | Verification gate |
|---|---|---|---|---|---|
| 01 | `slice_01_define-first-vertical.md` | Define the first vertical slice | — | no | slice brief exists and names a concrete verification gate |

<!-- Add one row per slice. Replace <NN>, <shortname>, <title>, dependency
     list, bundle status, and <one-line gate>. Keep this table's column shape:
     # | File | Title | Depends on | Bundled? | Verification gate. -->

## Acceptance

After the last slice passes, `octotools` is v1-complete. Any remaining
limitations are documented in `docs/parity-matrix.md` and the architecture
visual's known-limitations panel.
<!-- Replace the acceptance sentence if the project has a named final gate,
     e.g. "After S11 passes" or "After W10 passes". -->

## Branch convention

`slice/<NN>-<shortname>`, merged to `main` with `--no-ff` after independent
verification of each slice's gate.
<!-- Replace the branch pattern if the project uses prefixed IDs such as S<NN>
     or W<NN>. Preserve the --no-ff merge rule unless the operator records a
     different repository policy. -->

## The parity matrix is harness too

`docs/parity-matrix.md` is the second-tier authoritative reference for
operator-facing semantics. Every slice that adds or changes a CLI verb, harness
file, dispatch behavior, event shape, or verification surface must check the
matrix first; update an existing row's status/evidence or add a new row before
reporting completion.
<!-- Remove this section only when bootstrap records that the target has no
     parity surface. Otherwise keep it as a harness requirement. -->

## Implementation path diagram

See `docs/octotools-implementation-path.png.png` for the visual rendering of the
dependency graph above with verification-gate annotations per slice.
<!-- Replace octotools-implementation-path.png with the concrete PNG basename. -->
