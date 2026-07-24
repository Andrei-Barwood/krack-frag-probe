# Sample lab run

> **LAB ONLY.** Replace MACs with devices you own.

## 1. Dry-run (no RF)

```bash
krack-frag-probe run \
  --iface mon0 \
  --bssid aa:bb:cc:dd:ee:ff \
  --client 02:00:00:00:00:99 \
  --test all \
  --dry-run \
  --yes-i-understand \
  --output ./examples/sample-output
```

Expected: all tests **PASS**, exit code `0`, three report files under
`./examples/sample-output/`.

## 2. Simulated regression (training)

```bash
krack-frag-probe run \
  --iface mon0 \
  --bssid aa:bb:cc:dd:ee:ff \
  --dry-run \
  --yes-i-understand \
  --simulate-regression \
  --output ./examples/sample-output-fail
```

Expected: all tests **FAIL** with `SIMULATED` explanations, exit code `1`.

## 3. Live isolated lab (sketch)

```bash
# mon0 already in monitor mode on your lab channel
sudo krack-frag-probe run \
  --iface mon0 \
  --bssid 00:11:22:33:44:55 \
  --client 66:77:88:99:aa:bb \
  --test key_reinstall \
  --timeout 5 \
  --output ./lab-results-$(date +%Y%m%d)
```

Operator types: `I UNDERSTAND AND ACCEPT`

## 4. Rebuild HTML from JSON

```bash
krack-frag-probe report \
  --input ./examples/sample-output/results.json \
  --format html \
  --output ./examples/sample-output/report-rebuilt.html
```

## Interpreting results

- Clean modern firmware in a correct lab setup: expect **PASS**.
- **FAIL** without `--simulate-regression`: treat as a regression *signal*—
  reproduce, capture traces, contact vendor privately.
- **INCONCLUSIVE**: fix channel/monitor mode/permissions and re-run.

**LAB ONLY – NOT FOR PRODUCTION USE**
