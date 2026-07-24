"""Minimal educational 802.11 frame construction.

Author: Kirtan Teg Singh (ਕੀਰਤਨ ਤੇਗ ਸਿੰਘ)

IMPORTANT
---------
Frames built here are **synthetic regression probes**, not exploit chains.
They are intentionally limited to the minimum structure needed to exercise
historical edge-case *handling* on a lab target under operator control.

No full handshake hijacks, no decryption oracles, no credential theft, and
no multi-stage attack automation are implemented or permitted.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import IntEnum
from typing import Any

logger = logging.getLogger("krack_frag_probe.frame_builder")

try:
    from scapy.layers.dot11 import (
        Dot11,
        Dot11Deauth,
        Dot11Elt,
        Dot11ProbeReq,
        RadioTap,
    )
    from scapy.packet import Packet, Raw

    SCAPY_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised in environments without scapy
    SCAPY_AVAILABLE = False
    Packet = Any  # type: ignore[misc, assignment]
    Raw = Any  # type: ignore[misc, assignment]


class FCType(IntEnum):
    """802.11 frame control type field (educational reference)."""

    MANAGEMENT = 0
    CONTROL = 1
    DATA = 2


class FCSubtypeMgmt(IntEnum):
    """Subset of management subtypes used in lab probes."""

    PROBE_REQ = 4
    BEACON = 8
    DEAUTH = 12
    ACTION = 13


@dataclass(frozen=True, slots=True)
class BuiltFrame:
    """A crafted frame plus educational metadata (no secrets)."""

    name: str
    purpose: str
    packet: Any
    summary: str
    bytes_len: int

    def hex_preview(self, limit: int = 32) -> str:
        try:
            raw = bytes(self.packet)[:limit]
            return raw.hex()
        except Exception:  # noqa: BLE001
            return "<unavailable>"


def _require_scapy() -> None:
    if not SCAPY_AVAILABLE:
        raise RuntimeError("Scapy is required for frame crafting. Install with: pip install scapy")


def build_lab_data_probe(
    *,
    bssid: str,
    src: str,
    dst: str,
    payload: bytes,
    frag: int = 0,
    seq: int = 1,
    to_ds: int = 0,
    from_ds: int = 1,
    more_frag: int = 0,
    protected: int = 0,
    name: str = "lab_data_probe",
    purpose: str = "Minimal data-frame style probe for regression observation",
) -> BuiltFrame:
    """Craft a single 802.11 data frame with controlled FC flags.

    Educational purpose
    -------------------
    Historical fragmentation and key-install issues interacted with data-frame
    flags (fragment number, More Fragments, Protected). This builder sets those
    fields **explicitly and minimally** so a lab operator can observe whether a
    patched stack still handles them correctly.

    This is **not** a reinstallation attack: we do not complete or hijack a
    4-way handshake, do not install keys, and do not decrypt traffic.
    """
    _require_scapy()

    # Dot11 SC: fragment in low 4 bits, sequence in upper 12 bits
    sc = ((seq & 0x0FFF) << 4) | (frag & 0x0F)

    dot11 = Dot11(
        type=FCType.DATA,
        subtype=0,  # Data
        FCfield=(
            (0x01 if to_ds else 0)
            | (0x02 if from_ds else 0)
            | (0x04 if more_frag else 0)
            | (0x40 if protected else 0)
        ),
        addr1=dst,
        addr2=src,
        addr3=bssid,
        SC=sc,
    )
    pkt = RadioTap() / dot11 / Raw(load=payload)
    summary = (
        f"Data probe name={name} bssid={bssid} src={src} dst={dst} "
        f"frag={frag} seq={seq} more_frag={more_frag} protected={protected} "
        f"payload_len={len(payload)}"
    )
    logger.debug("Built frame: %s", summary)
    return BuiltFrame(
        name=name,
        purpose=purpose,
        packet=pkt,
        summary=summary,
        bytes_len=len(bytes(pkt)),
    )


def build_fragment_pair(
    *,
    bssid: str,
    src: str,
    dst: str,
    body: bytes,
    seq: int = 7,
    name_prefix: str = "frag_pair",
) -> list[BuiltFrame]:
    """Build two consecutive fragments of one MSDU (educational only).

    Historical FragAttacks-style issues involved incorrect reassembly or cache
    handling of fragments. We send **two benign fragments** with consistent
    sequence control so a lab stack's reassembly path can be exercised—not to
    inject attacker payloads into other clients' traffic.
    """
    if len(body) < 2:
        body = body + b"\x00\x00"
    mid = len(body) // 2
    part1, part2 = body[:mid], body[mid:]

    f0 = build_lab_data_probe(
        bssid=bssid,
        src=src,
        dst=dst,
        payload=part1,
        frag=0,
        seq=seq,
        more_frag=1,
        name=f"{name_prefix}.frag0",
        purpose=(
            "First fragment (More Fragments=1). Exercises reassembly start path "
            "for regression of historical cache mishandling — not an exploit."
        ),
    )
    f1 = build_lab_data_probe(
        bssid=bssid,
        src=src,
        dst=dst,
        payload=part2,
        frag=1,
        seq=seq,
        more_frag=0,
        name=f"{name_prefix}.frag1",
        purpose=(
            "Second fragment completing the MSDU. Used only to verify reassembly "
            "edge handling remains correct on patched firmware/drivers."
        ),
    )
    return [f0, f1]


def build_amsdu_style_probe(
    *,
    bssid: str,
    src: str,
    dst: str,
    inner_marker: bytes = b"KFP-LAB-AMSDU",
    name: str = "amsdu_style_probe",
) -> BuiltFrame:
    """Craft a data frame whose payload mimics A-MSDU-like structure (lab only).

    Educational purpose
    -------------------
    Historical aggregation parsing flaws mishandled A-MSDU boundaries. We place
    a **clear lab marker** and a simplified multi-subframe-like layout so
    parsers can be regression-tested. No attack against third-party traffic.
    """
    # Simplified educational layout: length-prefixed subframes with lab markers.
    # Not a full IEEE-compliant A-MSDU generator — sufficient for regression probes.
    sub1 = inner_marker + b"-SUB1"
    sub2 = inner_marker + b"-SUB2"
    payload = (
        len(sub1).to_bytes(2, "big")
        + sub1
        + len(sub2).to_bytes(2, "big")
        + sub2
        + b"\x00\x00"  # padding marker
    )
    return build_lab_data_probe(
        bssid=bssid,
        src=src,
        dst=dst,
        payload=payload,
        frag=0,
        seq=11,
        name=name,
        purpose=(
            "A-MSDU-style aggregation parsing probe with lab markers. "
            "Checks that historical aggregation boundary bugs remain fixed."
        ),
    )


def build_protected_flag_edge(
    *,
    bssid: str,
    src: str,
    dst: str,
    name: str = "protected_flag_edge",
) -> BuiltFrame:
    """Data frame with Protected bit set and non-cryptographic lab payload.

    Educational purpose
    -------------------
    Key-install edge cases historically interacted with the Protected flag and
    PN/nonce handling. We set Protected=1 with an **obvious non-encrypted lab
    payload** so observers can see whether the stack rejects/handles the edge
    safely. We do **not** perform key reinstallation or forge valid CCMP.
    """
    payload = b"KFP-LAB-PROTECTED-EDGE\x00\x01\x02\x03"
    return build_lab_data_probe(
        bssid=bssid,
        src=src,
        dst=dst,
        payload=payload,
        frag=0,
        seq=3,
        protected=1,
        name=name,
        purpose=(
            "Protected-flag edge probe without real crypto. Validates that "
            "patched stacks do not exhibit historical key/nonce mishandling "
            "symptoms when presented with malformed protected frames."
        ),
    )


def build_mgmt_action_probe(
    *,
    bssid: str,
    src: str,
    dst: str,
    name: str = "mgmt_action_probe",
) -> BuiltFrame:
    """Minimal Action management frame toward the lab BSSID.

    Educational purpose
    -------------------
    Some historical issues interacted with management/action processing paths.
    This frame is a **benign Action shell** with a lab category/body marker.
    """
    _require_scapy()
    # Category 127 (vendor-specific reserved range usage as lab marker) + body
    action_body = bytes([127, 0x4B, 0x46, 0x50]) + b"LAB-ACTION"  # KFP marker
    # Use raw Dot11 management subtype Action
    dot11 = Dot11(
        type=FCType.MANAGEMENT,
        subtype=FCSubtypeMgmt.ACTION,
        addr1=dst,
        addr2=src,
        addr3=bssid,
    )
    pkt = RadioTap() / dot11 / Raw(load=action_body)
    summary = f"Action mgmt probe name={name} bssid={bssid} dst={dst}"
    return BuiltFrame(
        name=name,
        purpose=(
            "Benign Action management frame for control-path regression. "
            "Not a deauth flood or association hijack."
        ),
        packet=pkt,
        summary=summary,
        bytes_len=len(bytes(pkt)),
    )


def build_deauth_single(
    *,
    bssid: str,
    dst: str,
    src: str | None = None,
    reason: int = 1,
    name: str = "single_deauth_edge",
) -> BuiltFrame:
    """Craft **exactly one** deauthentication management frame.

    Educational purpose
    -------------------
    Control/management edge cases historically interacted with state machines
    that also handled key install and fragment caches. We allow a **single**
    deauth for lab isolation tests — never a flood, never automated against
    unknown stations.

    Policy: callers must already have passed legal acknowledgement and
    explicit target validation.
    """
    _require_scapy()
    sa = src if src is not None else bssid
    pkt = (
        RadioTap()
        / Dot11(
            type=FCType.MANAGEMENT,
            subtype=FCSubtypeMgmt.DEAUTH,
            addr1=dst,
            addr2=sa,
            addr3=bssid,
        )
        / Dot11Deauth(reason=reason)
    )
    summary = f"Single deauth (lab) name={name} bssid={bssid} dst={dst} reason={reason}"
    return BuiltFrame(
        name=name,
        purpose=(
            "Single deauthentication frame for state-machine edge observation. "
            "Not a denial-of-service tool; floods are intentionally unsupported."
        ),
        packet=pkt,
        summary=summary,
        bytes_len=len(bytes(pkt)),
    )


def build_probe_request_lab(
    *,
    bssid: str,
    src: str,
    ssid: str = "KFP-LAB-ONLY",
    name: str = "lab_probe_request",
) -> BuiltFrame:
    """Probe request with lab SSID marker (management path smoke test)."""
    _require_scapy()
    pkt = (
        RadioTap()
        / Dot11(
            type=FCType.MANAGEMENT,
            subtype=FCSubtypeMgmt.PROBE_REQ,
            addr1="ff:ff:ff:ff:ff:ff",
            addr2=src,
            addr3=bssid,
        )
        / Dot11ProbeReq()
        / Dot11Elt(ID="SSID", info=ssid.encode("utf-8"))
    )
    summary = f"ProbeReq lab marker ssid={ssid!r} bssid={bssid}"
    return BuiltFrame(
        name=name,
        purpose="Benign probe request with lab SSID for mgmt-path regression smoke test.",
        packet=pkt,
        summary=summary,
        bytes_len=len(bytes(pkt)),
    )


def describe_frame(built: BuiltFrame) -> dict[str, Any]:
    """Serialize educational metadata for reports (no raw secrets)."""
    return {
        "name": built.name,
        "purpose": built.purpose,
        "summary": built.summary,
        "bytes_len": built.bytes_len,
        "hex_preview": built.hex_preview(),
    }
