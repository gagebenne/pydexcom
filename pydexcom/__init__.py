"""Python API to interact with Dexcom Share API"""
import datetime

import requests

from .const import (
    _LOGGER,
    DEXCOM_APPLICATION_ID,
    DEXCOM_BASE_URL,
    DEXCOM_LOGIN_ENDPOINT,
    DEXCOM_READ_BLOOD_GLUCOSE_ENDPOINT,
    DEXCOM_TREND_ARROWS,
    DEXCOM_TREND_DESCRIPTIONS,
    DEXCOM_USER_AGENT,
    DEXCOM_VERIFY_SERIAL_NUMBER_ENDPOINT,
)
from .errors import AccountError, ArguementError, SessionError


class GlucoseReading:
    """Class for a glucose reading"""

    def __init__(self, json_glucose_reading: dict):
        self.value = json_glucose_reading["Value"]
        self.trend = json_glucose_reading["Trend"]
        self.trend_description = DEXCOM_TREND_DESCRIPTIONS[self.trend]
        self.trend_arrow = DEXCOM_TREND_ARROWS[self.trend]
        self.time = datetime.datetime.fromtimestamp(
            int(json_glucose_reading["WT"][6:][:-2]) / 1000.0
        )


class Dexcom:
    """Class for communicating with Dexcom Share API"""

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.session_id = None
        self.create_session()

    def _request(
        self,
        method: str,
        endpoint: str,
        headers: dict = None,
        params: dict = None,
        json: dict = {},
    ) -> dict:
        try:
            _LOGGER.debug(f"{method} request to {endpoint}:")
            _LOGGER.debug(
                f"url: {DEXCOM_BASE_URL}/{endpoint} headers: {headers}, params:{params}, json: {json}"
            )
            r = requests.request(
                method,
                f"{DEXCOM_BASE_URL}/{endpoint}",
                headers=headers,
                params=params,
                json=json,
            )
            _LOGGER.debug(f"{method} request response {r.status_code}:")
            _LOGGER.debug(f"json: {r.json()}")
            r.raise_for_status()
            return r.json()
        except requests.HTTPError:
            _LOGGER.error(f"json: {r.json()}")
            if r.status_code == 500:
                if r.json()["Code"] == "SessionNotValid":
                    _LOGGER.error(f'{r.json()["Code"]}: {r.json()["Message"]}')
                    raise SessionError("Session ID expired")
                elif r.json()["Code"] == "SessionIdNotFound":
                    _LOGGER.error(f'{r.json()["Code"]}: {r.json()["Message"]}')
                    raise SessionError("Session ID not found")
                elif r.json()["Code"] == "SSO_AuthenticateAccountNotFound":
                    _LOGGER.error(f'{r.json()["Code"]}: {r.json()["Message"]}')
                    raise AccountError("Account not found")
                elif r.json()["Code"] == "SSO_AuthenticatePasswordInvalid":
                    _LOGGER.error(f'{r.json()["Code"]}: {r.json()["Message"]}')
                    raise AccountError("Password is invalid")
                else:
                    _LOGGER.error(f'{r.json()["Code"]}: {r.json()["Message"]}')
            else:
                _LOGGER.error(f"{r.status_code}: {r.json()}")
        except:
            _LOGGER.error(f"{r.status_code}")
            _LOGGER.error(f"Unknown request error")

    def create_session(self):
        """Creates Dexcom Share API session by getting session id"""
        _LOGGER.debug(f"Get session ID")
        if not self.password:
            _LOGGER.error("Password empty")
            raise AccountError("Password empty")
        try:
            headers = {"User-Agent": DEXCOM_USER_AGENT}
            json = {
                "accountName": self.username,
                "password": self.password,
                "applicationId": DEXCOM_APPLICATION_ID,
            }
            self.session_id = self._request(
                "post", DEXCOM_LOGIN_ENDPOINT, headers=headers, json=json
            )
        except:
            raise

    def verify_serial_number(self, serial_number: str) -> bool:
        """Verifies if a transmitter serial number is assigned to you"""
        if self.session_id is None:
            _LOGGER.error("Session ID empty")
            raise SessionError("Session ID empty")
        if not serial_number:
            _LOGGER.error("Serial number empty")
            raise ArguementError("Serial number empty")
        try:
            params = {"sessionId": self.session_id, "serialNumber": serial_number}
            r = self._request(
                "post", DEXCOM_VERIFY_SERIAL_NUMBER_ENDPOINT, params=params
            )
            return r.json() == "AssignedToYou"
        except:
            raise

    def get_glucose_readings(
        self, minutes: int = 1440, max_count: int = 288
    ) -> [GlucoseReading]:
        """Gets max_count glucose readings within the past minutes, None if no glucose reading in the past 24 hours"""
        if self.session_id is None:
            _LOGGER.error("Session ID empty")
            raise SessionError("Session ID empty")
        try:
            params = {
                "sessionId": self.session_id,
                "minutes": minutes,
                "maxCount": max_count,
            }
            json_glucose_readings = self._request(
                "post", DEXCOM_READ_BLOOD_GLUCOSE_ENDPOINT, params=params
            )
            glucose_readings = []
            for json_glucose_reading in json_glucose_readings:
                glucose_readings.append(GlucoseReading(json_glucose_reading))
            if not glucose_readings:
                return None
            return glucose_readings
        except:
            raise

    def get_latest_glucose_reading(self) -> GlucoseReading:
        """Gets latest available glucose reading, None if no glucose reading in the past 24 hours"""
        glucose_readings = self.get_glucose_readings(max_count=1)
        if not glucose_readings:
            return None
        return glucose_readings[0]

    def get_current_glucose_reading(self) -> GlucoseReading:
        """Gets current available glucose reading, None if no glucose reading in the past 6 minutes"""
        glucose_readings = self.get_glucose_readings(minutes=6, max_count=1)
        if not glucose_readings:
            return None
        return glucose_readings[0]
