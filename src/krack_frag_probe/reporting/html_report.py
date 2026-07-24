"""Optional HTML report with basic styling and lab-only banner."""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any

from krack_frag_probe.core.results import RunSummary, Verdict
from krack_frag_probe.reporting.json_report import summary_from_dict

_CSS = """
:root { --bg: #0f1419; --fg: #e7ecf1; --muted: #8b9bab; --card: #1a2332;
        --pass: #3dd68c; --fail: #f07178; --inc: #ffcc66; --err: #ff8f40;
        --banner: #5c1a1a; --accent: #59c2ff; }
* { box-sizing: border-box; }
body { font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
       background: var(--bg); color: var(--fg); margin: 0; padding: 0 0 3rem; line-height: 1.5; }
.banner { background: var(--banner); color: #fff; padding: 1rem 1.5rem; font-weight: 700;
          text-align: center; border-bottom: 3px solid #f07178; letter-spacing: 0.02em; }
.wrap { max-width: 960px; margin: 0 auto; padding: 1.5rem; }
h1 { font-size: 1.6rem; margin: 0 0 0.25rem; }
.sub { color: var(--muted); margin-bottom: 1.5rem; }
.card { background: var(--card); border-radius: 10px; padding: 1rem 1.25rem;
        margin-bottom: 1rem; border: 1px solid #2a3544; }
table { width: 100%; border-collapse: collapse; }
th, td { text-align: left; padding: 0.45rem 0.6rem; border-bottom: 1px solid #2a3544; }
th { color: var(--muted); font-weight: 600; font-size: 0.85rem; }
.badge { display: inline-block; padding: 0.15rem 0.55rem; border-radius: 999px;
         font-size: 0.8rem; font-weight: 700; letter-spacing: 0.04em; }
.PASS { background: rgba(61,214,140,.15); color: var(--pass); }
.FAIL { background: rgba(240,113,120,.15); color: var(--fail); }
.INCONCLUSIVE { background: rgba(255,204,102,.15); color: var(--inc); }
.SKIPPED { background: rgba(139,155,171,.15); color: var(--muted); }
.ERROR { background: rgba(255,143,64,.15); color: var(--err); }
.meta { color: var(--muted); font-size: 0.9rem; }
footer { color: var(--muted); font-size: 0.85rem; margin-top: 2rem; text-align: center; }
code { background: #0b1016; padding: 0.1rem 0.35rem; border-radius: 4px; color: var(--accent); }
"""


def _badge(verdict: str) -> str:
    v = html.escape(verdict)
    return f'<span class="badge {v}">{v}</span>'


def render_html(summary: RunSummary) -> str:
    counts = summary.counts
    rows = []
    for r in summary.results:
        notes = "".join(f"<li><code>{html.escape(n)}</code></li>" for n in r.diagnostic_notes)
        notes_html = f"<ul>{notes}</ul>" if notes else "—"
        rows.append(
            f"""
            <tr>
              <td><code>{html.escape(r.suite)}.{html.escape(r.name)}</code></td>
              <td>{_badge(r.verdict.value)}</td>
              <td>{r.duration_s:.3f}s</td>
              <td>{r.frames_crafted}/{r.frames_sent}</td>
              <td>{html.escape(r.explanation)}</td>
              <td class="meta">{notes_html}</td>
            </tr>
            """
        )

    iface = html.escape(str(summary.interface_details))
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>krack-frag-probe Lab Report</title>
  <style>{_CSS}</style>
</head>
<body>
  <div class="banner">LAB ONLY – NOT FOR PRODUCTION USE · NOT AN EXPLOIT REPORT</div>
  <div class="wrap">
    <h1>krack-frag-probe Lab Report</h1>
    <p class="sub">Educational regression results for long-patched Wi-Fi edge cases.
    Authorized laboratory use only.</p>

    <div class="card">
      <h2>Run metadata</h2>
      <table>
        <tr><th>Timestamp (UTC)</th><td><code>{html.escape(summary.timestamp)}</code></td></tr>
        <tr><th>Tool version</th><td><code>{html.escape(summary.tool_version)}</code></td></tr>
        <tr><th>Interface</th><td><code>{html.escape(summary.iface)}</code></td></tr>
        <tr><th>Target BSSID</th><td><code>{html.escape(summary.bssid)}</code></td></tr>
        <tr><th>Client MAC</th><td><code>{html.escape(summary.client or "—")}</code></td></tr>
        <tr><th>Dry-run</th><td><code>{summary.dry_run}</code></td></tr>
        <tr><th>Interface details</th><td class="meta">{iface}</td></tr>
      </table>
      <p class="meta">{html.escape(summary.operator_notes)}</p>
    </div>

    <div class="card">
      <h2>Summary</h2>
      <table>
        <tr>
          <th>Total</th><th>PASS</th><th>FAIL</th><th>INCONCLUSIVE</th><th>SKIPPED</th><th>ERROR</th>
        </tr>
        <tr>
          <td>{counts.get("total", 0)}</td>
          <td>{counts.get(Verdict.PASS.value, 0)}</td>
          <td>{counts.get(Verdict.FAIL.value, 0)}</td>
          <td>{counts.get(Verdict.INCONCLUSIVE.value, 0)}</td>
          <td>{counts.get(Verdict.SKIPPED.value, 0)}</td>
          <td>{counts.get(Verdict.ERROR.value, 0)}</td>
        </tr>
      </table>
    </div>

    <div class="card">
      <h2>Per-test results</h2>
      <table>
        <tr>
          <th>Test</th><th>Verdict</th><th>Duration</th><th>Crafted/Sent</th>
          <th>Explanation</th><th>Diagnostics</th>
        </tr>
        {"".join(rows)}
      </table>
    </div>

    <footer>
      krack-frag-probe · defensive educational regression tester ·
      LAB ONLY – NOT FOR PRODUCTION USE · no zero-day claims
    </footer>
  </div>
</body>
</html>
"""


def write_html_report(summary: RunSummary, path: Path | str) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_html(summary), encoding="utf-8")
    return out


def write_html_from_json(data: dict[str, Any], path: Path | str) -> Path:
    return write_html_report(summary_from_dict(data), path)
