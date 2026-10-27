from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from app.graph import compile_graph, initial_state
from app.nodes.assemble import json_path_for


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m app.main",
        description="Turn a .txt requirements spec into a draft abstraction model (HTML + JSON).",
    )
    parser.add_argument("--input", required=True, help="Path to the .txt spec file.")
    parser.add_argument(
        "--output",
        default="outputs/model.html",
        help="Path of the HTML file to write. The JSON model is written alongside it with a .json suffix.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if not os.environ.get("GROQ_API_KEY"):
        print(
            "error: GROQ_API_KEY is not set. This pipeline makes real Groq calls.\n"
            "       export GROQ_API_KEY=gsk_... and re-run.",
            file=sys.stderr,
        )
        return 2

    html_path = Path(args.output)
    try:
        app = compile_graph()
        final = app.invoke(initial_state(args.input, str(html_path)))
    except Exception as exc:
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    model = final["model"]
    print(f"Wrote {html_path}")
    print(f"Wrote {json_path_for(str(html_path))}")
    print(
        f"{len(model.features)} features, {len(model.relationships)} relationships, "
        f"{len(model.warnings)} warnings"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
