"""Human-readable Markdown report generation.

Author: Kirtan Teg Singh (ਕੀਰਤਨ ਤੇਗ ਸਿੰਘ)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from krack_frag_probe.core.results import RunSummary
from krack_frag_probe.reporting.json_report import summary_from_dict


def render_markdown(summary: RunSummary) -> str:
    """Render a full Markdown report string with lab-only banner."""
    counts = summary.counts
    lines: list[str] = [
        "# krack-frag-probe Lab Report",
        "",
        "> **LAB ONLY – NOT FOR PRODUCTION USE**",
        ">",
        "> Authorized laboratory regression testing only. Not an exploit report.",
        "> Do not use against production networks or third-party equipment without",
        "> written authorization.",
        ">",
        f"> **Author / ਲੇਖਕ:** {summary.author_romanized} ({summary.author_gurmukhi})",
        "",
        "## Run metadata",
        "",
        "| Field | Value |",
        "| ----- | ----- |",
        f"| Timestamp (UTC) | `{summary.timestamp}` |",
        f"| Tool version | `{summary.tool_version}` |",
        f"| Author (romanized) | `{summary.author_romanized}` |",
        f"| Author (Gurmukhi / ਗੁਰਮੁਖੀ) | `{summary.author_gurmukhi}` |",
        f"| Interface | `{summary.iface}` |",
        f"| Target BSSID | `{summary.bssid}` |",
        f"| Client MAC | `{summary.client or '—'}` |",
        f"| Dry-run | `{summary.dry_run}` |",
        f"| Interface details | `{summary.interface_details}` |",
        "",
        f"_{summary.operator_notes}_",
        "",
        "## Summary",
        "",
        "| Total | PASS | FAIL | INCONCLUSIVE | SKIPPED | ERROR |",
        "| ----- | ---- | ---- | ------------ | ------- | ----- |",
        (
            f"| {counts.get('total', 0)} "
            f"| {counts.get('PASS', 0)} "
            f"| {counts.get('FAIL', 0)} "
            f"| {counts.get('INCONCLUSIVE', 0)} "
            f"| {counts.get('SKIPPED', 0)} "
            f"| {counts.get('ERROR', 0)} |"
        ),
        "",
        "## Per-test results",
        "",
    ]

    for r in summary.results:
        lines.extend(
            [
                f"### `{r.suite}.{r.name}` — **{r.verdict.value}**",
                "",
                f"- **Duration:** {r.duration_s:.3f}s",
                f"- **Frames crafted / sent:** {r.frames_crafted} / {r.frames_sent}",
                f"- **Dry-run:** {r.dry_run}",
                f"- **Explanation:** {r.explanation}",
            ]
        )
        if r.diagnostic_notes:
            lines.append("- **Diagnostics:**")
            for note in r.diagnostic_notes:
                lines.append(f"  - `{note}`")
        lines.append("")

    lines.extend(
        [
            "---",
            "",
            "## Safety reminder",
            "",
            "- This report documents **regression probes** for long-patched behaviors.",
            "- It is **not** evidence of a new vulnerability or zero-day.",
            "- **LAB ONLY – NOT FOR PRODUCTION USE.**",
            f"- **Author / ਲੇਖਕ:** {summary.author_romanized} ({summary.author_gurmukhi})",
            "",
        ]
    )
    return "\n".join(lines)


def write_markdown_report(summary: RunSummary, path: Path | str) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_markdown(summary), encoding="utf-8")
    return out


def write_markdown_from_json(data: dict[str, Any], path: Path | str) -> Path:
    return write_markdown_report(summary_from_dict(data), path)
