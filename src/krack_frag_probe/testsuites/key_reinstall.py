"""Key-reinstallation *style* regression tests (educational).

Author: Kirtan Teg Singh (ਕੀਰਤਨ ਤੇਗ ਸਿੰਘ)

These checks relate to historical KRACK-class issues around key install
ordering and nonce/PN handling. They do **not** implement the public KRACK
attacks, complete handshake hijacks, or force nonce reset on a victim.

Each test crafts the **minimum** lab frames needed to exercise related
stack paths under operator control.
"""

from __future__ import annotations

from dataclasses import dataclass

from krack_frag_probe.core.frame_builder import (
    BuiltFrame,
    build_lab_data_probe,
    build_protected_flag_edge,
)
from krack_frag_probe.core.tester import RegressionTest, TestContext


@dataclass
class NonceReuseGuardTest(RegressionTest):
    """Probe protected-flag / PN-related edge handling (no real crypto)."""

    def craft(self, ctx: TestContext) -> list[BuiltFrame]:
        # Two protected-flag edge frames with same lab sequence — educational
        # only: we are not installing keys or forcing nonce reuse on the AP.
        f1 = build_protected_flag_edge(
            bssid=ctx.bssid,
            src=ctx.lab_src,
            dst=ctx.target_dst,
            name="nonce_reuse_guard.protected_a",
        )
        f2 = build_lab_data_probe(
            bssid=ctx.bssid,
            src=ctx.lab_src,
            dst=ctx.target_dst,
            payload=b"KFP-LAB-NONCE-EDGE\x00\x00\x00\x01",
            frag=0,
            seq=3,  # same SC as protected edge builder default
            protected=1,
            name="nonce_reuse_guard.protected_b",
            purpose=(
                "Second protected lab frame with controlled SC. Used to verify "
                "that historical nonce/PN reuse *symptoms* remain absent. "
                "Does not reinstall keys or complete a 4-way handshake."
            ),
        )
        return [f1, f2]


@dataclass
class ReinstallEdgeInstallOrderTest(RegressionTest):
    """Key-install ordering edge: benign data after protected edge marker."""

    def craft(self, ctx: TestContext) -> list[BuiltFrame]:
        # Ordering probe: unprotected lab marker then protected edge.
        # Historical issues involved incorrect reinstall during handshake
        # message processing — we do not run that handshake.
        plain = build_lab_data_probe(
            bssid=ctx.bssid,
            src=ctx.lab_src,
            dst=ctx.target_dst,
            payload=b"KFP-LAB-INSTALL-ORDER-PLAIN",
            frag=0,
            seq=20,
            protected=0,
            name="reinstall_edge.plain_marker",
            purpose=(
                "Unprotected lab marker preceding a protected edge frame. "
                "Educational ordering probe only."
            ),
        )
        prot = build_protected_flag_edge(
            bssid=ctx.bssid,
            src=ctx.lab_src,
            dst=ctx.target_dst,
            name="reinstall_edge.protected_marker",
        )
        return [plain, prot]


@dataclass
class ReplayCounterStyleTest(RegressionTest):
    """Sequence control monotonicity smoke probe (lab markers only)."""

    def craft(self, ctx: TestContext) -> list[BuiltFrame]:
        frames: list[BuiltFrame] = []
        for i, seq in enumerate((30, 31, 30)):  # intentional non-monotonic last
            frames.append(
                build_lab_data_probe(
                    bssid=ctx.bssid,
                    src=ctx.lab_src,
                    dst=ctx.target_dst,
                    payload=f"KFP-LAB-SEQ-{i}".encode(),
                    frag=0,
                    seq=seq,
                    protected=0,
                    name=f"replay_counter_style.seq_{seq}_{i}",
                    purpose=(
                        "Sequence control smoke frames including a non-monotonic "
                        "lab sequence. Checks that receivers still apply expected "
                        "replay/state handling. Not a full replay attack."
                    ),
                )
            )
        return frames


KEY_REINSTALL_TESTS: list[RegressionTest] = [
    NonceReuseGuardTest(
        name="nonce_reuse_guard",
        suite="key_reinstall",
        description=(
            "Regression probe for historical nonce/PN reuse style symptoms "
            "using protected-flag edge frames without real key install."
        ),
        historical_category="KRACK-style key/nonce install edge cases",
    ),
    ReinstallEdgeInstallOrderTest(
        name="reinstall_edge_install_order",
        suite="key_reinstall",
        description=(
            "Ordering probe related to historical key reinstall edge handling; no handshake hijack."
        ),
        historical_category="KRACK-style key reinstallation edge cases",
    ),
    ReplayCounterStyleTest(
        name="replay_counter_style",
        suite="key_reinstall",
        description=("Sequence control non-monotonicity smoke test for replay/state handling."),
        historical_category="Replay/PN state handling (related historical fixes)",
    ),
]
