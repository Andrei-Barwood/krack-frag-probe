#!/usr/bin/env python3
"""Optional experimental local report viewer.

Opens a generated HTML or Markdown report in a simple Tkinter window or the
system browser. Marked experimental — not required for core CLI use.

Usage:
    python scripts/generate_report_viewer.py ./kfp-results/report.html
    python scripts/generate_report_viewer.py ./kfp-results/report.md --browser
"""

from __future__ import annotations

import argparse
import sys
import webbrowser
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "EXPERIMENTAL: view krack-frag-probe lab reports locally. "
            "LAB ONLY – NOT FOR PRODUCTION USE."
        )
    )
    parser.add_argument("path", type=Path, help="Path to report.html or report.md")
    parser.add_argument(
        "--browser",
        action="store_true",
        help="Open with the system default browser instead of Tkinter.",
    )
    args = parser.parse_args(argv)

    path: Path = args.path
    if not path.is_file():
        print(f"File not found: {path}", file=sys.stderr)
        return 2

    print("LAB ONLY – NOT FOR PRODUCTION USE (experimental viewer)")
    print(f"Opening: {path.resolve()}")

    if args.browser or path.suffix.lower() in {".html", ".htm"}:
        uri = path.resolve().as_uri()
        webbrowser.open(uri)
        return 0

    # Markdown / other: try Tkinter text view
    try:
        import tkinter as tk
        from tkinter import scrolledtext
    except ImportError:
        print("Tkinter not available; falling back to browser/text.", file=sys.stderr)
        print(path.read_text(encoding="utf-8")[:8000])
        return 0

    root = tk.Tk()
    root.title(f"krack-frag-probe viewer (experimental) — {path.name}")
    root.geometry("900x700")

    banner = tk.Label(
        root,
        text="LAB ONLY – NOT FOR PRODUCTION USE · experimental viewer",
        fg="white",
        bg="#5c1a1a",
        font=("Helvetica", 12, "bold"),
        pady=8,
    )
    banner.pack(fill=tk.X)

    text = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Menlo", 11))
    text.pack(fill=tk.BOTH, expand=True)
    content = path.read_text(encoding="utf-8")
    text.insert(tk.END, content)
    text.configure(state=tk.DISABLED)

    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
