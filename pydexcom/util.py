"""Utilities for pydexcom."""

from __future__ import annotations

import logging
from uuid import UUID

_LOGGER = logging.getLogger("pydexcom")


def valid_uuid(uuid: str | None) -> bool:
    """Check if UUID is valid."""
    try:
        UUID(str(uuid))
    except ValueError:
        return False
    else:
        return True
