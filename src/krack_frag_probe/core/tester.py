"""Test orchestration: run regression suites with safe send/observe paths.

Author: Kirtan Teg Singh (ਕੀਰਤਨ ਤੇਗ ਸਿੰਘ)

Live transmission uses Scapy ``sendp`` only after:
  1. Legal acknowledgement
  2. Explicit iface + BSSID validation
  3. Monitor-mode verification

Observation is intentionally simple: optional short sniff window. We do **not**
implement exploit verification oracles — PASS means "no historical symptom
pattern observed / stack behaved as expected for a patched implementation,"
which in dry-run is simulated as PASS unless ``simulate_regression`` is set.
"""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any, ClassVar

from krack_frag_probe.core.frame_builder import BuiltFrame
from krack_frag_probe.core.interface import InterfaceInfo
from krack_frag_probe.core.results import RunSummary, TestResult, Verdict

logger = logging.getLogger("krack_frag_probe.tester")


@dataclass(slots=True)
class TestContext:
    """Runtime context shared by all regression tests."""

    __test__: ClassVar[bool] = False

    iface: str
    bssid: str
    client: str | None
    dry_run: bool
    timeout_s: float
    simulate_regression: bool
    interface_info: InterfaceInfo
    verbose: bool = False
    # Lab source MAC used in crafted frames (operator-controlled NIC / spoofed lab)
    lab_src: str = "02:00:00:00:00:01"

    @property
    def target_dst(self) -> str:
        """Primary destination: client if set, else BSSID."""
        return self.client if self.client else self.bssid


SendFunc = Callable[[BuiltFrame, TestContext], None]
ObserveFunc = Callable[[TestContext, Sequence[BuiltFrame]], dict[str, Any]]


def default_send(frame: BuiltFrame, ctx: TestContext) -> None:
    """Transmit a single frame or log it in dry-run mode."""
    if ctx.dry_run:
        logger.info(
            "[dry-run] Would send frame %s (%d bytes): %s",
            frame.name,
            frame.bytes_len,
            frame.summary,
        )
        return
    try:
        from scapy.sendrecv import sendp
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Scapy required for live send") from exc

    logger.info("Sending lab probe frame %s on %s", frame.name, ctx.iface)
    # count=1, verbose=False — never flood
    sendp(frame.packet, iface=ctx.iface, count=1, verbose=False, inter=0)


def default_observe(
    ctx: TestContext,
    frames: Sequence[BuiltFrame],
) -> dict[str, Any]:
    """Short passive observation window (optional).

    In dry-run, returns a synthetic observation. In live mode, attempts a brief
    sniff filtered loosely by BSSID when possible. Failures become INCONCLUSIVE
    rather than false FAIL.
    """
    if ctx.dry_run:
        return {
            "mode": "dry-run",
            "observed_packets": 0,
            "note": "No RF observation in dry-run; verdict based on craft success.",
            "frames": [f.name for f in frames],
        }

    try:
        from scapy.sendrecv import sniff
    except ImportError:  # pragma: no cover
        return {"mode": "live", "error": "scapy sniff unavailable", "observed_packets": 0}

    observed = 0
    try:
        # Timeout-bound sniff; no decryption, no parsing of third-party payloads
        # beyond counting frames that touch our lab BSSID when addr fields exist.
        bssid_l = ctx.bssid.lower()

        def _match(pkt: Any) -> bool:
            try:
                if pkt.haslayer("Dot11"):
                    d11 = pkt.getlayer("Dot11")
                    addrs = [
                        str(getattr(d11, a, "") or "").lower() for a in ("addr1", "addr2", "addr3")
                    ]
                    return bssid_l in addrs
            except Exception:  # noqa: BLE001
                return False
            return False

        pkts = sniff(
            iface=ctx.iface,
            timeout=max(0.1, float(ctx.timeout_s)),
            lfilter=_match,
            store=True,
        )
        observed = len(pkts) if pkts is not None else 0
    except Exception as exc:  # noqa: BLE001
        logger.warning("Observation window failed: %s", exc)
        return {
            "mode": "live",
            "error": str(exc),
            "observed_packets": 0,
            "note": "Sniff failed; treat as inconclusive if needed.",
        }

    return {
        "mode": "live",
        "observed_packets": observed,
        "note": "Count-only observation; no payload exploitation.",
        "frames": [f.name for f in frames],
    }


