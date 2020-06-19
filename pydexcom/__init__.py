"""Python API to interact with Dexcom Share API"""
import datetime

import requests

from .const import (
    _LOGGER,
    ACCOUNT_ERROR_ACCOUNT_NOT_FOUND,
    ACCOUNT_ERROR_PASSWORD_INVALID,
    ACCOUNT_ERROR_PASSWORD_NULL_EMPTY,
    ACCOUNT_ERROR_UNKNOWN,
    ACCOUNT_ERROR_USERNAME_NULL_EMPTY,
    ARGUEMENT_ERROR_MAX_COUNT_INVALID,
    ARGUEMENT_ERROR_MINUTES_INVALID,
    ARGUEMENT_ERROR_SERIAL_NUMBER_NULL_EMPTY,
    DEFAULT_SESSION_ID,
    DEXCOM_APPLICATION_ID,
    DEXCOM_AUTHENTICATE_ENDPOINT,
    DEXCOM_BASE_URL,
    DEXCOM_BASE_URL_OUS,
    DEXCOM_LOGIN_ENDPOINT,
    DEXCOM_READ_BLOOD_GLUCOSE_ENDPOINT,
    DEXCOM_TREND_ARROWS,
    DEXCOM_TREND_DESCRIPTIONS,
    DEXCOM_USER_AGENT,
    DEXCOM_VERIFY_SERIAL_NUMBER_ENDPOINT,
    MMOL_L_CONVERTION_FACTOR,
    SESSION_ERROR_SESSION_ID_DEFAULT,
    SESSION_ERROR_SESSION_ID_NULL,
    SESSION_ERROR_SESSION_NOT_FOUND,
    SESSION_ERROR_SESSION_NOT_VALID,
)
from .errors import AccountError, ArguementError, SessionError


class GlucoseReading:
    """Class for a glucose reading"""

    def __init__(self, json_glucose_reading: dict):
        self.value = json_glucose_reading["Value"]
        self.mg_dl = self.value
        self.mmol_l = round(self.value * MMOL_L_CONVERTION_FACTOR, 1)
        self.trend = json_glucose_reading["Trend"]
        self.trend_description = DEXCOM_TREND_DESCRIPTIONS[self.trend]
        self.trend_arrow = DEXCOM_TREND_ARROWS[self.trend]
        self.time = datetime.datetime.fromtimestamp(
            int(json_glucose_reading["WT"][6:][:-2]) / 1000.0
        )


