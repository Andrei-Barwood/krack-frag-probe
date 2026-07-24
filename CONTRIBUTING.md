# Contributing to krack-frag-probe

Thank you for helping improve this **educational, lab-only** regression tester.

## Before you contribute

1. Read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) and [SECURITY.md](SECURITY.md).
2. Read [docs/ethics-and-warnings.md](docs/ethics-and-warnings.md).
3. Accept that **weaponization, exploit chains, and unauthorized targeting features
   will be rejected**.

## What we welcome

- Bug fixes and safer error handling
- Improved documentation and lab setup guides
- Additional **regression** tests for *already-public, long-patched* behaviors,
  with clear educational documentation
- Better reporting formats, accessibility, and test coverage
- Packaging, typing, and CI improvements

## What we reject

- Working exploit logic or “full attack chains”
- Automated scanning of unknown networks
- Credential harvesting, RCE payloads, or traffic interception beyond synthetic
  test frames
- Removal or bypass of legal acknowledgement / monitor-mode / explicit-target
  gates
- Claims of discovering new zero-days via this tool

## Development setup

```bash
git clone https://github.com/example/krack-frag-probe.git
cd krack-frag-probe
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
make check   # lint + typecheck + unit tests
```

## Adding a new regression test suite

1. Create a module under `src/krack_frag_probe/testsuites/`.
2. Subclass `RegressionTest` (see `core/tester.py`) or register via the suite
   registry in `testsuites/__init__.py`.
3. Document:
   - Which **historical, public** issue style is being regression-checked
   - What frames are sent and **why** (educational purpose only)
   - Expected PASS / FAIL / INCONCLUSIVE criteria
4. Keep frame construction **minimal** — only what is needed to elicit the
   historical symptom under lab control.
5. Add unit tests with **mocked** Scapy; never require live injection in CI.
6. Update `docs/test-descriptions.md` and the CHANGELOG.

See [docs/architecture.md](docs/architecture.md) for design details.

## Code standards

- Python 3.11+
- Type hints on public APIs; `mypy --strict` friendly where practical
- Docstrings on modules, classes, and public functions
- Ruff for lint/format; pytest for tests
- No live packet injection in automated tests

## Commit and PR process

1. Open an issue first for non-trivial design changes.
2. Keep PRs focused and small.
3. Ensure `make check` passes.
4. In the PR description, explicitly state how the change remains defensive and
   educational.

## Legal

By contributing, you agree that your contributions are licensed under the MIT
License, and that you will not submit material intended for unauthorized or
malicious use.
