"""Wireless interface handling for Linux mac80211 monitor mode.

Hard-coded safety: refuse live injection unless the interface exists and is
in monitor mode. Dry-run may proceed with a synthetic interface description.
"""

from __future__ import annotations

import logging
import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from krack_frag_probe.utils.validation import ValidationError

logger = logging.getLogger("krack_frag_probe.interface")


@dataclass(slots=True)
class InterfaceInfo:
    """Snapshot of wireless interface state relevant to lab injection."""

    name: str
    exists: bool
    is_monitor: bool
    details: dict[str, Any] = field(default_factory=dict)
    source: str = "unknown"

    def require_monitor_for_live(self, *, dry_run: bool) -> None:
        """Raise ValidationError if live run cannot proceed safely."""
        if dry_run:
            return
        if not self.exists:
            raise ValidationError(
                f"Interface {self.name!r} not found. "
                "Create/enable a monitor-mode interface before live runs. "
                "See docs/lab-setup.md. Use --dry-run without hardware."
            )
        if not self.is_monitor:
            raise ValidationError(
                f"Interface {self.name!r} is not in monitor mode "
                f"(details={self.details!r}). "
                "Hard-coded policy: refuse to send frames unless type is monitor. "
                "See docs/lab-setup.md."
            )


def _read_sysfs_type(iface: str) -> str | None:
    """Best-effort sysfs type read (not always present for wireless)."""
    path = Path(f"/sys/class/net/{iface}/type")
    try:
        if path.is_file():
            return path.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return None


def _iface_exists(iface: str) -> bool:
    return Path(f"/sys/class/net/{iface}").exists() or Path(f"/sys/class/net/{iface}").is_symlink()


def _parse_iw_info(text: str) -> dict[str, Any]:
    """Parse subset of ``iw dev <iface> info`` output."""
    info: dict[str, Any] = {"raw_excerpt": text[:500]}
    type_m = re.search(r"^\s*type\s+(\S+)", text, re.MULTILINE | re.IGNORECASE)
    if type_m:
        info["type"] = type_m.group(1).lower()
    wiphy_m = re.search(r"^\s*wiphy\s+(\d+)", text, re.MULTILINE | re.IGNORECASE)
    if wiphy_m:
        info["wiphy"] = int(wiphy_m.group(1))
    channel_m = re.search(r"channel\s+(\d+)\s+\(([\d.]+\s*MHz)\)", text, re.IGNORECASE)
    if channel_m:
        info["channel"] = channel_m.group(1)
        info["frequency"] = channel_m.group(2)
    return info


def _run_iw_info(iface: str) -> tuple[bool, dict[str, Any]]:
    """Run ``iw dev IFACE info``; return (ok, details)."""
    try:
        proc = subprocess.run(
            ["iw", "dev", iface, "info"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except FileNotFoundError:
        return False, {"error": "iw command not found"}
    except subprocess.TimeoutExpired:
        return False, {"error": "iw command timed out"}
    except OSError as exc:
        return False, {"error": str(exc)}

    if proc.returncode != 0:
        return False, {
            "error": "iw failed",
            "stderr": (proc.stderr or "")[:300],
            "returncode": proc.returncode,
        }
    return True, _parse_iw_info(proc.stdout or "")


def probe_interface(iface: str, *, dry_run: bool = False) -> InterfaceInfo:
    """Inspect *iface* and determine monitor-mode status.

    On non-Linux or when sysfs/iw are unavailable:
    - dry_run: return a synthetic OK description
    - live: raise ValidationError

    Parameters
    ----------
    iface:
        Interface name supplied by the operator (never auto-selected).
    dry_run:
        If True, missing hardware is tolerated.
    """
    if not iface or not str(iface).strip():
        raise ValidationError("Interface name is required.")

    name = str(iface).strip()

    # Non-Linux: only dry-run is allowed for "live" semantics
    if os.name != "posix" or not Path("/sys/class/net").exists():
        if dry_run:
            return InterfaceInfo(
                name=name,
                exists=False,
                is_monitor=False,
                details={
                    "note": "Non-Linux or no sysfs; dry-run only",
                    "platform": os.name,
                },
                source="synthetic-dry-run",
            )
        raise ValidationError(
            "Live packet injection requires Linux with mac80211 monitor mode. "
            "Use --dry-run on this platform, or run from a lab Linux host."
        )

    exists = _iface_exists(name)
    if not exists:
        if dry_run:
            return InterfaceInfo(
                name=name,
                exists=False,
                is_monitor=False,
                details={"note": "Interface missing; dry-run proceeds without TX"},
                source="sysfs-missing-dry-run",
            )
        return InterfaceInfo(
            name=name,
            exists=False,
            is_monitor=False,
            details={"sysfs": "missing"},
            source="sysfs",
        )

    ok, iw_details = _run_iw_info(name)
    details: dict[str, Any] = {"sysfs_type": _read_sysfs_type(name)}
    if ok:
        details.update(iw_details)
        is_monitor = str(details.get("type", "")).lower() == "monitor"
        return InterfaceInfo(
            name=name,
            exists=True,
            is_monitor=is_monitor,
            details=details,
            source="iw",
        )

    # Fallback: if iw missing, refuse live (cannot prove monitor mode)
    details.update(iw_details)
    if dry_run:
        return InterfaceInfo(
            name=name,
            exists=True,
            is_monitor=False,
            details={**details, "note": "Could not verify monitor mode; dry-run OK"},
            source="fallback-dry-run",
        )
    return InterfaceInfo(
        name=name,
        exists=True,
        is_monitor=False,
        details={
            **details,
            "policy": "Refuse live run when monitor mode cannot be verified via iw",
        },
        source="unverified",
    )


def ensure_interface_ready(iface: str, *, dry_run: bool) -> InterfaceInfo:
    """Probe interface and enforce monitor-mode policy for live runs."""
    info = probe_interface(iface, dry_run=dry_run)
    info.require_monitor_for_live(dry_run=dry_run)
    logger.debug(
        "Interface ready: %s exists=%s monitor=%s dry_run=%s source=%s",
        info.name,
        info.exists,
        info.is_monitor,
        dry_run,
        info.source,
    )
    return info
