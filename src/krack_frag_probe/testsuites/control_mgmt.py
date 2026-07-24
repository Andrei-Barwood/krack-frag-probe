"""Control and management frame edge-case regression tests (educational).

Historical key-install and fragmentation issues sometimes interacted with
management/control processing (state machines, buffering). These probes use
**single** benign management frames — never floods, never automated targeting
of unknown stations.
"""

from __future__ import annotations

from dataclasses import dataclass

from krack_frag_probe.core.frame_builder import (
    BuiltFrame,
    build_deauth_single,
    build_mgmt_action_probe,
    build_probe_request_lab,
)
from krack_frag_probe.core.tester import RegressionTest, TestContext


@dataclass
class SingleDeauthEdgeTest(RegressionTest):
    """Exactly one deauth toward the explicit lab target (state edge)."""

    def craft(self, ctx: TestContext) -> list[BuiltFrame]:
        dst = ctx.client if ctx.client else ctx.bssid
        return [
            build_deauth_single(
                bssid=ctx.bssid,
                dst=dst,
                src=ctx.bssid,
                reason=1,
                name="single_deauth_edge",
            )
        ]


@dataclass
class ActionMgmtPathTest(RegressionTest):
    """Benign Action frame with lab marker."""

    def craft(self, ctx: TestContext) -> list[BuiltFrame]:
        return [
            build_mgmt_action_probe(
                bssid=ctx.bssid,
                src=ctx.lab_src,
                dst=ctx.target_dst,
                name="action_mgmt_path",
            )
        ]


@dataclass
class ProbeRequestSmokeTest(RegressionTest):
    """Probe request with lab SSID (mgmt path smoke)."""

    def craft(self, ctx: TestContext) -> list[BuiltFrame]:
        return [
            build_probe_request_lab(
                bssid=ctx.bssid,
                src=ctx.lab_src,
                ssid="KFP-LAB-ONLY",
                name="probe_request_smoke",
            )
        ]


CONTROL_MGMT_TESTS: list[RegressionTest] = [
    SingleDeauthEdgeTest(
        name="single_deauth_edge",
        suite="control_mgmt",
        description=(
            "Single deauthentication frame for state-machine edge observation. "
            "Floods are intentionally unsupported."
        ),
        historical_category="Management-frame state interactions (historical)",
    ),
    ActionMgmtPathTest(
        name="action_mgmt_path",
        suite="control_mgmt",
        description="Benign Action management frame path regression probe.",
        historical_category="Action frame processing edge cases",
    ),
    ProbeRequestSmokeTest(
        name="probe_request_smoke",
        suite="control_mgmt",
        description="Probe request with lab SSID marker (management path smoke test).",
        historical_category="Management path smoke / edge interaction",
    ),
]
