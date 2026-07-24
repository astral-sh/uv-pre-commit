#!/usr/bin/env python3
"""Hook: regenerate requirements.txt (or a custom output file) via `uv export`
and automatically stage it so the commit is not interrupted by pre-commit's
"files were modified by this hook" check.

Usage (via .pre-commit-config.yaml):
    - id: uv-update-requirements
      args: ["--frozen", "--output-file=requirements.txt", "--quiet"]
"""
from __future__ import annotations

import subprocess
import sys

def _parse_output_file(args: list[str]) -> str:
    """Extract the --output-file value from the args list."""
    for i, arg in enumerate(args):
        if arg.startswith("--output-file="):
            return arg.split("=", 1)[1]
        if arg == "--output-file" and i + 1 < len(args):
            return args[i + 1]
    return "requirements.txt"

def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]

    # Fall back to sensible defaults when no args are supplied.
    if not args:
        args = ["--frozen", "--output-file=requirements.txt", "--quiet"]

    # Run `uv export` with the provided arguments.
    export_result = subprocess.run(["uv", "export", *args])
    if export_result.returncode != 0:
        return export_result.returncode

    # Stage the generated file so pre-commit does not abort the commit.
    output_file = _parse_output_file(args)
    stage_result = subprocess.run(["git", "add", output_file])
    if stage_result.returncode != 0:
        print(
            f"uv-update-requirements: warning: could not stage '{output_file}' "
            f"(git add exited with {stage_result.returncode})",
            file=sys.stderr,
        )
        return stage_result.returncode

    return 0

if __name__ == "__main__":
    sys.exit(main())
