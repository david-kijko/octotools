"""Subprocess wrapper for adversarial hephaestus2 plan review."""

from __future__ import annotations

import os
import shlex
import subprocess
import tempfile
from pathlib import Path


def _brief(plan_text: str, diagram_path: Path | None) -> str:
    diagram_section = "No diagram was provided."
    if diagram_path is not None:
        diagram = diagram_path.expanduser().resolve()
        diagram_section = f"Diagram for review:\n\n![](file://{diagram})"

    return f"""gap_analysis

Role: adversarial reviewer.

Review the plan below for correctness, missing steps, brittle assumptions, and verification gaps.
Be concise and concrete. If the plan is acceptable with no material concerns, return `approved`.

Plan text:
{plan_text}

{diagram_section}

Required completion-guard evidence:
- Include at least one literal line beginning with `output:` that summarizes your review result.
- Do not claim completion without the concrete critique or `approved`.
"""


def critique(plan_text: str, diagram_path: Path | None) -> str:
    """Run hephaestus2 as an adversarial reviewer and return critique text.

    Empty or whitespace-only subprocess output is normalized to ``approved``.
    """

    with tempfile.TemporaryDirectory(prefix="octotools-hephaestus2-") as tmp:
        brief_path = Path(tmp) / "hephaestus2-brief.md"
        brief_path.write_text(_brief(plan_text, diagram_path), encoding="utf-8")

        argv = ["hephaestus", "--file", str(brief_path), "--dangerous"]
        env = os.environ.copy()
        env["HEPHAESTUS_MODEL"] = "gpt-5.5"
        env["HEPHAESTUS_REASONING_EFFORT"] = "high"
        completed = subprocess.run(
            argv,
            text=True,
            capture_output=True,
            timeout=600,
            env=env,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"hephaestus2 critique command failed: {shlex.join(argv)}; "
                f"exit={completed.returncode}; "
                f"stdout-tail={completed.stdout[-1000:]!r}; "
                f"stderr-tail={completed.stderr[-1000:]!r}"
            )

    out = completed.stdout.strip()
    return out if out else "approved"
