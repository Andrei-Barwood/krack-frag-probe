"""Unit tests for result models and reporting."""

from __future__ import annotations

from pathlib import Path

import pytest

from krack_frag_probe.core.results import RunSummary, TestResult, Verdict
from krack_frag_probe.reporting.html_report import render_html, write_html_report
from krack_frag_probe.reporting.json_report import (
    load_results_json,
    summary_from_dict,
    write_json_report,
)
from krack_frag_probe.reporting.markdown_report import render_markdown, write_markdown_report


def _sample_summary() -> RunSummary:
    s = RunSummary.create(
        iface="mon0",
        bssid="aa:bb:cc:dd:ee:ff",
        client=None,
        dry_run=True,
        tool_version="1.0.0",
        interface_details={"note": "test"},
    )
    s.add(
        TestResult(
            name="nonce_reuse_guard",
            suite="key_reinstall",
            verdict=Verdict.PASS,
            explanation="ok",
            duration_s=0.1,
            frames_crafted=2,
            frames_sent=0,
            dry_run=True,
        )
    )
    s.add(
        TestResult(
            name="cache_poison_style_probe",
            suite="frag_cache",
            verdict=Verdict.FAIL,
            explanation="SIMULATED",
            duration_s=0.2,
            dry_run=True,
        )
    )
    return s


@pytest.mark.unit
def test_counts_and_exit_code() -> None:
    s = _sample_summary()
    assert s.counts["total"] == 2
    assert s.counts["PASS"] == 1
    assert s.counts["FAIL"] == 1
    assert s.any_failures()
    assert s.exit_code() == 1


@pytest.mark.unit
def test_exit_code_all_pass() -> None:
    s = RunSummary.create(
        iface="mon0",
        bssid="aa:bb:cc:dd:ee:ff",
        client=None,
        dry_run=True,
        tool_version="1.0.0",
    )
    s.add(
        TestResult(
            name="t",
            suite="s",
            verdict=Verdict.PASS,
            explanation="ok",
        )
    )
    assert s.exit_code() == 0


@pytest.mark.unit
def test_json_roundtrip(tmp_path: Path) -> None:
    s = _sample_summary()
    path = write_json_report(s, tmp_path / "results.json")
    data = load_results_json(path)
    assert data["bssid"] == "aa:bb:cc:dd:ee:ff"
    assert data["lab_banner"].startswith("LAB ONLY")
    rehydrated = summary_from_dict(data)
    assert len(rehydrated.results) == 2
    assert rehydrated.results[1].verdict == Verdict.FAIL


@pytest.mark.unit
def test_markdown_contains_banner() -> None:
    md = render_markdown(_sample_summary())
    assert "LAB ONLY" in md
    assert "nonce_reuse_guard" in md
    assert "**PASS**" in md or "PASS" in md


@pytest.mark.unit
def test_html_contains_banner(tmp_path: Path) -> None:
    html = render_html(_sample_summary())
    assert "LAB ONLY" in html
    assert "nonce_reuse_guard" in html
    path = write_html_report(_sample_summary(), tmp_path / "r.html")
    assert path.is_file()
    write_markdown_report(_sample_summary(), tmp_path / "r.md")
    assert (tmp_path / "r.md").is_file()
