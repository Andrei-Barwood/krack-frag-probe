"""Unit tests for interface probing (no real hardware required)."""

from __future__ import annotations

import pytest

from krack_frag_probe.core.interface import InterfaceInfo, ensure_interface_ready, probe_interface
from krack_frag_probe.utils.validation import ValidationError


@pytest.mark.unit
def test_interface_info_dry_run_allows_non_monitor() -> None:
    info = InterfaceInfo(
        name="wlan0",
        exists=True,
        is_monitor=False,
        details={},
        source="test",
    )
    info.require_monitor_for_live(dry_run=True)  # must not raise


@pytest.mark.unit
def test_interface_info_live_requires_monitor() -> None:
    info = InterfaceInfo(
        name="wlan0",
        exists=True,
        is_monitor=False,
        details={"type": "managed"},
        source="test",
    )
    with pytest.raises(ValidationError, match="monitor"):
        info.require_monitor_for_live(dry_run=False)


@pytest.mark.unit
def test_interface_info_live_requires_exists() -> None:
    info = InterfaceInfo(name="mon9", exists=False, is_monitor=False)
    with pytest.raises(ValidationError, match="not found"):
        info.require_monitor_for_live(dry_run=False)


@pytest.mark.unit
def test_probe_dry_run_missing_iface() -> None:
    # Should not raise on dry-run even if iface missing
    info = probe_interface("this_iface_should_not_exist_kfp_999", dry_run=True)
    assert info.name == "this_iface_should_not_exist_kfp_999"
    # dry-run path always returns without raising
    ensure_interface_ready("this_iface_should_not_exist_kfp_999", dry_run=True)


@pytest.mark.unit
def test_ensure_live_missing_raises() -> None:
    with pytest.raises(ValidationError):
        ensure_interface_ready("this_iface_should_not_exist_kfp_999", dry_run=False)
