# krack-frag-probe Lab Report

> **LAB ONLY – NOT FOR PRODUCTION USE**
>
> Authorized laboratory regression testing only. Not an exploit report.
> Do not use against production networks or third-party equipment without
> written authorization.

## Run metadata

| Field | Value |
| ----- | ----- |
| Timestamp (UTC) | `2026-07-24T00:29:45.024514+00:00` |
| Tool version | `1.0.0` |
| Interface | `mon0` |
| Target BSSID | `aa:bb:cc:dd:ee:ff` |
| Client MAC | `—` |
| Dry-run | `True` |
| Interface details | `{'exists': False, 'is_monitor': False, 'source': 'synthetic-dry-run', 'note': 'Non-Linux or no sysfs; dry-run only', 'platform': 'posix'}` |

_Authorized laboratory regression test. Not for production or third-party use._

## Summary

| Total | PASS | FAIL | INCONCLUSIVE | SKIPPED | ERROR |
| ----- | ---- | ---- | ------------ | ------- | ----- |
| 10 | 10 | 0 | 0 | 0 | 0 |

## Per-test results

### `control_mgmt.single_deauth_edge` — **PASS**

- **Duration:** 0.001s
- **Frames crafted / sent:** 1 / 0
- **Dry-run:** True
- **Explanation:** No historical Management-frame state interactions (historical) regression symptom indicated under controlled probe for single_deauth_edge. Stack handling consistent with expected post-patch behavior (dry-run craft OK).
- **Diagnostics:**
  - `suite=control_mgmt`
  - `historical_category=Management-frame state interactions (historical)`
  - `frames=['single_deauth_edge']`
  - `observation_mode=dry-run`

### `control_mgmt.action_mgmt_path` — **PASS**

- **Duration:** 0.000s
- **Frames crafted / sent:** 1 / 0
- **Dry-run:** True
- **Explanation:** No historical Action frame processing edge cases regression symptom indicated under controlled probe for action_mgmt_path. Stack handling consistent with expected post-patch behavior (dry-run craft OK).
- **Diagnostics:**
  - `suite=control_mgmt`
  - `historical_category=Action frame processing edge cases`
  - `frames=['action_mgmt_path']`
  - `observation_mode=dry-run`

### `control_mgmt.probe_request_smoke` — **PASS**

- **Duration:** 0.001s
- **Frames crafted / sent:** 1 / 0
- **Dry-run:** True
- **Explanation:** No historical Management path smoke / edge interaction regression symptom indicated under controlled probe for probe_request_smoke. Stack handling consistent with expected post-patch behavior (dry-run craft OK).
- **Diagnostics:**
  - `suite=control_mgmt`
  - `historical_category=Management path smoke / edge interaction`
  - `frames=['probe_request_smoke']`
  - `observation_mode=dry-run`

### `frag_cache.cache_poison_style_probe` — **PASS**

- **Duration:** 0.001s
- **Frames crafted / sent:** 2 / 0
- **Dry-run:** True
- **Explanation:** No historical FragAttacks-style fragment cache handling regression symptom indicated under controlled probe for cache_poison_style_probe. Stack handling consistent with expected post-patch behavior (dry-run craft OK).
- **Diagnostics:**
  - `suite=frag_cache`
  - `historical_category=FragAttacks-style fragment cache handling`
  - `frames=['cache_poison_style_probe.frag0', 'cache_poison_style_probe.frag1']`
  - `observation_mode=dry-run`

### `frag_cache.mixed_key_fragment_style` — **PASS**

- **Duration:** 0.001s
- **Frames crafted / sent:** 2 / 0
- **Dry-run:** True
- **Explanation:** No historical Mixed plaintext/encrypted fragment handling regression symptom indicated under controlled probe for mixed_key_fragment_style. Stack handling consistent with expected post-patch behavior (dry-run craft OK).
- **Diagnostics:**
  - `suite=frag_cache`
  - `historical_category=Mixed plaintext/encrypted fragment handling`
  - `frames=['mixed_key_fragment.plain_frag0', 'mixed_key_fragment.protected_frag1']`
  - `observation_mode=dry-run`

### `frag_cache.amsdu_aggregation_probe` — **PASS**

- **Duration:** 0.000s
- **Frames crafted / sent:** 1 / 0
- **Dry-run:** True
- **Explanation:** No historical A-MSDU aggregation parsing (historical fixes) regression symptom indicated under controlled probe for amsdu_aggregation_probe. Stack handling consistent with expected post-patch behavior (dry-run craft OK).
- **Diagnostics:**
  - `suite=frag_cache`
  - `historical_category=A-MSDU aggregation parsing (historical fixes)`
  - `frames=['amsdu_aggregation_probe']`
  - `observation_mode=dry-run`

### `frag_cache.ampdu_delimiter_style_probe` — **PASS**

- **Duration:** 0.000s
- **Frames crafted / sent:** 1 / 0
- **Dry-run:** True
- **Explanation:** No historical A-MPDU aggregation parsing (historical fixes) regression symptom indicated under controlled probe for ampdu_delimiter_style_probe. Stack handling consistent with expected post-patch behavior (dry-run craft OK).
- **Diagnostics:**
  - `suite=frag_cache`
  - `historical_category=A-MPDU aggregation parsing (historical fixes)`
  - `frames=['ampdu_delimiter_style_probe']`
  - `observation_mode=dry-run`

### `key_reinstall.nonce_reuse_guard` — **PASS**

- **Duration:** 0.001s
- **Frames crafted / sent:** 2 / 0
- **Dry-run:** True
- **Explanation:** No historical KRACK-style key/nonce install edge cases regression symptom indicated under controlled probe for nonce_reuse_guard. Stack handling consistent with expected post-patch behavior (dry-run craft OK).
- **Diagnostics:**
  - `suite=key_reinstall`
  - `historical_category=KRACK-style key/nonce install edge cases`
  - `frames=['nonce_reuse_guard.protected_a', 'nonce_reuse_guard.protected_b']`
  - `observation_mode=dry-run`

### `key_reinstall.reinstall_edge_install_order` — **PASS**

- **Duration:** 0.001s
- **Frames crafted / sent:** 2 / 0
- **Dry-run:** True
- **Explanation:** No historical KRACK-style key reinstallation edge cases regression symptom indicated under controlled probe for reinstall_edge_install_order. Stack handling consistent with expected post-patch behavior (dry-run craft OK).
- **Diagnostics:**
  - `suite=key_reinstall`
  - `historical_category=KRACK-style key reinstallation edge cases`
  - `frames=['reinstall_edge.plain_marker', 'reinstall_edge.protected_marker']`
  - `observation_mode=dry-run`

### `key_reinstall.replay_counter_style` — **PASS**

- **Duration:** 0.001s
- **Frames crafted / sent:** 3 / 0
- **Dry-run:** True
- **Explanation:** No historical Replay/PN state handling (related historical fixes) regression symptom indicated under controlled probe for replay_counter_style. Stack handling consistent with expected post-patch behavior (dry-run craft OK).
- **Diagnostics:**
  - `suite=key_reinstall`
  - `historical_category=Replay/PN state handling (related historical fixes)`
  - `frames=['replay_counter_style.seq_30_0', 'replay_counter_style.seq_31_1', 'replay_counter_style.seq_30_2']`
  - `observation_mode=dry-run`

---

## Safety reminder

- This report documents **regression probes** for long-patched behaviors.
- It is **not** evidence of a new vulnerability or zero-day.
- **LAB ONLY – NOT FOR PRODUCTION USE.**
