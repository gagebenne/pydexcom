"""
.. include:: ../README.md
"""  # noqa: D200, D212, D400, D415

from .const import Region
from .dexcom import Dexcom
from .glucose_reading import GlucoseReading

__all__ = [
    "Dexcom",
    "Region",
    "GlucoseReading",
    "errors",
    "const",
]
