# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-23

### Added

- Initial public release of **krack-frag-probe**, an educational lab-only
  regression tester for long-patched Wi-Fi edge cases (KRACK-style key
  reinstallation and FragAttacks-style fragmentation/aggregation handling).
- CLI entry points: `krack-frag-probe` and `python -m krack_frag_probe`.
- Subcommands: `list-tests`, `run`, `report`, `acknowledge` helpers via run flow.
- Mandatory legal acknowledgement (`I UNDERSTAND AND ACCEPT`) before any
  non-dry-run transmission.
- Hard gates: monitor-mode interface check; explicit BSSID (and optional client
  MAC) required.
- Test suites:
  - `key_reinstall` — nonce / key-install edge-case regression probes
  - `frag_cache` — fragmentation / A-MSDU / A-MPDU cache handling regression probes
  - `control_mgmt` — control and management frame edge cases historically
    related to the above
- Reporting: JSON, Markdown, optional HTML with lab-only banners.
- Structured logging (console + JSON lines).
- Dry-run mode for development without hardware.
- Documentation: README, lab-setup, ethics, architecture, test descriptions.
- Optional experimental report viewer script (Tkinter).
- Unit tests, GitHub Actions CI (lint, mypy, pytest — no live injection).
- MIT license, SECURITY.md, CODE_OF_CONDUCT.md, CONTRIBUTING.md.

### Safety notes

- No exploitation logic, no automated scanning of unknown networks, no
  credential harvesting, no RCE.
- Tool is for authorized laboratory use only.
