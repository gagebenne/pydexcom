"""Tests for pydexcom."""
import os

USERNAME = os.environ.get("DEXCOM_USERNAME", "")
PASSWORD = os.environ.get("DEXCOM_PASSWORD", "")
assert USERNAME
assert PASSWORD