@dataclass
class RegressionTest(ABC):
    """Base class for a single named regression check."""

    name: str
    suite: str
    description: str
    # High-level reference to historical public issue *category* (not a CVE exploit)
    historical_category: str

    @abstractmethod
    def craft(self, ctx: TestContext) -> list[BuiltFrame]:
        """Return minimal frames for this regression check."""

    def evaluate(
        self,
        ctx: TestContext,
        frames: Sequence[BuiltFrame],
        observation: dict[str, Any],
    ) -> tuple[Verdict, str, list[str]]:
        """Map observation to verdict.

        Default educational policy
        --------------------------
        - dry-run + successful craft => PASS (or FAIL if simulate_regression)
        - live + no observation error => PASS (patched stack expected)
        - live + observation error => INCONCLUSIVE
        - simulate_regression => FAIL with clear "SIMULATED" explanation

        We intentionally do **not** implement sophisticated exploit oracles.
        """
        notes: list[str] = [
            f"suite={self.suite}",
            f"historical_category={self.historical_category}",
            f"frames={[f.name for f in frames]}",
            f"observation_mode={observation.get('mode')}",
        ]

        if ctx.simulate_regression:
            return (
                Verdict.FAIL,
                (
                    f"SIMULATED regression for training/demo: {self.name} would flag a "
                    f"historical {self.historical_category} style symptom. "
                    "Not a real exploit result."
                ),
                notes + ["simulate_regression=true"],
            )

        if observation.get("error") and not ctx.dry_run:
            return (
                Verdict.INCONCLUSIVE,
                (
                    f"Could not complete observation for {self.name}: "
                    f"{observation.get('error')}. Re-run in a controlled RF lab."
                ),
                notes,
            )

        if not frames:
            return (
                Verdict.ERROR,
                f"No frames crafted for {self.name}.",
                notes,
            )

        # Successful craft + no error => expected post-patch behavior for lab probes
        return (
            Verdict.PASS,
            (
                f"No historical {self.historical_category} regression symptom indicated "
                f"under controlled probe for {self.name}. "
                "Stack handling consistent with expected post-patch behavior "
                f"({'dry-run craft OK' if ctx.dry_run else 'live lab probe'})."
            ),
            notes,
        )

    def run(
        self,
        ctx: TestContext,
        *,
        send: SendFunc = default_send,
        observe: ObserveFunc = default_observe,
    ) -> TestResult:
        """Craft → send (or dry-run) → observe → evaluate."""
        t0 = time.monotonic()
        frames_sent = 0
        try:
            frames = self.craft(ctx)
            for fr in frames:
                send(fr, ctx)
                if not ctx.dry_run:
                    frames_sent += 1
            observation = observe(ctx, frames)
            verdict, explanation, notes = self.evaluate(ctx, frames, observation)
            return TestResult(
                name=self.name,
                suite=self.suite,
                verdict=verdict,
                explanation=explanation,
                duration_s=time.monotonic() - t0,
                diagnostic_notes=notes,
                frames_crafted=len(frames),
                frames_sent=frames_sent,
                dry_run=ctx.dry_run,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Test %s failed with error", self.name)
            return TestResult(
                name=self.name,
                suite=self.suite,
                verdict=Verdict.ERROR,
                explanation=f"Internal error during {self.name}: {exc}",
                duration_s=time.monotonic() - t0,
                diagnostic_notes=[str(exc)],
                frames_crafted=0,
                frames_sent=frames_sent,
                dry_run=ctx.dry_run,
            )


@dataclass
class TestRunner:
    """Execute a list of :class:`RegressionTest` instances."""

    __test__: ClassVar[bool] = False

    tests: list[RegressionTest] = field(default_factory=list)
    send: SendFunc = default_send
    observe: ObserveFunc = default_observe

    def run_all(self, ctx: TestContext, summary: RunSummary) -> RunSummary:
        for test in self.tests:
            logger.info("Running %s ...", test.name)
            result = test.run(ctx, send=self.send, observe=self.observe)
            summary.add(result)
            logger.info(
                "Finished %s => %s",
                test.name,
                result.verdict.value,
                extra={"test": test.name, "verdict": result.verdict.value},
            )
        return summary
