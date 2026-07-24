# Security Policy

## Purpose of this project

**krack-frag-probe** is an **educational, lab-only regression tester**. It checks
whether modern Wi-Fi drivers, chips, and firmware still correctly handle edge
cases related to **already-public, long-patched** issues in the style of KRACK
(key reinstallation) and FragAttacks (fragmentation / aggregation cache
handling).

It is **not** an exploit framework, vulnerability scanner, or attack toolkit.

## What this project will never accept

We will **reject** and **report** contributions that:

- Add working exploitation logic or full attack chains
- Automate real-world attacks against unknown networks
- Enable remote code execution, credential harvesting, or traffic interception
  beyond synthetic test frames
- Remove or weaken legal acknowledgements, monitor-mode checks, or explicit
  target requirements
- Add automated scanning of unknown BSSIDs or “find vulnerable APs” features
- Weaponize the tool for unauthorized use
- Claim discovery of new zero-days

## Supported versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | Yes (security fixes and defensive improvements only) |
| < 1.0   | No                 |

## Reporting security issues in *this* project

If you discover a vulnerability **in krack-frag-probe itself** (e.g. unsafe
defaults, path traversal in report generation, privilege issues):

1. **Do not** open a public GitHub issue.
2. Email the maintainers / author (**Kirtan Teg Singh** / **ਕੀਰਤਨ ਤੇਗ ਸਿੰਘ**)
   at: `security@example.invalid` (replace with project contact when published).
3. Include: description, reproduction steps, impact, and suggested fix if known.
4. Allow reasonable time for a fix before public disclosure.

We aim to acknowledge reports within **7 days** and provide a status update
within **30 days**.

## Reporting misuse

If you observe this software being used for unauthorized attacks, contact the
appropriate law enforcement or CERT organization. Maintainers do not condone
or support illegal use.

## Safe development guidelines

- Never commit live capture files containing third-party traffic without
  redaction and authorization.
- CI must **never** inject frames on live interfaces.
- All packet-sending code paths must go through legal acknowledgement and
  validation gates (`utils/validation.py`, `core/interface.py`).
- Prefer dry-run and unit tests with mocked Scapy layers.

## Dependency security

Report vulnerable dependencies via the same private channel. We use
`pip-audit` / Dependabot-style updates where possible in CI.

## Legal reminder

**Authorized laboratory use only.** Operators must own the target equipment or
have written permission to test it. Misuse may be a criminal offense under
applicable computer crime and wiretap laws.
