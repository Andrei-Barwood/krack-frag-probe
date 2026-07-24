"""Unit tests for suite registry and dry-run execution (no live TX)."""

from __future__ import annotations

import pytest

from krack_frag_probe.core.interface import InterfaceInfo
from krack_frag_probe.core.results import RunSummary
from krack_frag_probe.core.tester import TestContext, TestRunner
from krack_frag_probe.testsuites import SUITE_REGISTRY, all_tests, get_tests, list_suite_info


@pytest.mark.unit
def test_registry_nonempty() -> None:
    assert "key_reinstall" in SUITE_REGISTRY
    assert "frag_cache" in SUITE_REGISTRY
    assert "control_mgmt" in SUITE_REGISTRY
    tests = all_tests()
    assert len(tests) >= 8
    names = {f"{t.suite}.{t.name}" for t in tests}
    assert "key_reinstall.nonce_reuse_guard" in names
    assert "frag_cache.cache_poison_style_probe" in names


@pytest.mark.unit
def test_get_tests_selectors() -> None:
    assert len(get_tests("all")) == len(all_tests())
    assert len(get_tests("key_reinstall")) == len(SUITE_REGISTRY["key_reinstall"])
    one = get_tests("nonce_reuse_guard")
    assert len(one) == 1
    assert one[0].name == "nonce_reuse_guard"
    with pytest.raises(KeyError):
        get_tests("not_a_real_test_xyz")


@pytest.mark.unit
def test_list_suite_info() -> None:
    rows = list_suite_info(verbose=True)
    assert all("description" in r for r in rows)
    assert any("historical_category" in r for r in rows)


def _ctx(*, simulate: bool = False) -> TestContext:
    return TestContext(
        iface="mon0",
        bssid="aa:bb:cc:dd:ee:ff",
        client="02:00:00:00:00:99",
        dry_run=True,
        timeout_s=0.1,
        simulate_regression=simulate,
        interface_info=InterfaceInfo(
            name="mon0",
            exists=False,
            is_monitor=False,
            details={"note": "unit"},
            source="test",
        ),
    )


@pytest.mark.unit
def test_dry_run_all_pass() -> None:
    summary = RunSummary.create(
        iface="mon0",
        bssid="aa:bb:cc:dd:ee:ff",
        client=None,
        dry_run=True,
        tool_version="1.0.0",
    )
    runner = TestRunner(tests=all_tests())
    runner.run_all(_ctx(simulate=False), summary)
    assert summary.counts["total"] == len(all_tests())
    assert summary.counts["PASS"] == len(all_tests())
    assert summary.exit_code() == 0


@pytest.mark.unit
def test_simulate_regression_all_fail() -> None:
    summary = RunSummary.create(
        iface="mon0",
        bssid="aa:bb:cc:dd:ee:ff",
        client=None,
        dry_run=True,
        tool_version="1.0.0",
    )
    runner = TestRunner(tests=get_tests("frag_cache"))
    runner.run_all(_ctx(simulate=True), summary)
    assert summary.counts["FAIL"] == len(get_tests("frag_cache"))
    assert all("SIMULATED" in r.explanation for r in summary.results)
    assert summary.exit_code() == 1


@pytest.mark.unit
def test_craft_produces_frames() -> None:
    ctx = _ctx()
    for t in all_tests():
        frames = t.craft(ctx)
        assert isinstance(frames, list)
        assert len(frames) >= 1
        for fr in frames:
            assert fr.bytes_len > 0
            assert fr.purpose  # educational purpose required
