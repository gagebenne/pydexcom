"""Test retrieving glucose readings."""

import os

import pytest

from pydexcom import (
    DEFAULT_SESSION_ID,
    SESSION_ERROR_SESSION_ID_DEFAULT,
    SESSION_ERROR_SESSION_NOT_FOUND,
    Dexcom,
    SessionError,
)

USERNAME = os.environ.get("PYDEXCOM_USERNAME")
PASSWORD = os.environ.get("PYDEXCOM_PASSWORD")


def test_env():
    """Ensure environment variables are set."""
    assert USERNAME
    assert PASSWORD


def test_glucose_readings_success():
    """Test retrieving glucose readings sucessfully."""
    d = Dexcom(USERNAME, PASSWORD)
    d.get_current_glucose_reading()
    d.get_latest_glucose_reading()


def test_glucose_readings_invalid_session():
    """Test retrieving glucose readings with default session ID."""
    d = Dexcom(USERNAME, PASSWORD)
    d.session_id = DEFAULT_SESSION_ID
    with pytest.raises(SessionError) as e:
        d.get_current_glucose_reading()
    assert SESSION_ERROR_SESSION_ID_DEFAULT == str(e.value)


def test_glucose_readings_expired_session():
    """Test retrieving glucose readings with expired session ID."""
    d = Dexcom(USERNAME, PASSWORD)
    d.session_id = "12345678-1234-1234-1234-123456789012"
    with pytest.raises(SessionError) as e:
        d.get_current_glucose_reading()
    assert SESSION_ERROR_SESSION_NOT_FOUND == str(e.value)
