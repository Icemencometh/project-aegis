"""Re-export of the canonical MetaModelEngine.

aegis.scoring.meta.MetaModelEngine is the canonical implementation (it's the
one Scoring Hub actually wires up per Aegis_Module_Contracts.md). This module
used to carry a second, independently-drifting copy of the same class under
`aegis.meta` -- that duplication was a coding-standards violation ("no hidden
coupling between modules") waiting to bite the next person who edited one
copy and not the other. Import path kept for backward compatibility.
"""

from __future__ import annotations

from ..scoring.meta import MetaModelEngine

__all__ = ["MetaModelEngine"]
