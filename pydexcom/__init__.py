'''Python API to interact with Dexcom Share API'''
import requests
import datetime

from .const import (
    _LOGGER,
    DEXCOM_USER_AGENT,
    DEXCOM_APPLICATION_ID,
    DEXCOM_BASE_URL,
    DEXCOM_LOGIN_ENDPOINT,
    DEXCOM_VERIFY_SERIAL_NUMBER_ENDPOINT,
    DEXCOM_READ_BLOOD_GLUCOSE_ENDPOINT,
    DEXCOM_TREND_DESCRIPTIONS,
    DEXCOM_TREND_ARROWS
)

from .errors import AccountError, SessionError, ArguementError

class GlucoseValue:
    '''Class for glucose value data'''
    def __init__(self, json_glucose_value):
        self.value = json_glucose_value['Value']
        self.trend = json_glucose_value['Trend']
        self.trend_description = DEXCOM_TREND_DESCRIPTIONS[self.trend]
        self.trend_arrow = DEXCOM_TREND_ARROWS[self.trend]
        self.time = datetime.datetime.fromtimestamp(int(json_glucose_value['WT'][6:][:-2])/1000.0)

class Dexcom:
    '''Class for communicating with Dexcom Share API'''
    def __init__(self, username, password):
        if not password:
            _LOGGER.error('Password empty')
            raise AccountError('Password empty')
        self.username = username
        self.password = password
        self.session_id = None

    def _request(self, method: str, endpoint: str, headers: dict=None, params: dict=None, json: dict={}) -> dict:
        try:
            _LOGGER.debug(f'{method} request to {endpoint}:')
            _LOGGER.debug(f'url: {DEXCOM_BASE_URL}/{endpoint} headers: {headers}, params:{params}, json: {json}')
            r = requests.request(method, f'{DEXCOM_BASE_URL}/{endpoint}', headers=headers, params=params, json=json)
            _LOGGER.debug(f'{method} request response {r.status_code}:')
            _LOGGER.debug(f'json: {r.json()}')
            r.raise_for_status()
            return r.json()
        except requests.HTTPError:
            _LOGGER.error(f'json: {r.json()}')
            if r.status_code == 500:
                if r.json()['Code'] == 'SessionNotValid':
                    _LOGGER.error(f'{r.json()["Code"]}: {r.json()["Message"]}')
                    raise SessionError('Session ID expired')
                elif r.json()['Code'] == 'SessionIdNotFound':
                    _LOGGER.error(f'{r.json()["Code"]}: {r.json()["Message"]}')
                    raise SessionError('Session ID not found')
                elif r.json()['Code'] == 'SSO_AuthenticateAccountNotFound':
                    _LOGGER.error(f'{r.json()["Code"]}: {r.json()["Message"]}')
                    raise AccountError('Account not found')
                elif r.json()['Code'] == 'SSO_AuthenticatePasswordInvalid':
                    _LOGGER.error(f'{r.json()["Code"]}: {r.json()["Message"]}')
                    raise AccountError('Password is invalid')
                else:
                    _LOGGER.error(f'{r.json()["Code"]}: {r.json()["Message"]}')
            else:
                _LOGGER.error(f'{r.status_code}: {r.json()}')
        except:
            _LOGGER.error(f'{r.status_code}')
            _LOGGER.error(f'Unknown request error')

    def get_session_id(self):
        '''Creates Dexcom Share API session'''
        _LOGGER.debug(f'Get session ID')
        try:
            headers = { 'User-Agent': DEXCOM_USER_AGENT }
            json = { 'accountName': self.username, 'password': self.password, 'applicationId': DEXCOM_APPLICATION_ID }
            self.session_id = self._request('post', DEXCOM_LOGIN_ENDPOINT, headers=headers, json=json)
        except:
            raise

    def verify_serial_number(self, serial_number: str) -> bool:
        '''Verifies if transmitter serial number is assigned to you'''
        if self.session_id is None:
            _LOGGER.error('Session ID empty')
            raise SessionError('Session ID empty')
        if not serial_number:
            _LOGGER.error('Serial number empty')
            raise ArguementError('Serial number empty')
        try:
            params = { 'sessionId': self.session_id, 'serialNumber': serial_number }
            r = self._request('post', DEXCOM_VERIFY_SERIAL_NUMBER_ENDPOINT, params=params)
            if r.json() == 'AssignedToYou':
                return True
            else: # NotAssigned
                return False
        except:
            raise

    def get_glucose_values(self, minutes: int=1440, max_count: int=288) -> [GlucoseValue]:
        '''Gets all glucose values within the last 24 hours'''
        if self.session_id is None:
            _LOGGER.error('Session ID empty')
            raise SessionError('Session ID empty')
        try:
            params = { 'sessionId': self.session_id, 'minutes': minutes, 'maxCount': max_count }
            json_glucose_values = self._request('post', DEXCOM_READ_BLOOD_GLUCOSE_ENDPOINT, params=params)
            glucose_values = []
            for json_glucose_value in json_glucose_values:
                glucose_values.append(GlucoseValue(json_glucose_value))
            return glucose_values
        except:
            raise

    def get_glucose_value(self) -> GlucoseValue:
        '''Gets most recent glucose value data'''
        return self.get_glucose_values(max_count=1)[0]
