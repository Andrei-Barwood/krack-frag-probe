"""Input validation and mandatory legal acknowledgement gates.

All executable paths that could send frames must call
:func:`require_legal_acknowledgement` and supply an explicit target MAC.
"""

from __future__ import annotations

import re
import sys
from typing import TextIO

# Exact phrase the operator must type (case-sensitive).
LEGAL_ACK_PHRASE = "I UNDERSTAND AND ACCEPT"

_MAC_RE = re.compile(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$")


class ValidationError(Exception):
    """Raised when configuration or safety checks fail (CLI exit code 2)."""


def validate_mac(value: str, *, field: str = "MAC") -> str:
    """Validate and normalize a MAC address.

    Parameters
    ----------
    value:
        Operator-supplied MAC string.
    field:
        Human-readable field name for error messages.

    Returns
    -------
    str
        Canonical lowercase colon-separated MAC.

    Raises
    ------
    ValidationError
        If the value is empty or not a valid unicast/multicast MAC format.
    """
    if value is None or not str(value).strip():
        raise ValidationError(
            f"{field} is required. You must explicitly supply the target address. "
            "Automated discovery of unknown networks is intentionally unsupported."
        )
    normalized = normalize_mac(value)
    if not _MAC_RE.match(normalized):
        raise ValidationError(f"Invalid {field}: {value!r}. Expected format aa:bb:cc:dd:ee:ff.")
    return normalized


def normalize_mac(value: str) -> str:
    """Normalize MAC separators and case to ``aa:bb:cc:dd:ee:ff``."""
    raw = value.strip().lower().replace("-", ":").replace(".", ":")
    # Support compact form aabbccddeeff
    if ":" not in raw and len(raw) == 12 and all(c in "0123456789abcdef" for c in raw):
        raw = ":".join(raw[i : i + 2] for i in range(0, 12, 2))
    return raw


LEGAL_WARNING = """
================================================================================
  LEGAL AND ETHICAL WARNING — READ CAREFULLY
================================================================================

  krack-frag-probe is an EDUCATIONAL, LAB-ONLY regression tester.

  You may use it ONLY on wireless equipment that:
    • YOU OWN, or
    • YOU HAVE WRITTEN PERMISSION to test.

  Unauthorized testing of third-party networks or devices may violate criminal
  and civil law, including computer crime and wiretap statutes.

  This tool:
    • Does NOT implement working exploitation chains
    • Does NOT scan for unknown networks
    • Does NOT harvest credentials or execute remote code
    • Does NOT claim to find new zero-days
    • ONLY checks regression of known, long-patched edge-case behaviors

  By proceeding you accept full legal responsibility for your actions.

  Type exactly the following phrase to continue (or cancel with Ctrl-C):

      I UNDERSTAND AND ACCEPT

================================================================================
""".strip()


def require_legal_acknowledgement(
    *,
    pre_accepted: bool = False,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
) -> None:
    """Display the multi-line legal warning and require explicit acceptance.

    Parameters
    ----------
    pre_accepted:
        If True, the operator passed ``--yes-i-understand``. The full warning
        is still printed; interactive prompt is skipped (scripted lab runs).
    stdin, stdout:
        Streams for testing; default to ``sys.stdin`` / ``sys.stdout``.

    Raises
    ------
    ValidationError
        If the operator does not type the exact acknowledgement phrase.
    """
    out = stdout if stdout is not None else sys.stdout
    inp = stdin if stdin is not None else sys.stdin

    print(LEGAL_WARNING, file=out, flush=True)

    if pre_accepted:
        print(
            "\n[--yes-i-understand] Acknowledgement flag accepted for this lab session.\n",
            file=out,
            flush=True,
        )
        return

    try:
        response = inp.readline()
    except KeyboardInterrupt as exc:
        raise ValidationError("Legal acknowledgement cancelled by operator.") from exc

    if response is None:
        raise ValidationError("Legal acknowledgement required; no input received.")

    if response.strip() != LEGAL_ACK_PHRASE:
        raise ValidationError(
            f"Legal acknowledgement failed. You must type exactly: {LEGAL_ACK_PHRASE!r}"
        )

    print("\nAcknowledgement recorded for this session.\n", file=out, flush=True)


def require_explicit_targets(*, iface: str | None, bssid: str | None) -> tuple[str, str]:
    """Hard gate: refuse to proceed without interface and BSSID.

    Returns normalized ``(iface, bssid)``.
    """
    if not iface or not str(iface).strip():
        raise ValidationError(
            "Wireless interface (--iface) is required. "
            "The tool will not guess or auto-select an interface."
        )
    if not bssid or not str(bssid).strip():
        raise ValidationError(
            "Target BSSID (--bssid) is required. "
            "The tool will not scan for or select unknown networks."
        )
    iface_clean = str(iface).strip()
    bssid_norm = validate_mac(bssid, field="BSSID")
    return iface_clean, bssid_norm