class Dexcom:
    """Class for communicating with Dexcom Share API"""

    def __init__(self, username: str, password: str, ous: bool = False):
        self.base_url = DEXCOM_BASE_URL_OUS if ous else DEXCOM_BASE_URL
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
                f"url: {self.base_url}/{endpoint} headers: {headers}, params:{params}, json: {json}"
            )
            r = requests.request(
                method,
                f"{self.base_url}/{endpoint}",
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
                _LOGGER.error(f'{r.json()["Code"]}: {r.json()["Message"]}')
                if r.json()["Code"] == "SessionNotValid":
                    raise SessionError(SESSION_ERROR_SESSION_NOT_VALID)
                elif r.json()["Code"] == "SessionIdNotFound":
                    raise SessionError(SESSION_ERROR_SESSION_NOT_FOUND)
                elif r.json()["Code"] == "SSO_AuthenticateAccountNotFound":
                    raise AccountError(ACCOUNT_ERROR_ACCOUNT_NOT_FOUND)
                elif r.json()["Code"] == "SSO_AuthenticatePasswordInvalid":
                    raise AccountError(ACCOUNT_ERROR_PASSWORD_INVALID)
                elif r.json()["Code"] == "InvalidArgument":
                    if "accountName" in r.json()["Message"]:
                        raise AccountError(ACCOUNT_ERROR_USERNAME_NULL_EMPTY)
                    if "password" in r.json()["Message"]:
                        raise AccountError(ACCOUNT_ERROR_PASSWORD_NULL_EMPTY)
                else:
                    _LOGGER.error(f'{r.json()["Code"]}: {r.json()["Message"]}')
            else:
                _LOGGER.error(f"{r.status_code}: {r.json()}")
        except:
            _LOGGER.error(r.status_code)
            _LOGGER.error("Unknown request error")
        return None

    def _validate_session_id(self):
        if not self.session_id:
            _LOGGER.error(SESSION_ERROR_SESSION_ID_NULL)
            raise SessionError(SESSION_ERROR_SESSION_ID_NULL)
        if self.session_id == DEFAULT_SESSION_ID:
            _LOGGER.error(SESSION_ERROR_SESSION_ID_DEFAULT)
            raise SessionError(SESSION_ERROR_SESSION_ID_DEFAULT)

    def _validate_account(self):
        if not self.username:
            _LOGGER.error(ACCOUNT_ERROR_USERNAME_NULL_EMPTY)
            raise AccountError(ACCOUNT_ERROR_USERNAME_NULL_EMPTY)
        if not self.password:
            _LOGGER.error(ACCOUNT_ERROR_PASSWORD_NULL_EMPTY)
            raise AccountError(ACCOUNT_ERROR_PASSWORD_NULL_EMPTY)

    def create_session(self):
        """Creates Dexcom Share API session by getting session id"""
        _LOGGER.debug(f"Get session ID")
        self._validate_account()

        headers = {"User-Agent": DEXCOM_USER_AGENT}
        json = {
            "accountName": self.username,
            "password": self.password,
            "applicationId": DEXCOM_APPLICATION_ID,
        }
        self.session_id = self._request(
            "post", DEXCOM_AUTHENTICATE_ENDPOINT, headers=headers, json=json
        )
        try:
            self._validate_session_id()
            self.session_id = self._request(
                "post", DEXCOM_LOGIN_ENDPOINT, headers=headers, json=json
            )
            self._validate_session_id()
        except SessionError:
            raise AccountError(ACCOUNT_ERROR_UNKNOWN)

    def verify_serial_number(self, serial_number: str) -> bool:
        """Verifies if a transmitter serial number is assigned to you"""
        self._validate_session_id()
        if not serial_number:
            _LOGGER.error(ARGUEMENT_ERROR_SERIAL_NUMBER_NULL_EMPTY)
            raise ArguementError(ARGUEMENT_ERROR_SERIAL_NUMBER_NULL_EMPTY)

        params = {"sessionId": self.session_id, "serialNumber": serial_number}
        try:
            r = self._request("post", DEXCOM_VERIFY_SERIAL_NUMBER_ENDPOINT, params=params)
        except SessionError:
            _LOGGER.debug(f"Fetching new session id")
            self.create_session()
            r = self._request("post", DEXCOM_VERIFY_SERIAL_NUMBER_ENDPOINT, params=params)
        return r.json() == "AssignedToYou"


    def get_glucose_readings(
        self, minutes: int = 1440, max_count: int = 288
    ) -> [GlucoseReading]:
        """Gets max_count glucose readings within the past minutes, None if no glucose reading in the past 24 hours"""
        self._validate_session_id()
        if minutes < 1 or minutes > 1440:
            _LOGGER.error(ARGUEMENT_ERROR_MINUTES_INVALID)
            raise ArguementError(ARGUEMENT_ERROR_MINUTES_INVALID)
        if max_count < 1 or max_count > 288:
            _LOGGER.error(ARGUEMENT_ERROR_MAX_COUNT_INVALID)
            raise ArguementError(ARGUEMENT_ERROR_MAX_COUNT_INVALID)

        params = {
            "sessionId": self.session_id,
            "minutes": minutes,
            "maxCount": max_count,
        }
        try:
            json_glucose_readings = self._request(
                "post", DEXCOM_READ_BLOOD_GLUCOSE_ENDPOINT, params=params
            )
        except SessionError:
            _LOGGER.debug(f"Fetching new session id")
            self.create_session()
            json_glucose_readings = self._request(
                "post", DEXCOM_READ_BLOOD_GLUCOSE_ENDPOINT, params=params
            )

        glucose_readings = []
        if not json_glucose_readings:
            return None
        for json_glucose_reading in json_glucose_readings:
            glucose_readings.append(GlucoseReading(json_glucose_reading))
        if not glucose_readings:
            return None
        return glucose_readings

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
