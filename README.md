# pydexcom
Python API to interact with Dexcom Share API

```python
>>> dexcom = pydexcom.Dexcom('username', 'password')

>>> bg = dexcom.get_current_glucose_reading()

>>> bg.value
105

>>> bg.trend_arrow
'→'

>>> bg.trend_description
'steady'
```
