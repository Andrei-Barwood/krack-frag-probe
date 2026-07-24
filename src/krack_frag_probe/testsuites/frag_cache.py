"""Fragmentation / aggregation cache regression tests (educational).

Related to historical FragAttacks-class issues around fragment caches,
A-MSDU parsing, and aggregation handling. These tests craft **minimal**
benign fragments and aggregation-style payloads with clear lab markers.

They do **not** implement cache poisoning attacks against third-party traffic,
plaintext injection into other clients' sessions, or full exploit chains.
"""

from __future__ import annotations

from dataclasses import dataclass

from krack_frag_probe.core.frame_builder import (
    BuiltFrame,
    build_amsdu_style_probe,
    build_fragment_pair,
    build_lab_data_probe,
)
from krack_frag_probe.core.tester import RegressionTest, TestContext


@dataclass
class CachePoisonStyleProbe(RegressionTest):
    """Two-fragment MSDU with lab payload (reassembly path regression)."""

    def craft(self, ctx: TestContext) -> list[BuiltFrame]:
        return build_fragment_pair(
            bssid=ctx.bssid,
            src=ctx.lab_src,
            dst=ctx.target_dst,
            body=b"KFP-LAB-FRAG-CACHE-PROBE-BODY-EDU-ONLY",
            seq=77,
            name_prefix="cache_poison_style_probe",
        )


@dataclass
class MixedKeyFragmentStyleTest(RegressionTest):
    """Fragment with Protected flag differences (edge case, no real keys)."""

    def craft(self, ctx: TestContext) -> list[BuiltFrame]:
        # Historical issues mixed plaintext/encrypted fragments. We mark frames
        # clearly as lab probes and do not supply valid encryption.
        f0 = build_lab_data_probe(
            bssid=ctx.bssid,
            src=ctx.lab_src,
            dst=ctx.target_dst,
            payload=b"KFP-LAB-MIX-FRAG0",
            frag=0,
            seq=88,
            more_frag=1,
            protected=0,
            name="mixed_key_fragment.plain_frag0",
            purpose=(
                "Plain fragment 0 (More Fragments=1). Educational mixed-protection "
                "edge; not a cross-context injection attack."
            ),
        )
        f1 = build_lab_data_probe(
            bssid=ctx.bssid,
            src=ctx.lab_src,
            dst=ctx.target_dst,
            payload=b"KFP-LAB-MIX-FRAG1",
            frag=1,
            seq=88,
            more_frag=0,
            protected=1,
            name="mixed_key_fragment.protected_frag1",
            purpose=(
                "Protected-flag fragment 1 completing seq. Verifies patched stacks "
                "still reject unsafe mixed-context reassembly."
            ),
        )
        return [f0, f1]


@dataclass
class AmsduAggregationProbe(RegressionTest):
    """A-MSDU-style boundary parsing probe with lab markers."""

    def craft(self, ctx: TestContext) -> list[BuiltFrame]:
        return [
            build_amsdu_style_probe(
                bssid=ctx.bssid,
                src=ctx.lab_src,
                dst=ctx.target_dst,
                name="amsdu_aggregation_probe",
            )
        ]


@dataclass
class AmpduDelimiterStyleProbe(RegressionTest):
    """Lightweight A-MPDU-ish delimiter pattern in payload (educational)."""

    def craft(self, ctx: TestContext) -> list[BuiltFrame]:
        # Educational delimiter-like pattern — not a full A-MPDU aggregator.
        # Pattern inspired by public delimiter structure docs, filled with lab markers.
        delimiter_like = b"\x00\x00" + b"KFP" + b"\x4c\x41\x42"  # KFP LAB
        payload = delimiter_like + b"KFP-LAB-AMPDU-STYLE" + delimiter_like
        return [
            build_lab_data_probe(
                bssid=ctx.bssid,
                src=ctx.lab_src,
                dst=ctx.target_dst,
                payload=payload,
                frag=0,
                seq=99,
                name="ampdu_delimiter_style_probe",
                purpose=(
                    "A-MPDU-style delimiter pattern probe for aggregation parsing "
                    "regression. Not a full A-MPDU injection attack."
                ),
            )
        ]


FRAG_CACHE_TESTS: list[RegressionTest] = [
    CachePoisonStyleProbe(
        name="cache_poison_style_probe",
        suite="frag_cache",
        description=(
            "Two-fragment lab MSDU exercising reassembly/cache paths related to "
            "historical FragAttacks-class cache issues."
        ),
        historical_category="FragAttacks-style fragment cache handling",
    ),
    MixedKeyFragmentStyleTest(
        name="mixed_key_fragment_style",
        suite="frag_cache",
        description=("Mixed Protected-flag fragments for unsafe reassembly regression check."),
        historical_category="Mixed plaintext/encrypted fragment handling",
    ),
    AmsduAggregationProbe(
        name="amsdu_aggregation_probe",
        suite="frag_cache",
        description="A-MSDU-style aggregation boundary parsing regression probe.",
        historical_category="A-MSDU aggregation parsing (historical fixes)",
    ),
    AmpduDelimiterStyleProbe(
        name="ampdu_delimiter_style_probe",
        suite="frag_cache",
        description="A-MPDU-style delimiter pattern educational probe.",
        historical_category="A-MPDU aggregation parsing (historical fixes)",
    ),
]
