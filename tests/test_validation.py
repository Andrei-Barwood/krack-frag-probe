"""Unit tests for validation and legal acknowledgement."""

from __future__ import annotations

import io

import pytest

from krack_frag_probe.utils.validation import (
    LEGAL_ACK_PHRASE,
    ValidationError,
    normalize_mac,
    require_explicit_targets,
    require_legal_acknowledgement,
    validate_mac,
)


@pytest.mark.unit
def test_validate_mac_accepts_colon() -> None:
    assert validate_mac("AA:BB:CC:DD:EE:FF") == "aa:bb:cc:dd:ee:ff"


@pytest.mark.unit
def test_validate_mac_accepts_hyphen_and_compact() -> None:
    assert validate_mac("aa-bb-cc-dd-ee-ff") == "aa:bb:cc:dd:ee:ff"
    assert normalize_mac("aabbccddeeff") == "aa:bb:cc:dd:ee:ff"
    assert validate_mac("aabbccddeeff") == "aa:bb:cc:dd:ee:ff"


@pytest.mark.unit
def test_validate_mac_rejects_empty() -> None:
    with pytest.raises(ValidationError, match="required"):
        validate_mac("")


@pytest.mark.unit
def test_validate_mac_rejects_garbage() -> None:
    with pytest.raises(ValidationError, match="Invalid"):
        validate_mac("not-a-mac")


@pytest.mark.unit
def test_require_explicit_targets() -> None:
    iface, bssid = require_explicit_targets(iface=" mon0 ", bssid="AA:BB:CC:DD:EE:FF")
    assert iface == "mon0"
    assert bssid == "aa:bb:cc:dd:ee:ff"


@pytest.mark.unit
def test_require_explicit_targets_missing_bssid() -> None:
    with pytest.raises(ValidationError, match="BSSID"):
        require_explicit_targets(iface="mon0", bssid=None)


@pytest.mark.unit
def test_require_explicit_targets_missing_iface() -> None:
    with pytest.raises(ValidationError, match="interface"):
        require_explicit_targets(iface="", bssid="aa:bb:cc:dd:ee:ff")


@pytest.mark.unit
def test_legal_ack_success() -> None:
    stdin = io.StringIO(LEGAL_ACK_PHRASE + "\n")
    stdout = io.StringIO()
    require_legal_acknowledgement(stdin=stdin, stdout=stdout)
    assert "LEGAL AND ETHICAL WARNING" in stdout.getvalue()


@pytest.mark.unit
def test_legal_ack_pre_accepted() -> None:
    stdout = io.StringIO()
    require_legal_acknowledgement(pre_accepted=True, stdout=stdout)
    assert "yes-i-understand" in stdout.getvalue().lower()


@pytest.mark.unit
def test_legal_ack_wrong_phrase() -> None:
    stdin = io.StringIO("yes\n")
    stdout = io.StringIO()
    with pytest.raises(ValidationError, match="acknowledgement failed"):
        require_legal_acknowledgement(stdin=stdin, stdout=stdout)
