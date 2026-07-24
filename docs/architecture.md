# Architecture

## Design principles

1. **Safety before features** — legal ack, explicit targets, monitor-mode gate.
2. **Minimal frames** — no full attack chains.
3. **Deterministic verdicts** — PASS / FAIL / INCONCLUSIVE / SKIPPED / ERROR.
4. **Modular suites** — easy to add educational regression checks.
5. **No live injection in CI** — unit tests mock Scapy where needed.

## Package layout

```
src/krack_frag_probe/
  cli.py                 # Click CLI + Rich UI
  core/
    interface.py         # Monitor-mode probe (iw/sysfs)
    frame_builder.py     # Scapy frame craft + educational metadata
    tester.py            # RegressionTest ABC, TestRunner, send/observe
    results.py           # TestResult, RunSummary, Verdict
  testsuites/
    key_reinstall.py     # KRACK-style edge regression
    frag_cache.py        # FragAttacks-style cache/aggregation
    control_mgmt.py      # Mgmt/control path edges
  reporting/
    json_report.py
    markdown_report.py
    html_report.py
  utils/
    validation.py        # MAC + legal acknowledgement
    logging.py           # Console + JSON lines
```

## Execution flow (`run`)

```
CLI parse
  → print banner
  → require_legal_acknowledgement()
  → require_explicit_targets(iface, bssid)
  → ensure_interface_ready(monitor unless dry-run)
  → load tests from registry
  → for each test:
        craft() → send()/dry-run log → observe() → evaluate()
  → write JSON + Markdown + HTML
  → exit 0/1/2
```

## Adding a new regression suite safely

1. Create `testsuites/my_suite.py` with classes subclassing `RegressionTest`.
2. Implement `craft(ctx) -> list[BuiltFrame]` using `frame_builder` helpers or
   carefully commented Scapy layers.
3. Prefer the default `evaluate()` unless you have a **non-exploitative**
   observation criterion.
4. Register tests in `testsuites/__init__.py` `SUITE_REGISTRY`.
5. Document in `docs/test-descriptions.md`.
6. Add unit tests that never open a live interface.
7. PR description must explain educational purpose and why the frames are minimal.

### Template

```python
from dataclasses import dataclass
from krack_frag_probe.core.frame_builder import BuiltFrame, build_lab_data_probe
from krack_frag_probe.core.tester import RegressionTest, TestContext

@dataclass
class MyProbe(RegressionTest):
    def craft(self, ctx: TestContext) -> list[BuiltFrame]:
        return [build_lab_data_probe(
            bssid=ctx.bssid,
            src=ctx.lab_src,
            dst=ctx.target_dst,
            payload=b"KFP-LAB-MY-PROBE",
            name="my_probe",
            purpose="Educational regression for <historical category>.",
        )]
```

## Observation model

Live observation is **count-only / presence-oriented**, not an exploit oracle.
Dry-run treats successful craft as PASS (unless `--simulate-regression`).
This keeps the tool defensive: it does not automate “break this AP” workflows.

## Reporting

All formats embed:

- Timestamp, iface, BSSID, client
- Per-test verdict + diagnostics
- **LAB ONLY – NOT FOR PRODUCTION USE** banner

## Threat model (of the tool itself)

We defend against:

- Accidental use without acknowledgement
- Accidental TX on non-monitor interfaces
- Implicit target discovery
- Contribution of weaponized code (process + CODE_OF_CONDUCT)

We do **not** attempt to make misuse impossible (root users can always craft
packets); we make legitimate lab use clear and misuse friction high.
