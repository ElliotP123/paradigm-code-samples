# built ins
import base64
import hmac
import time

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
host = 'https://api.fs.test.paradigm.co'

# DELETE /v1/fs/orders/{order_id}
method = 'DELETE'
path = '/v1/fs/orders/123'

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
response = requests.delete(
    host+path,
    headers=headers
    )

print(response.status_code)
print(response.text)