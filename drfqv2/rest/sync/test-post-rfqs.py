# built ins
import base64
import hmac
import time
import json

# installed
import requests

access_key = '<access-key>'
secret_key = b'<secret-key>'


def sign_request(secret_key, method, path, body):
    signing_key = base64.b64decode(secret_key)
    timestamp = str(int(time.time() * 1000)).encode('utf-8')
    message = b'\n'.join([timestamp, method.upper(), path, body])
    digest = hmac.digest(signing_key, message, 'sha256')
    signature = base64.b64encode(digest)
    return timestamp, signature


# Request Host
host = 'https://api.testnet.paradigm.trade'

# POST /v2/drfq/rfqs
method = 'POST'
path = '/v2/drfq/rfqs'

payload = {
            "venue": "DBT",
            "quantity": "100",
            "is_taker_anonymous": True,
            "counterparties": ["DSK2", "DSK3"],
            "legs": [
                    {
                        "instrument_id": 12314,
                        "ratio": "1",
                        "side": "SELL"
                    }
                    ]
            }

json_payload = json.dumps(payload)

timestamp, signature = sign_request(secret_key=secret_key,
                                    method=method.encode('utf-8'),
                                    path=path.encode('utf-8'),
                                    body=json_payload.encode('utf-8'),
                                    )

headers = {
          'Paradigm-API-Timestamp': timestamp,
          'Paradigm-API-Signature': signature,
          'Authorization': f'Bearer {access_key}'
           }

# Send request
response = requests.post(
    host+path,
    headers=headers,
    json=payload
    )

print(response.status_code)
print(response.text)
