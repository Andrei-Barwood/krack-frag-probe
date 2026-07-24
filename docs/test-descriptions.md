# Test descriptions (high level)

**Author / ਲੇਖਕ:** **Kirtan Teg Singh** (**ਕੀਰਤਨ ਤੇਗ ਸਿੰਘ**).

> Educational regression checks only. Names refer to **historical issue
> categories**, not working exploits.

## Suite: `key_reinstall`

Related to long-patched KRACK-style key reinstallation / nonce handling.

| Test | What it checks (conceptually) |
| ---- | ----------------------------- |
| `nonce_reuse_guard` | Whether protected-flag / PN-related edge handling still behaves as expected for patched stacks when presented with controlled lab frames (no real key install). |
| `reinstall_edge_install_order` | Ordering smoke probe (plain lab marker then protected edge) related to historical install-order bugs—without a 4-way handshake hijack. |
| `replay_counter_style` | Sequence control smoke including intentional non-monotonic lab sequence to exercise replay/state handling. |

**Not included (intentionally):** full 4-way handshake interception, GTK/PTK
reinstallation attack sequences, decryption oracles.

## Suite: `frag_cache`

Related to long-patched FragAttacks-style fragmentation and aggregation issues.

| Test | What it checks (conceptually) |
| ---- | ----------------------------- |
| `cache_poison_style_probe` | Two-fragment MSDU reassembly path with lab payload markers. |
| `mixed_key_fragment_style` | Mixed Protected-flag fragments (unsafe reassembly should remain rejected). |
| `amsdu_aggregation_probe` | Simplified A-MSDU-like boundary layout with lab markers. |
| `ampdu_delimiter_style_probe` | Lightweight A-MPDU-ish delimiter pattern for aggregation parsing smoke. |

**Not included (intentionally):** cache poisoning against third-party sessions,
plaintext injection into other clients, full multi-stage FragAttacks exploits.

## Suite: `control_mgmt`

Management/control paths that historically interacted with the above.

| Test | What it checks (conceptually) |
| ---- | ----------------------------- |
| `single_deauth_edge` | Exactly one deauth toward the explicit lab target (state edge). Floods unsupported. |
| `action_mgmt_path` | Benign Action frame with lab category/body marker. |
| `probe_request_smoke` | Probe request carrying lab SSID `KFP-LAB-ONLY`. |

## Verdict meanings

| Verdict | Meaning |
| ------- | ------- |
| **PASS** | No historical regression symptom indicated under the controlled probe; craft/observation consistent with expected post-patch behavior. |
| **FAIL** | Regression signal (or `--simulate-regression` demo). Investigate in lab; not automatic proof of a new CVE. |
| **INCONCLUSIVE** | Observation failed or environment insufficient—re-run with better RF isolation/timeout. |
| **ERROR** | Tool/internal failure. |
| **SKIPPED** | Reserved for future selective skip logic. |

## Adding documentation for new tests

When you add a test, document:

1. Historical category (public, long-patched)
2. Frames sent and educational purpose
3. What PASS/FAIL means
4. Explicit statement that it is not an exploit chain
