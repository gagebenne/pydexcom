"""
.. include:: ../README.md
"""  # noqa: D200, D400, D415

from .const import Region
from .dexcom import Dexcom
from .glucose_reading import GlucoseReading

__all__ = [
    "Dexcom",
    "GlucoseReading",
    "Region",
    "const",
    "errors",
]
