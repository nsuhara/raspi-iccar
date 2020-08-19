"""app/apis/client/post_motor.py
"""
import json

import requests

from apis.client import URL

url = '{url}'.format(**{
    'url': URL
})
data = json.dumps({
    'process': 'back_end',
    'request': {
        'param1': 'button',
        'param2': [{
            'button_type': 'BUTTON_TYPE_UP',
            'button_event': 'BUTTON_EVENT_PRESS',
            'button_option': 50
        }]
    }
})
headers = {
    'Content-Type': 'application/json'
}

res = requests.post(url=url, data=data, headers=headers)

print(res.status_code)
print(res.text)
