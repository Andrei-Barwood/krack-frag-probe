"""Machine-readable JSON results.

Author: Kirtan Teg Singh (ਕੀਰਤਨ ਤੇਗ ਸਿੰਘ)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from krack_frag_probe.core.results import RunSummary, TestResult, Verdict


def write_json_report(summary: RunSummary, path: Path | str) -> Path:
    """Write run summary to JSON file. Returns path written."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = summary.to_dict()
    payload["format"] = "krack-frag-probe-results-v1"
    with out.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=False)
        fh.write("\n")
    return out


def load_results_json(path: Path | str) -> dict[str, Any]:
    """Load a previously written results JSON document."""
    with Path(path).open(encoding="utf-8") as fh:
        data: dict[str, Any] = json.load(fh)
    return data


def summary_from_dict(data: dict[str, Any]) -> RunSummary:
    """Rehydrate a :class:`RunSummary` from JSON (best effort)."""
    results: list[TestResult] = []
    for item in data.get("results", []):
        results.append(
            TestResult(
                name=str(item.get("name", "")),
                suite=str(item.get("suite", "")),
                verdict=Verdict(str(item.get("verdict", "INCONCLUSIVE"))),
                explanation=str(item.get("explanation", "")),
                duration_s=float(item.get("duration_s", 0.0)),
                diagnostic_notes=list(item.get("diagnostic_notes") or []),
                frames_crafted=int(item.get("frames_crafted", 0)),
                frames_sent=int(item.get("frames_sent", 0)),
                dry_run=bool(item.get("dry_run", False)),
            )
        )
    summary = RunSummary(
        timestamp=str(data.get("timestamp", "")),
        iface=str(data.get("iface", "")),
        bssid=str(data.get("bssid", "")),
        client=data.get("client"),
        dry_run=bool(data.get("dry_run", False)),
        results=results,
        lab_banner=str(data.get("lab_banner", "LAB ONLY – NOT FOR PRODUCTION USE")),
        tool_version=str(data.get("tool_version", "")),
        author=str(data.get("author", "Kirtan Teg Singh (ਕੀਰਤਨ ਤੇਗ ਸਿੰਘ)")),
        author_romanized=str(data.get("author_romanized", "Kirtan Teg Singh")),
        author_gurmukhi=str(data.get("author_gurmukhi", "ਕੀਰਤਨ ਤੇਗ ਸਿੰਘ")),
        operator_notes=str(data.get("operator_notes", "")),
        interface_details=dict(data.get("interface_details") or {}),
    )
    return summary
