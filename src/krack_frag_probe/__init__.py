"""krack-frag-probe: educational lab-only Wi-Fi regression tester.

This package checks for residual or re-introduced *symptoms* of
already-publicly-patched Wi-Fi edge cases (KRACK-style key reinstallation
and FragAttacks-style fragmentation/aggregation handling).

**Authorized laboratory use only.** Not an exploit toolkit.

Author: Kirtan Teg Singh (ਕੀਰਤਨ ਤੇਗ ਸਿੰਘ)
"""

from __future__ import annotations

__version__ = "1.0.0"

# Author: romanized Latin + Gurmukhi (ਗੁਰਮੁਖੀ) forms
__author__ = "Kirtan Teg Singh"
__author_gurmukhi__ = "ਕੀਰਤਨ ਤੇਗ ਸਿੰਘ"
__author_full__ = f"{__author__} ({__author_gurmukhi__})"

__all__ = [
    "__author__",
    "__author_full__",
    "__author_gurmukhi__",
    "__version__",
    "AUTHOR_FULL",
    "LAB_ONLY_BANNER",
]

# Convenience alias used by CLI and reports
AUTHOR_FULL = __author_full__

# Safety banner available for importers
LAB_ONLY_BANNER = (
    "LAB ONLY – NOT FOR PRODUCTION USE. "
    "Authorized testing of equipment you own or have written permission to test."
)
