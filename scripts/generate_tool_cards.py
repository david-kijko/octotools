#!/usr/bin/env python3
"""Generate committed octotools PNG tool cards via hephaestus + /imagegen briefs."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

EXPECTED_TOOLS = {
    "Relevant_Patch_Zoomer_Tool",
    "Google_Search_Tool",
    "Python_Code_Generator_Tool",
    "Image_Captioner_Tool",
    "Generalist_Solution_Generator_Tool",
    "Pubmed_Search_Tool",
    "Wikipedia_Knowledge_Searcher_Tool",
    "URL_Text_Extractor_Tool",
}

TOOL_PURPOSES = {
    "Relevant_Patch_Zoomer_Tool": "Zoom into the most relevant image patch for visual inspection.",
    "Google_Search_Tool": "Search the public web for current or factual supporting evidence.",
    "Python_Code_Generator_Tool": "Write and run focused Python snippets for computation or data inspection.",
    "Image_Captioner_Tool": "Describe image content when the query depends on visual details.",
    "Generalist_Solution_Generator_Tool": "Synthesize a direct reasoning answer from available context.",
    "Pubmed_Search_Tool": "Search biomedical literature for medical evidence.",
    "Wikipedia_Knowledge_Searcher_Tool": "Retrieve concise encyclopedic background knowledge.",
    "URL_Text_Extractor_Tool": "Extract readable text from a URL for downstream reasoning.",
}


def parse_tools(raw: str) -> list[str]:
    tools = [part.strip() for part in raw.split(",") if part.strip()]
    unexpected = sorted(set(tools) - EXPECTED_TOOLS)
    if unexpected:
        raise SystemExit(f"Unexpected tool names: {unexpected}")
    return tools


def validate_png(path: Path) -> None:
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError(f"{path} is not a PNG")
    if len(data) <= 10_000:
        raise ValueError(f"{path} is too small: {len(data)} bytes")
    with Image.open(path) as img:
        img.verify()


def write_brief(tool_name: str, output_path: Path) -> Path:
    purpose = TOOL_PURPOSES.get(tool_name, "Explain when and how to use this OctoTools tool effectively.")
    text = f"""# /imagegen tool-card brief for {tool_name}

Create a single PNG technical-architecture tool card for OctoTools.

Absolute output path: `{output_path}`

Use `/imagegen` or the available image generation tool to create a polished, legible 16:9 PNG infographic. After generation, copy or move the selected PNG to the absolute output path above. Do not use browser automation. Do not call the OpenAI SDK directly.
Do not run `git add`, `git commit`, `git push`, or any GitHub/CI commands; the parent slice process will handle version control after all cards are generated and validated.

Card content requirements:
- Title text exactly: `{tool_name}`
- One-line purpose: {purpose}
- Show a left-to-right flow: Query context -> Required inputs -> Tool execution -> Output -> When to hand result back to planner.
- Include compact I/O boxes for input types and output type; infer reasonable high-level labels from the tool name if exact schema is unavailable.
- Include one small worked example flow and one limitations/warnings callout.
- Dense but readable technical-architecture-diagram style, white background, dark text, blue/teal accents, clean icons, no logos, no watermark.

Validation requirements before final response:
- `{output_path}` exists.
- It is a PNG larger than 10 KB.
- It has parseable image dimensions.

Final response must include a line starting with `contents:` and the absolute output path.
"""
    fd, name = tempfile.mkstemp(prefix=f"octotools-{tool_name}-", suffix=".md")
    with os.fdopen(fd, "w") as f:
        f.write(text)
    return Path(name)


def run_hephaestus(brief: Path, cwd: Path) -> None:
    env = os.environ.copy()
    env["HEPHAESTUS_MODEL"] = "gpt-5.5"
    env["HEPHAESTUS_REASONING_EFFORT"] = "high"
    env["COMPLETION_GUARD_TASK_TYPE"] = "file_create"
    cmd = ["hephaestus", "--file", str(brief), "--dir", str(cwd), "--dangerous"]
    subprocess.run(cmd, check=True, env=env)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--enabled-tools", required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    tools = parse_tools(args.enabled_tools)
    expected_paths = {output_dir / f"{tool}.png" for tool in tools}
    for existing in output_dir.glob("*.png"):
        if existing not in expected_paths:
            raise SystemExit(f"Refusing unexpected card file: {existing}")
        if existing.exists() and not args.force:
            validate_png(existing)
            print(f"contents: existing valid card retained: {existing}")
            continue

    for tool_name in tools:
        output_path = output_dir / f"{tool_name}.png"
        if output_path.exists() and not args.force:
            continue
        brief = write_brief(tool_name, output_path)
        try:
            run_hephaestus(brief, repo_root)
        finally:
            brief.unlink(missing_ok=True)
        validate_png(output_path)
        print(f"contents: generated {output_path}")

    for path in sorted(expected_paths):
        validate_png(path)
        print(f"contents: validated {path} bytes={path.stat().st_size}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"card generation failed: {exc}", file=sys.stderr)
        raise SystemExit(10)
