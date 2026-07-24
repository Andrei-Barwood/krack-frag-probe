"""Command-line interface for krack-frag-probe.

Every path that could transmit frames displays the legal warning and requires
acknowledgement. Live runs refuse non-monitor interfaces and missing targets.

Author: Kirtan Teg Singh (ਕੀਰਤਨ ਤੇਗ ਸਿੰਘ)
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from krack_frag_probe import AUTHOR_FULL, LAB_ONLY_BANNER, __version__
from krack_frag_probe.core.interface import ensure_interface_ready
from krack_frag_probe.core.results import RunSummary, Verdict
from krack_frag_probe.core.tester import TestContext
from krack_frag_probe.reporting.html_report import write_html_from_json, write_html_report
from krack_frag_probe.reporting.json_report import load_results_json, write_json_report
from krack_frag_probe.reporting.markdown_report import (
    write_markdown_from_json,
    write_markdown_report,
)
from krack_frag_probe.testsuites import get_tests, list_suite_info
from krack_frag_probe.utils.logging import setup_logging
from krack_frag_probe.utils.validation import (
    ValidationError,
    require_explicit_targets,
    require_legal_acknowledgement,
    validate_mac,
)

EXIT_OK = 0
EXIT_FAIL = 1
EXIT_CONFIG = 2

BANNER_TEXT = """\
[bold red]AUTHORIZED LABORATORY USE ONLY[/bold red]

This tool is a [bold]defensive regression tester[/bold] for long-patched Wi-Fi
edge cases. It is [bold]not[/bold] an exploit kit.

You must only target equipment [bold]you own[/bold] or have
[bold]written permission[/bold] to test.

[dim]Author: Kirtan Teg Singh (ਕੀਰਤਨ ਤੇਗ ਸਿੰਘ)[/dim]
"""


def _console(no_color: bool) -> Console:
    return Console(no_color=no_color, highlight=False, stderr=False)


def _print_banner(console: Console) -> None:
    console.print(
        Panel(
            BANNER_TEXT,
            title="krack-frag-probe",
            subtitle=f"v{__version__} · {AUTHOR_FULL}",
            border_style="red",
        )
    )
    console.print(f"[bold yellow]{LAB_ONLY_BANNER}[/bold yellow]\n")


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    help=(
        "Educational lab-only regression tester for long-patched Wi-Fi edge cases "
        "(KRACK/FragAttacks style). AUTHORIZED LABORATORY USE ONLY. "
        "Author: Kirtan Teg Singh (ਕੀਰਤਨ ਤੇਗ ਸਿੰਘ)."
    ),
)
@click.version_option(
    __version__,
    prog_name="krack-frag-probe",
    message=f"%(prog)s, version %(version)s\nAuthor: {AUTHOR_FULL}",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose logging.")
@click.option("--json", "json_mode", is_flag=True, help="JSON-lines logging on stderr.")
@click.option("--no-color", is_flag=True, help="Disable ANSI colors.")
@click.pass_context
def cli(ctx: click.Context, verbose: bool, json_mode: bool, no_color: bool) -> None:
    """Root group; global flags apply to all subcommands."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["json_mode"] = json_mode
    ctx.obj["no_color"] = no_color
    ctx.obj["console"] = _console(no_color)
    setup_logging(verbose=verbose, json_mode=json_mode, no_color=no_color)


@cli.command("list-tests")
@click.option("--verbose", "-v", "list_verbose", is_flag=True, help="Show historical category.")
@click.pass_context
def list_tests_cmd(ctx: click.Context, list_verbose: bool) -> None:
    """Enumerate available regression test suites and tests."""
    console: Console = ctx.obj["console"]
    _print_banner(console)
    console.print(
        "[bold]Available regression tests[/bold] (educational checks for long-patched behaviors)\n"
    )
    table = Table(show_header=True, header_style="bold")
    table.add_column("Suite")
    table.add_column("Test")
    table.add_column("Description")
    if list_verbose or ctx.obj.get("verbose"):
        table.add_column("Historical category")

    for row in list_suite_info(verbose=True):
        cols = [row["suite"], row["name"], row["description"]]
        if list_verbose or ctx.obj.get("verbose"):
            cols.append(row.get("historical_category", ""))
        table.add_row(*cols)

    console.print(table)
    console.print(
        "\n[dim]Use: krack-frag-probe run --iface <if> --bssid <mac> --test <name|all>[/dim]"
    )


