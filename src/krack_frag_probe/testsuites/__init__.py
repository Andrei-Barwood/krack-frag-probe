"""Registry of modular regression test suites.

Author: Kirtan Teg Singh (ਕੀਰਤਨ ਤੇਗ ਸਿੰਘ)

All suites are educational checks for long-patched behaviors.
"""

from __future__ import annotations

from krack_frag_probe.core.tester import RegressionTest
from krack_frag_probe.testsuites.control_mgmt import CONTROL_MGMT_TESTS
from krack_frag_probe.testsuites.frag_cache import FRAG_CACHE_TESTS
from krack_frag_probe.testsuites.key_reinstall import KEY_REINSTALL_TESTS

# Suite name -> list of tests
SUITE_REGISTRY: dict[str, list[RegressionTest]] = {
    "key_reinstall": list(KEY_REINSTALL_TESTS),
    "frag_cache": list(FRAG_CACHE_TESTS),
    "control_mgmt": list(CONTROL_MGMT_TESTS),
}


def all_tests() -> list[RegressionTest]:
    """Return every registered regression test in stable order."""
    tests: list[RegressionTest] = []
    for suite_name in sorted(SUITE_REGISTRY.keys()):
        tests.extend(SUITE_REGISTRY[suite_name])
    return tests


def get_tests(selector: str) -> list[RegressionTest]:
    """Resolve ``all``, suite name, or fully-qualified / short test name.

    Parameters
    ----------
    selector:
        ``all``, a suite key (e.g. ``key_reinstall``), a test name
        (e.g. ``nonce_reuse_guard``), or ``suite.test`` form.
    """
    sel = selector.strip().lower()
    if sel in ("", "all", "*"):
        return all_tests()

    if sel in SUITE_REGISTRY:
        return list(SUITE_REGISTRY[sel])

    # Exact full name or suffix match
    matched: list[RegressionTest] = []
    for t in all_tests():
        full = f"{t.suite}.{t.name}".lower()
        if sel == full or sel == t.name.lower():
            matched.append(t)
    if matched:
        return matched

    available = [f"{t.suite}.{t.name}" for t in all_tests()]
    raise KeyError(f"Unknown test or suite {selector!r}. Available: {', '.join(available)}")


def list_suite_info(*, verbose: bool = False) -> list[dict[str, str]]:
    """Metadata for ``list-tests`` command."""
    rows: list[dict[str, str]] = []
    for t in all_tests():
        row = {
            "name": t.name,
            "suite": t.suite,
            "full_name": f"{t.suite}.{t.name}",
            "description": t.description,
        }
        if verbose:
            row["historical_category"] = t.historical_category
        rows.append(row)
    return rows


__all__ = [
    "SUITE_REGISTRY",
    "all_tests",
    "get_tests",
    "list_suite_info",
]
