# built ins
import base64
import hmac
import time

# installed
import requests

access_key = 'Z9gBdD05yiHLotRCxrSeFTfC'
secret_key = b'9qgG7DU0XNaqF9n5Q35iQtL5Bv7JFNUffagT7/qC9jlH0exj'


def sign_request(secret_key, method, path, body):
    signing_key = base64.b64decode(secret_key)
    timestamp = str(int(time.time() * 1000)).encode('utf-8')
    message = b'\n'.join([timestamp, method.upper(), path, body])
    digest = hmac.digest(signing_key, message, 'sha256')
    signature = base64.b64encode(digest)
    return timestamp, signature


# Request Host
host = 'https://api.nightly.paradigm.co'

# GET /v1/grfq/rfqs/{rfq_id}/bbo
method = 'GET'
path = '/v1/grfq/rfqs/579/bbo'

payload = ''

timestamp, signature = sign_request(secret_key=secret_key,
                                    method=method.encode('utf-8'),
                                    path=path.encode('utf-8'),
                                    body=payload.encode('utf-8'),
                                    )

headers = {
          'Paradigm-API-Timestamp': timestamp,
          'Paradigm-API-Signature': signature,
          'Authorization': f'Bearer {access_key}'
           }

# Send request
response = requests.get(
    host+path,
    headers=headers
    )

print(response.status_code)
print(response.text)