@cli.command("run")
@click.option(
    "--iface",
    required=True,
    help="Wireless interface (must be monitor mode for live runs).",
)
@click.option(
    "--bssid",
    required=True,
    help="Target AP BSSID (explicit; no auto-scan).",
)
@click.option(
    "--client",
    default=None,
    help="Optional associated client MAC under your control.",
)
@click.option(
    "--test",
    "test_selector",
    default="all",
    show_default=True,
    help="Test name, suite name, or 'all'.",
)
@click.option(
    "--timeout",
    default=3.0,
    show_default=True,
    type=float,
    help="Per-test observation timeout (seconds).",
)
@click.option(
    "--output",
    "output_dir",
    default="./kfp-results",
    show_default=True,
    type=click.Path(),
    help="Directory for JSON/Markdown/HTML reports.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Craft and log frames only; never transmit.",
)
@click.option(
    "--yes-i-understand",
    is_flag=True,
    help="Acknowledge legal warning non-interactively (lab automation).",
)
@click.option(
    "--simulate-regression",
    is_flag=True,
    help="Force FAIL verdicts for training/demo reporting (not a real exploit).",
)
@click.option(
    "--lab-src",
    default="02:00:00:00:00:01",
    show_default=True,
    help="Source MAC used in crafted lab frames.",
)
@click.pass_context
def run_cmd(
    ctx: click.Context,
    iface: str,
    bssid: str,
    client: str | None,
    test_selector: str,
    timeout: float,
    output_dir: str,
    dry_run: bool,
    yes_i_understand: bool,
    simulate_regression: bool,
    lab_src: str,
) -> None:
    """Run regression tests against an explicit lab target.

    **Authorized laboratory use only.** Live runs require monitor mode and
    legal acknowledgement before any frame is sent.
    """
    console: Console = ctx.obj["console"]
    _print_banner(console)

    try:
        # --- Safety gates ---
        require_legal_acknowledgement(pre_accepted=yes_i_understand)
        iface_clean, bssid_norm = require_explicit_targets(iface=iface, bssid=bssid)
        client_norm = validate_mac(client, field="client MAC") if client else None
        lab_src_norm = validate_mac(lab_src, field="lab source MAC")

        if timeout <= 0:
            raise ValidationError("--timeout must be positive.")

        iface_info = ensure_interface_ready(iface_clean, dry_run=dry_run)

        try:
            tests = get_tests(test_selector)
        except KeyError as exc:
            raise ValidationError(str(exc)) from exc

        if not tests:
            raise ValidationError("No tests selected.")

        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        mode = "DRY-RUN" if dry_run else "LIVE LAB"
        console.print(
            f"[bold]Mode:[/bold] {mode}  "
            f"[bold]iface:[/bold] {iface_clean}  "
            f"[bold]BSSID:[/bold] {bssid_norm}  "
            f"[bold]client:[/bold] {client_norm or '—'}  "
            f"[bold]tests:[/bold] {len(tests)}\n"
        )

        summary = RunSummary.create(
            iface=iface_clean,
            bssid=bssid_norm,
            client=client_norm,
            dry_run=dry_run,
            tool_version=__version__,
            interface_details={
                "exists": iface_info.exists,
                "is_monitor": iface_info.is_monitor,
                "source": iface_info.source,
                **iface_info.details,
            },
        )

        tctx = TestContext(
            iface=iface_clean,
            bssid=bssid_norm,
            client=client_norm,
            dry_run=dry_run,
            timeout_s=timeout,
            simulate_regression=simulate_regression,
            interface_info=iface_info,
            verbose=bool(ctx.obj.get("verbose")),
            lab_src=lab_src_norm,
        )

        # Progress lines (run tests individually for live status output)
        for i, test in enumerate(tests, start=1):
            console.print(f"  [{i}/{len(tests)}] Running [cyan]{test.suite}.{test.name}[/cyan] ...")
            result = test.run(tctx)
            summary.add(result)
            color = {
                Verdict.PASS: "green",
                Verdict.FAIL: "red",
                Verdict.INCONCLUSIVE: "yellow",
                Verdict.SKIPPED: "dim",
                Verdict.ERROR: "red",
            }.get(result.verdict, "white")
            console.print(
                f"       [{color}][{result.verdict.value}][/{color}] "
                f"{result.explanation[:120]}" + ("…" if len(result.explanation) > 120 else "")
            )

        # Write reports
        json_path = write_json_report(summary, out_path / "results.json")
        md_path = write_markdown_report(summary, out_path / "report.md")
        html_path = write_html_report(summary, out_path / "report.html")

        _print_summary_table(console, summary)
        console.print(
            f"\nReports written:\n"
            f"  JSON:     {json_path}\n"
            f"  Markdown: {md_path}\n"
            f"  HTML:     {html_path}\n"
        )
        console.print(f"[bold yellow]{LAB_ONLY_BANNER}[/bold yellow]")

        code = summary.exit_code()
        ctx.exit(code)

    except ValidationError as exc:
        console.print(f"[bold red]Configuration / safety error:[/bold red] {exc}")
        ctx.exit(EXIT_CONFIG)
    except click.exceptions.Exit:
        raise
    except Exception as exc:  # noqa: BLE001
        console.print(f"[bold red]Unexpected error:[/bold red] {exc}")
        if ctx.obj.get("verbose"):
            console.print_exception()
        ctx.exit(EXIT_CONFIG)


