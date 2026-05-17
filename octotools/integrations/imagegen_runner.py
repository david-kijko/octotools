"""Subprocess wrapper for generating PNG diagrams through the local imagegen skill."""

from __future__ import annotations

import os
import shlex
import struct
import subprocess
import tempfile
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MIN_PNG_BYTES = 10 * 1024


def _png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as file:
        header = file.read(24)
    if len(header) < 24 or header[:8] != PNG_SIGNATURE or header[12:16] != b"IHDR":
        raise ValueError(f"not a valid PNG IHDR header: {path}")
    width, height = struct.unpack(">II", header[16:24])
    if width <= 0 or height <= 0:
        raise ValueError(f"invalid PNG dimensions {width}x{height}: {path}")
    return width, height


def _validate_png(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"imagegen output was not created: {path}")
    size = path.stat().st_size
    if size <= MIN_PNG_BYTES:
        raise ValueError(f"imagegen output is too small ({size} bytes): {path}")
    _png_dimensions(path)


def _brief(brief_text: str, output_path: Path) -> str:
    return f"""file_create

Use $imagegen to generate the requested image and save it to the exact output path specified below.

User request:
{brief_text}

Output path (required, absolute):
{output_path}

Execution constraints:
- Use Codex's built-in $imagegen / image_gen tool.
- Do not use browser automation, Playwright, ChatGPT web UI, OpenAI SDK/API scripts, or a custom runner.
- Save (or move/copy) the final selected image to the Output path above. Overwrite is permitted for this runtime integration call.
- Produce a real PNG diagram file, not SVG, HTML, a placeholder, or a text-only artifact.

Required verification in your final output (literal lines):
- A line starting with `output:` followed by the absolute generated image path (MUST equal the Output path above).
- A line starting with `contents:` followed by path, byte size, image format (must be PNG), width, and height obtained from a real file/header inspection (e.g. `file` or `python -c "import struct; ..."`).
- Do not claim completion without those literal lines.
"""


def generate_image(brief_text: str, output_path: str | Path) -> Path:
    """Generate a PNG image via hephaestus/imagegen and return its absolute path.

    The caller owns retry policy. This function raises if the subprocess fails or
    if the produced file is not a parseable PNG larger than 10 KB.
    """

    target = Path(output_path).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="octotools-imagegen-") as tmp:
        brief_path = Path(tmp) / "imagegen-brief.md"
        brief_path.write_text(_brief(brief_text, target), encoding="utf-8")

        argv = ["hephaestus", "--file", str(brief_path), "--dangerous"]
        env = os.environ.copy()
        env["HEPHAESTUS_MODEL"] = "gpt-5.5"
        env["HEPHAESTUS_REASONING_EFFORT"] = "high"
        completed = subprocess.run(
            argv,
            text=True,
            capture_output=True,
            timeout=900,
            env=env,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"imagegen command failed: {shlex.join(argv)}; "
                f"exit={completed.returncode}; "
                f"stdout-tail={completed.stdout[-1000:]!r}; "
                f"stderr-tail={completed.stderr[-1000:]!r}"
            )

    try:
        _validate_png(target)
    except Exception as exc:
        raise RuntimeError(f"imagegen did not produce a valid PNG at {target}: {exc}") from exc
    return target
