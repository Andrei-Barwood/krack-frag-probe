"""krack-frag-probe: educational lab-only Wi-Fi regression tester.

This package checks for residual or re-introduced *symptoms* of
already-publicly-patched Wi-Fi edge cases (KRACK-style key reinstallation
and FragAttacks-style fragmentation/aggregation handling).

**Authorized laboratory use only.** Not an exploit toolkit.
"""

from __future__ import annotations

__version__ = "1.0.0"
__all__ = ["__version__"]

# Safety banner available for importers
LAB_ONLY_BANNER = (
    "LAB ONLY – NOT FOR PRODUCTION USE. "
    "Authorized testing of equipment you own or have written permission to test."
)
