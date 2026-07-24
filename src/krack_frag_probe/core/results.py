"""Result models: per-test verdicts and run summaries.

Author: Kirtan Teg Singh (ਕੀਰਤਨ ਤੇਗ ਸਿੰਘ)
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, ClassVar

from krack_frag_probe import AUTHOR_FULL, __author__, __author_gurmukhi__


class Verdict(StrEnum):
    """Deterministic human-readable test outcomes."""

    PASS = "PASS"
    FAIL = "FAIL"
    INCONCLUSIVE = "INCONCLUSIVE"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"

    def is_failure(self) -> bool:
        return self in (Verdict.FAIL, Verdict.ERROR)


@dataclass(slots=True)
class TestResult:
    """Outcome of a single named regression test."""

    # Prevent pytest from collecting this model as a test class
    __test__: ClassVar[bool] = False

    name: str
    suite: str
    verdict: Verdict
    explanation: str
    duration_s: float = 0.0
    diagnostic_notes: list[str] = field(default_factory=list)
    frames_crafted: int = 0
    frames_sent: int = 0
    dry_run: bool = False

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["verdict"] = self.verdict.value
        return d


@dataclass(slots=True)
class RunSummary:
    """Aggregate results for a full ``run`` invocation."""

    timestamp: str
    iface: str
    bssid: str
    client: str | None
    dry_run: bool
    results: list[TestResult] = field(default_factory=list)
    lab_banner: str = "LAB ONLY – NOT FOR PRODUCTION USE"
    tool_version: str = "1.0.0"
    author: str = AUTHOR_FULL
    author_romanized: str = __author__
    author_gurmukhi: str = __author_gurmukhi__
    operator_notes: str = (
        "Authorized laboratory regression test. Not for production or third-party use."
    )
    interface_details: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        *,
        iface: str,
        bssid: str,
        client: str | None,
        dry_run: bool,
        tool_version: str,
        interface_details: dict[str, Any] | None = None,
    ) -> RunSummary:
        return cls(
            timestamp=datetime.now(UTC).isoformat(),
            iface=iface,
            bssid=bssid,
            client=client,
            dry_run=dry_run,
            tool_version=tool_version,
            author=AUTHOR_FULL,
            author_romanized=__author__,
            author_gurmukhi=__author_gurmukhi__,
            interface_details=interface_details or {},
        )

    def add(self, result: TestResult) -> None:
        self.results.append(result)

    @property
    def counts(self) -> dict[str, int]:
        counts: dict[str, int] = {v.value: 0 for v in Verdict}
        for r in self.results:
            counts[r.verdict.value] = counts.get(r.verdict.value, 0) + 1
        counts["total"] = len(self.results)
        return counts

    def any_failures(self) -> bool:
        return any(r.verdict.is_failure() for r in self.results)

    def exit_code(self) -> int:
        """0 = all passed, 1 = failures, (config errors use 2 outside this model)."""
        if not self.results:
            return 2
        if self.any_failures():
            return 1
        # INCONCLUSIVE alone does not fail the run (operator may re-test)
        # but ERROR/FAIL do. All PASS/SKIPPED/INCONCLUSIVE => 0.
        return 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "lab_banner": self.lab_banner,
            "tool_version": self.tool_version,
            "author": self.author,
            "author_romanized": self.author_romanized,
            "author_gurmukhi": self.author_gurmukhi,
            "timestamp": self.timestamp,
            "iface": self.iface,
            "bssid": self.bssid,
            "client": self.client,
            "dry_run": self.dry_run,
            "operator_notes": self.operator_notes,
            "interface_details": self.interface_details,
            "counts": self.counts,
            "results": [r.to_dict() for r in self.results],
        }