def _print_summary_table(console: Console, summary: RunSummary) -> None:
    counts = summary.counts
    table = Table(title="Summary", show_header=True, header_style="bold")
    table.add_column("Total")
    table.add_column("PASS", style="green")
    table.add_column("FAIL", style="red")
    table.add_column("INCONCLUSIVE", style="yellow")
    table.add_column("SKIPPED")
    table.add_column("ERROR", style="red")
    table.add_row(
        str(counts.get("total", 0)),
        str(counts.get("PASS", 0)),
        str(counts.get("FAIL", 0)),
        str(counts.get("INCONCLUSIVE", 0)),
        str(counts.get("SKIPPED", 0)),
        str(counts.get("ERROR", 0)),
    )
    console.print()
    console.print(table)

    # Detail table
    detail = Table(title="Per-test verdicts", show_header=True, header_style="bold")
    detail.add_column("Test")
    detail.add_column("Verdict")
    detail.add_column("Seconds")
    for r in summary.results:
        style = {
            Verdict.PASS: "green",
            Verdict.FAIL: "red",
            Verdict.INCONCLUSIVE: "yellow",
            Verdict.ERROR: "red",
        }.get(r.verdict, "")
        detail.add_row(
            f"{r.suite}.{r.name}",
            Text(r.verdict.value, style=style),
            f"{r.duration_s:.3f}",
        )
    console.print(detail)


@cli.command("report")
@click.option(
    "--input",
    "input_path",
    required=True,
    type=click.Path(exists=True, dir_okay=False),
    help="Path to results JSON (or prior log JSON).",
)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["html", "md", "json", "markdown"], case_sensitive=False),
    default="md",
    show_default=True,
    help="Output format. 'pdf' is not built-in; use HTML print-to-PDF.",
)
@click.option(
    "--output",
    "output_path",
    default=None,
    type=click.Path(),
    help="Output file path (default: alongside input with new extension).",
)
@click.pass_context
def report_cmd(
    ctx: click.Context,
    input_path: str,
    fmt: str,
    output_path: str | None,
) -> None:
    """Generate Markdown/HTML/JSON report from a previous results file."""
    console: Console = ctx.obj["console"]
    _print_banner(console)

    try:
        data = load_results_json(input_path)
        in_path = Path(input_path)
        fmt_l = fmt.lower()
        if fmt_l == "markdown":
            fmt_l = "md"

        if fmt_l == "pdf":
            raise ValidationError(
                "Native PDF is not bundled. Generate HTML and print to PDF from a browser."
            )

        if output_path:
            out = Path(output_path)
        else:
            ext = {"md": ".md", "html": ".html", "json": ".json"}[fmt_l]
            out = in_path.with_suffix(ext)

        if fmt_l == "md":
            write_markdown_from_json(data, out)
        elif fmt_l == "html":
            write_html_from_json(data, out)
        elif fmt_l == "json":
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(
                __import__("json").dumps(data, indent=2) + "\n",
                encoding="utf-8",
            )
        else:
            raise ValidationError(f"Unsupported format: {fmt}")

        console.print(f"[green]Report written:[/green] {out}")
        console.print(f"[bold yellow]{LAB_ONLY_BANNER}[/bold yellow]")
        ctx.exit(EXIT_OK)
    except ValidationError as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        ctx.exit(EXIT_CONFIG)
    except click.exceptions.Exit:
        raise
    except Exception as exc:  # noqa: BLE001
        console.print(f"[bold red]Failed to generate report:[/bold red] {exc}")
        ctx.exit(EXIT_CONFIG)


def main(argv: list[str] | None = None) -> int:
    """Console script entry point."""
    try:
        # Click handles sys.argv; standalone_mode=False returns exit code
        result: Any = cli.main(args=argv, prog_name="krack-frag-probe", standalone_mode=False)
        if result is None:
            return EXIT_OK
        if isinstance(result, int):
            return result
        return EXIT_OK
    except click.ClickException as exc:
        exc.show()
        return EXIT_CONFIG
    except click.exceptions.Exit as exc:
        return int(exc.exit_code)
    except ValidationError as exc:
        print(f"Configuration / safety error: {exc}", file=sys.stderr)
        return EXIT_CONFIG
    except SystemExit as exc:
        code = exc.code
        if code is None:
            return EXIT_OK
        if isinstance(code, int):
            return code
        return EXIT_CONFIG
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return EXIT_CONFIG


if __name__ == "__main__":
    sys.exit(main())
