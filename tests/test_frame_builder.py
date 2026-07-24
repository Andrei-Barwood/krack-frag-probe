"""Unit tests for educational frame builders (require scapy)."""

from __future__ import annotations

import pytest

from krack_frag_probe.core.frame_builder import (
    SCAPY_AVAILABLE,
    build_amsdu_style_probe,
    build_fragment_pair,
    build_lab_data_probe,
    build_protected_flag_edge,
    describe_frame,
)

pytestmark = pytest.mark.skipif(not SCAPY_AVAILABLE, reason="scapy not installed")


@pytest.mark.unit
def test_lab_data_probe_bytes() -> None:
    fr = build_lab_data_probe(
        bssid="aa:bb:cc:dd:ee:ff",
        src="02:00:00:00:00:01",
        dst="aa:bb:cc:dd:ee:ff",
        payload=b"KFP-LAB",
        frag=1,
        seq=5,
        more_frag=1,
    )
    assert fr.bytes_len > 0
    assert "frag=1" in fr.summary
    assert b"KFP-LAB" in bytes(fr.packet)
    meta = describe_frame(fr)
    assert meta["name"] == "lab_data_probe"
    assert "hex_preview" in meta


@pytest.mark.unit
def test_fragment_pair() -> None:
    frames = build_fragment_pair(
        bssid="aa:bb:cc:dd:ee:ff",
        src="02:00:00:00:00:01",
        dst="aa:bb:cc:dd:ee:ff",
        body=b"ABCDEFGH",
        seq=7,
    )
    assert len(frames) == 2
    assert "frag0" in frames[0].name
    assert "frag1" in frames[1].name
    assert "reassembly" in frames[0].purpose.lower() or "fragment" in frames[0].purpose.lower()


@pytest.mark.unit
def test_amsdu_and_protected() -> None:
    a = build_amsdu_style_probe(
        bssid="aa:bb:cc:dd:ee:ff",
        src="02:00:00:00:00:01",
        dst="aa:bb:cc:dd:ee:ff",
    )
    p = build_protected_flag_edge(
        bssid="aa:bb:cc:dd:ee:ff",
        src="02:00:00:00:00:01",
        dst="aa:bb:cc:dd:ee:ff",
    )
    assert b"KFP-LAB-AMSDU" in bytes(a.packet)
    assert b"KFP-LAB-PROTECTED" in bytes(p.packet)
    assert "not" in p.purpose.lower() or "without real crypto" in p.purpose.lower()
