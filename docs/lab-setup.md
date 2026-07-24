# Laboratory setup guide

> **AUTHORIZED LABORATORY USE ONLY.**  
> Configure monitor mode and RF isolation **only** for equipment you own or have
> written permission to test. Never point this tool at production or third-party
> networks without authorization.

## Goals

1. Provide a **controlled RF environment** (ideally Faraday cage, shielded room,
   or isolated lab channel with no bystander networks of concern).
2. Put a Linux wireless NIC into **monitor mode** for optional live injection.
3. Identify **exact** BSSID / client MACs of devices under your control.
4. Run `krack-frag-probe` with legal acknowledgement and capture reports.

## Legal checklist (before any live TX)

- [ ] Written authorization or ownership documented for every target
- [ ] Lab RF isolation or permission for the channel in use
- [ ] No accidental targeting of guest/neighbor networks
- [ ] Operators trained on ethics policy (`docs/ethics-and-warnings.md`)

## Hardware

- Linux host (recommended: recent Debian/Ubuntu/Fedora)
- Wi-Fi adapter with **mac80211** driver and monitor + injection support
  - Common chipsets: Atheros ath9k_htc, some MediaTek, some Ralink (verify yours)
- Access Point and/or client **you own** for regression testing

## Software packages

### Debian / Ubuntu

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip \
  iw wireless-tools net-tools rfkill aircrack-ng
```

### Fedora

```bash
sudo dnf install -y python3.11 iw wireless-tools aircrack-ng
```

## Enabling monitor mode

### Method A — `iw` (preferred)

```bash
# Identify interface
ip link
iw dev

# Example: physical iface wlan0
sudo rfkill unblock wifi
sudo ip link set wlan0 down
sudo iw dev wlan0 set type monitor
sudo ip link set wlan0 up
# Optionally set channel used by your lab AP
sudo iw dev wlan0 set channel 6

iw dev wlan0 info   # type must show: monitor
```

You may rename for clarity:

```bash
sudo ip link set wlan0 name mon0
```

### Method B — `airmon-ng`

```bash
sudo airmon-ng check kill   # careful: stops NetworkManager temporarily
sudo airmon-ng start wlan0
# Creates mon0 or wlan0mon depending on version
iw dev
```

Restore managed mode after lab work:

```bash
sudo ip link set mon0 down
sudo iw dev mon0 set type managed
sudo ip link set mon0 up
# or: sudo airmon-ng stop mon0
sudo systemctl restart NetworkManager   # if stopped
```

## Verifying injection capability (optional)

Use vendor or community tools **only on your lab AP**, e.g. Scapy one-liner or
`aireplay-ng --test` against **your** BSSID. Do not “test” random networks.

## Running krack-frag-probe

```bash
cd krack-frag-probe
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e .

# Dry-run first (no hardware required)
krack-frag-probe run \
  --iface mon0 \
  --bssid aa:bb:cc:dd:ee:ff \
  --dry-run \
  --yes-i-understand

# Live lab run (monitor mode required)
sudo krack-frag-probe run \
  --iface mon0 \
  --bssid 00:11:22:33:44:55 \
  --client 66:77:88:99:aa:bb \
  --test all \
  --timeout 5 \
  --output ./lab-results
```

Type `I UNDERSTAND AND ACCEPT` when prompted (unless `--yes-i-understand` after
you have read the full warning).

## Isolation recommendations

- Prefer indoor lab AP on a fixed channel with known empty spectrum.
- Disable production SSIDs on the same radio during tests.
- Document BSSID/MAC allow-list for the session.
- Store reports offline; redact if sharing publicly.

## Troubleshooting

| Symptom | Likely cause | Action |
| ------- | ------------ | ------ |
| “not in monitor mode” | Interface still managed | `iw dev IFACE set type monitor` |
| “Interface not found” | Wrong name | `iw dev` / `ip link` |
| Permission denied | Needs CAP_NET_RAW/root | `sudo` in lab only |
| INCONCLUSIVE results | Sniff failed / RF quiet | Increase `--timeout`, check channel |
| Scapy import errors | Missing dep | `pip install scapy` |

## What this lab setup does **not** authorize

- Testing coffee-shop, airport, neighbor, or customer networks
- Automated scanning for “vulnerable” BSSIDs
- Using the tool as a penetration weapon outside written scope

**LAB ONLY – NOT FOR PRODUCTION USE**
