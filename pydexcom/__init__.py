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
    DEXCOM_BLOOD_GLUCOSE_ENDPOINT
)

from .errors import InvalidAccountError, InvalidPasswordError, SessionExpiredError, SessionNotFoundError

class DexcomData:
    '''Class for dexcom glucose value data'''
    def __init__(self, json_glucose_value):
        self.value = json_glucose_value['Value']
        self.trend = json_glucose_value['Trend']
        self.trend_description = ['', 'rising quickly', 'rising slightly', 'steady', 'falling slightly', 'falling', 'falling quickly', 'unable to determine trend', 'trend unavailable'][self.trend]
        self.trend_arrow = ['', '↑↑', '↑', '↗', '→', '↘', '↓', '↓↓', '?', '-'][self.trend]
        self.time = datetime.datetime.fromtimestamp(int(json_glucose_value['WT'][6:][:-2])/1000.0)

class Dexcom:
    '''Class for communicating with Dexcom Share API'''
    def __init__(self, username, password):
        if password is None:
            _LOGGER.error('Password is blank, unable to continue')

        self.username = username
        self.password = password
        self.session = None

        try:
            self._create_session()
        except:
            raise


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
                if False:
                    raise SessionExpiredError(r.json()['Message'])
                elif r.json()['Code'] == 'SessionIdNotFound':
                    raise SessionNotFoundError(r.json()['Message'])
                elif r.json()['Code'] == 'SSO_AuthenticateAccountNotFound':
                    raise InvalidAccountError(r.json()['Message'])
                elif r.json()['Code'] == 'SSO_AuthenticatePasswordInvalid':
                    raise InvalidPasswordError(r.json()['Message'])
                else:
                    _LOGGER.error(f'{r.json()["Code"]}: {r.json()["Message"]}')
            else:
                _LOGGER.error(f'{r.status_code}: {r.json()}')
        except:
            _LOGGER.error(f'Unknown error')

    def _create_session(self):
        '''Creates Dexcom Share API session'''
        _LOGGER.debug(f'Create session')
        try:
            headers = {
                'User-Agent': DEXCOM_USER_AGENT,
            }
            json = {
                'accountName': self.username,
                'applicationId': DEXCOM_APPLICATION_ID,
                'password': self.password
            }

            self.session = self._request('post', DEXCOM_LOGIN_ENDPOINT, headers=headers, json=json)
        except:
            raise

    def _verify_serial_number(self, serial) -> bool:
        '''Verifies if transmitter serial number is assigned to you'''
        try:
            params = {
                'sessionId': self.session,
                'serialNumber': serial
            }
            r = self._request('post', DEXCOM_VERIFY_SERIAL_NUMBER_ENDPOINT, params=params)
            if r.json() == 'AssignedToYou':
                return True
            else: #NotAssigned
                return False
        except (SessionExpiredError, SessionNotFoundError):
            try:
                self._create_session()
            except:
                raise
        except:
            raise

    def _get_glucose_values(self, minutes: int=1440, max_count=1) -> [DexcomData]:
        '''Gets glucose values'''
        try:
            params = {
                'sessionId': self.session,
                'minutes': minutes,
                'maxCount': max_count
            }

            json_glucose_values = self._request('post', DEXCOM_BLOOD_GLUCOSE_ENDPOINT, params=params)
            glucose_values = []
            for json_glucose_value in json_glucose_values:
                glucose_values.append(DexcomData(json_glucose_value))

            return glucose_values
        except (SessionExpiredError, SessionNotFoundError):
            try:
                self._create_session()
            except:
                raise
        except:
            raise

    def get_recent_glucose_value(self) -> DexcomData:
        '''Gets most recent glucose value data'''
        return self._get_glucose_values()[0]

    def get_all_glucose_values(self) -> [DexcomData]:
        '''Get all glucose values data (within the past 24 hours)'''
        return self._get_glucose_values(max_count=288)
