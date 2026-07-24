# krack-frag-probe

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ⚠  AUTHORIZED LABORATORY USE ONLY — NOT FOR PRODUCTION NETWORKS  ⚠        ║
║                                                                              ║
║   This tool must ONLY be used on Wi-Fi equipment that YOU OWN or for which  ║
║   you have WRITTEN PERMISSION to test. Unauthorized testing may violate     ║
║   criminal and civil law (computer crime, wiretap, and related statutes).   ║
║                                                                              ║
║   This is a DEFENSIVE REGRESSION TESTER for long-patched, publicly          ║
║   documented Wi-Fi edge cases. It is NOT an exploit kit, NOT a scanner,     ║
║   and does NOT discover zero-days.                                           ║
║                                                                              ║
║   By running this software you accept full responsibility for lawful use.   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**krack-frag-probe** is an educational regression tester that checks for residual
or re-introduced *symptoms* of already-publicly-patched Wi-Fi issues:

- **KRACK-style** key reinstallation / nonce-reuse edge cases (historical)
- **FragAttacks-style** fragmentation and aggregation cache handling (historical)

It crafts a **minimal** set of carefully controlled 802.11 test frames (via
[Scapy](https://scapy.net/)) toward a **user-specified** Access Point or client
that is under the operator’s exclusive physical and administrative control.

> **Bold requirement:** The tool is for **authorized laboratory use only** on
> equipment the operator owns or has written permission to test.

---

## What this tool is (and is not)

| This tool **is** | This tool is **not** |
| ---------------- | -------------------- |
| A lab regression checker for long-patched behaviors | An exploit framework |
| Educational documentation of historical edge cases | A zero-day discovery tool |
| Operator-driven (explicit iface + BSSID required) | An automated network scanner |
| Useful for vendors validating new driver/firmware stacks | A credential harvester or MITM toolkit |

No remote code execution, no credential harvesting, no traffic interception
beyond synthetic test frames, and no automated scanning of unknown networks.

---

## Features

- **Mandatory legal acknowledgement** before any non-dry-run packet send
- **Hard gates:** monitor-mode interface + explicit target BSSID/MAC
- Modular test suites: key-reinstall, fragmentation/cache, control/management
- Deterministic verdicts: `PASS` / `FAIL` / `INCONCLUSIVE` with explanations
- Structured logging (console + JSON lines)
- Reports: JSON, Markdown, HTML — all with lab-only banners
- **Dry-run mode** for development without hardware
- Optional experimental local report viewer (Tkinter)
- Typed Python 3.11+, mypy-friendly, pytest + CI (no live injection in CI)

---

## Requirements

- **Python 3.11+**
- **Linux** with a wireless NIC capable of **monitor mode** (mac80211) for live runs
- Root or `CAP_NET_RAW` / appropriate capabilities for injection (lab hosts only)
- [Scapy](https://scapy.net/), [Click](https://click.palletsprojects.com/), [Rich](https://rich.readthedocs.io/)

macOS/Windows are supported for `list-tests`, `report`, and `--dry-run` only.
Live injection targets Linux monitor-mode interfaces.

---

## Installation

```bash
# Clone
git clone https://github.com/example/krack-frag-probe.git
cd krack-frag-probe

# Virtual environment (recommended)
python3.11 -m venv .venv
source .venv/bin/activate

# Install
pip install -e ".[dev]"

# Or via pipx for isolated CLI
pipx install .
```

Verify:

```bash
krack-frag-probe --help
python -m krack_frag_probe list-tests
```

### Monitor-mode setup (lab hosts)

See **[docs/lab-setup.md](docs/lab-setup.md)** for distro-specific steps. Sketch:

```bash
# Example — replace wlan0 / mon0 as appropriate
sudo ip link set wlan0 down
sudo iw dev wlan0 set type monitor
sudo ip link set wlan0 up
# or: sudo airmon-ng start wlan0
```

Confirm:

```bash
iw dev mon0 info   # type must be "monitor"
```

---

## Quick start (lab only)

### 1. Dry-run (no hardware, no packets)

```bash
krack-frag-probe run \
  --iface mon0 \
  --bssid aa:bb:cc:dd:ee:ff \
  --test all \
  --dry-run \
  --yes-i-understand
```

### 2. Live lab run

```bash
# You MUST own the AP/client or have written permission.
sudo krack-frag-probe run \
  --iface mon0 \
  --bssid 00:11:22:33:44:55 \
  --client aa:bb:cc:dd:ee:01 \
  --test all \
  --timeout 5 \
  --output ./lab-results
```

You will be prompted to type exactly:

```text
I UNDERSTAND AND ACCEPT
```

(or pass `--yes-i-understand` only after you have read the full legal warning).

### 3. List tests

```bash
krack-frag-probe list-tests
krack-frag-probe list-tests --verbose
```

### 4. Generate reports from a previous run

```bash
krack-frag-probe report \
  --input ./lab-results/results.json \
  --format html \
  --output ./lab-results/report.html
```

---

## CLI reference

| Command | Purpose |
| ------- | ------- |
| `list-tests` | Enumerate regression test suites and individual tests |
| `run` | Execute tests against an explicit lab target |
| `report` | Rebuild Markdown/HTML/JSON views from a results file |

### `run` options

| Flag | Description |
| ---- | ----------- |
| `--iface` | Wireless interface (**required**; must be monitor mode for live runs) |
| `--bssid` | Target AP BSSID (**required**) |
| `--client` | Optional associated client MAC |
| `--test` | Test name, suite name, or `all` (default: `all`) |
| `--timeout` | Per-test observation timeout in seconds (default: 3) |
| `--output` | Directory for JSON/MD/HTML artifacts |
| `--dry-run` | Craft and log frames only; never transmit |
| `--yes-i-understand` | Skip interactive prompt after acknowledging risk (scripted labs) |
| `--verbose` / `-v` | Verbose logging |
| `--json` | Emit JSON lines on stdout |
| `--no-color` | Disable ANSI colors |
| `--simulate-regression` | **Lab training only:** force FAIL verdicts to demo reporting |

### Exit codes

| Code | Meaning |
| ---- | ------- |
| `0` | All executed tests passed |
| `1` | One or more failures / regressions detected |
| `2` | Configuration, permission, or validation error |

---

## Sample expected output

### Clean modern firmware (PASS)

```text
LAB ONLY – NOT FOR PRODUCTION USE
Target BSSID: 00:11:22:33:44:55  iface: mon0  mode: live

  [PASS] key_reinstall.nonce_reuse_guard
         No historical nonce-reuse symptom observed under controlled probe.
  [PASS] key_reinstall.reinstall_edge_install_order
         Key install edge handling consistent with post-patch behavior.
  [PASS] frag_cache.cache_poison_style_probe
         Fragmentation cache handling consistent with patched stacks.
  ...

┌──────────────────────────── Summary ────────────────────────────┐
│ Total: 9   PASS: 9   FAIL: 0   INCONCLUSIVE: 0                  │
└─────────────────────────────────────────────────────────────────┘
```

### Simulated regression (training / CI demo)

```bash
krack-frag-probe run --iface mon0 --bssid aa:bb:cc:dd:ee:ff \
  --dry-run --yes-i-understand --simulate-regression
```

```text
  [FAIL] key_reinstall.nonce_reuse_guard
         SIMULATED: historical nonce-reuse style symptom would be flagged.
  ...
Exit code: 1
```

---

## Architecture (overview)

```
src/krack_frag_probe/
  cli.py              # Click CLI, legal gate, progress UI
  core/
    interface.py      # Monitor-mode detection & validation
    frame_builder.py  # Minimal educational 802.11 frame craft
    tester.py         # Suite runner & observation logic
    results.py        # Verdict model & aggregation
  testsuites/         # Modular regression suites
  reporting/          # JSON / Markdown / HTML
  utils/              # Logging, MAC validation, legal text
```

To add a safe new suite, see [docs/architecture.md](docs/architecture.md) and
[CONTRIBUTING.md](CONTRIBUTING.md).

---

## Documentation

| Document | Content |
| -------- | ------- |
| [docs/lab-setup.md](docs/lab-setup.md) | Monitor mode, RF isolation, legal lab practices |
| [docs/ethics-and-warnings.md](docs/ethics-and-warnings.md) | Ethics, law, misuse prohibition |
| [docs/architecture.md](docs/architecture.md) | Design and extension guide |
| [docs/test-descriptions.md](docs/test-descriptions.md) | What each test checks (high level) |
| [examples/sample-lab-run.md](examples/sample-lab-run.md) | End-to-end lab example |
| [SECURITY.md](SECURITY.md) | Security policy & anti-weaponization |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Community standards |

---

## Development

```bash
make install-dev
make check          # ruff + mypy + pytest
make dry-run        # full dry-run without hardware
```

CI runs linting, type checking, and unit tests **without** live packet injection.

---

## Optional report viewer (experimental)

```bash
python scripts/generate_report_viewer.py ./lab-results/report.html
```

Requires a desktop Python with Tkinter. Marked **experimental**.

---

## License

MIT — see [LICENSE](LICENSE).

The license does **not** grant permission to violate the law. Authorized lab use
only.

---

## Acknowledgments

Historical public research on key reinstallation (KRACK) and fragmentation
attacks (FragAttacks) informed the *categories* of regression checks. This
project does **not** reimplement public exploits; it only probes whether
patched stacks still reject the historical edge cases under controlled lab
conditions.

---

```
LAB ONLY – NOT FOR PRODUCTION USE
NO EXPLOITATION · NO SCANNING OF UNKNOWN NETWORKS · NO ZERO-DAY CLAIMS
```
