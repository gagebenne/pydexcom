'''Errors used in pydexcom'''

class DexcomError(Exception):
    '''Base class for all Dexcom errors'''
    pass

class InvalidAccountError(DexcomError):
    '''Raised when Dexcom API Share returns a code indicating invalid account'''
    pass

class InvalidPasswordError(DexcomError):
    '''Raised when Dexcom Share API returns a code indicating invalid password'''
    pass

class SessionExpiredError(DexcomError):
    '''Raised when Dexcom Share API returns a code indicating session expiration'''
    pass

class SessionNotFoundError(DexcomError):
    '''Raised when Dexcom Share API returns a code indicating session not found'''
    pass
