# pydexcom
Python API to interact with Dexcom Share API

```python
>>> from pydexcom import Dexcom, DexcomData

>>> dexcom = Dexcom('username', 'password')

>>> dexcom.get_recent_glucose_value().value
105

>>> dexcom.get_recent_glucose_value.trend_arrow
'→'

>>> dexcom.get_recent_glucose_value().trend_description
'steady'
```
