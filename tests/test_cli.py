"""CLI integration tests (dry-run only, no live injection)."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from krack_frag_probe.cli import cli


@pytest.mark.integration
def test_list_tests() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["list-tests"])
    assert result.exit_code == 0
    assert "key_reinstall" in result.output
    assert "frag_cache" in result.output
    assert "LABORATORY" in result.output.upper() or "LAB ONLY" in result.output.upper()


@pytest.mark.integration
def test_run_dry_run_pass(tmp_path: Path) -> None:
    runner = CliRunner()
    out = tmp_path / "out"
    result = runner.invoke(
        cli,
        [
            "run",
            "--iface",
            "mon0",
            "--bssid",
            "aa:bb:cc:dd:ee:ff",
            "--test",
            "all",
            "--dry-run",
            "--yes-i-understand",
            "--output",
            str(out),
        ],
    )
    assert result.exit_code == 0, result.output
    assert (out / "results.json").is_file()
    assert (out / "report.md").is_file()
    assert (out / "report.html").is_file()
    assert "PASS" in result.output


@pytest.mark.integration
def test_run_simulate_regression(tmp_path: Path) -> None:
    runner = CliRunner()
    out = tmp_path / "out"
    result = runner.invoke(
        cli,
        [
            "run",
            "--iface",
            "mon0",
            "--bssid",
            "aa:bb:cc:dd:ee:ff",
            "--test",
            "key_reinstall",
            "--dry-run",
            "--yes-i-understand",
            "--simulate-regression",
            "--output",
            str(out),
        ],
    )
    assert result.exit_code == 1, result.output
    assert "FAIL" in result.output or "SIMULATED" in result.output


@pytest.mark.integration
def test_run_missing_ack_fails(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "run",
            "--iface",
            "mon0",
            "--bssid",
            "aa:bb:cc:dd:ee:ff",
            "--dry-run",
            "--output",
            str(tmp_path / "o"),
        ],
        input="nope\n",
    )
    assert result.exit_code == 2


@pytest.mark.integration
def test_report_from_json(tmp_path: Path) -> None:
    # First produce results
    runner = CliRunner()
    out = tmp_path / "out"
    runner.invoke(
        cli,
        [
            "run",
            "--iface",
            "mon0",
            "--bssid",
            "aa:bb:cc:dd:ee:ff",
            "--test",
            "probe_request_smoke",
            "--dry-run",
            "--yes-i-understand",
            "--output",
            str(out),
        ],
    )
    html_out = tmp_path / "rebuilt.html"
    result = runner.invoke(
        cli,
        [
            "report",
            "--input",
            str(out / "results.json"),
            "--format",
            "html",
            "--output",
            str(html_out),
        ],
    )
    assert result.exit_code == 0, result.output
    assert html_out.is_file()
    assert "LAB ONLY" in html_out.read_text(encoding="utf-8")
