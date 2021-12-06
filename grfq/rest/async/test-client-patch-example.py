# built ins
import base64
import hmac
import time
from urllib.parse import urljoin
import asyncio
from typing import Dict, Tuple
import logging
import json

# installed
import aiohttp


class ParadigmAsyncClient:
    def __init__(
        self,
        operating_environment: str,
        access_key: str,
        secret_key: str,
        method: str,
        endpoint: str,
        body: Dict = {}
            ) -> None:
        # Instance Variables
        self.operating_environment: str = operating_environment
        self.access_key: str = access_key
        self.secret_key: str = secret_key
        self.method: str = method.upper()
        self.endpoint: str = endpoint
        self.body: str = body

        # Event Loop
        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()

        # Request Endpoint
        self.loop.run_until_complete(
            self.rest_request()
            )

    @property
    def operating_environment(self):
        return self._operating_environment

    @operating_environment.setter
    def operating_environment(self, value):
        if value in ['TEST', 'test']:
            self._operating_environment = value.lower()
        else:
            self._operating_environment: str = 'test'
            logging.info('Operating Environment set to `test` due to invalid param')

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, value):
        self._method: str = value.upper()

    @property
    def base_http_url(self):
        return f'https://api.{self.operating_environment}.paradigm.co'

    async def sign_request(
        self,
        secret_key: str,
        method: str,
        path: str,
        body: Dict
            ) -> Tuple[int, bytes]:
        """
        Creates the required signature neccessary
        as apart of all RESToverHTTP requests with Paradigm.
        """
        _secret_key: bytes = secret_key.encode('utf-8')
        _method: bytes = method.encode('utf-8')
        _path: bytes = path.encode('utf-8')
        if body:
            body: str = json.dumps(body)
        else:
            body: str = ''
        _body: bytes = body.encode('utf-8')
        signing_key: bytes = base64.b64decode(_secret_key)
        timestamp: str = str(int(time.time() * 1000)).encode('utf-8')
        message: bytes = b'\n'.join([timestamp, _method.upper(), _path, _body])
        digest: hmac.digest = hmac.digest(signing_key, message, 'sha256')
        signature: bytes = base64.b64encode(digest)

        return timestamp, signature

    async def create_rest_headers(self) -> Dict:
        """
        Creates the required headers to authenticate
        Paradigm RESToverHTTP requests.
        """
        timestamp, signature = await self.sign_request(
            secret_key=self.secret_key,
            method=self.method,
            path=self.endpoint,
            body=self.body
            )

        headers: Dict = {
                        'Paradigm-API-Timestamp': timestamp.decode('utf-8'),
                        'Paradigm-API-Signature': signature.decode('utf-8'),
                        'Authorization': f'Bearer {self.access_key}'
                        }

        return headers

    async def http_client(self) -> Tuple[int, Dict]:
        """
        Client used to request Paradigm's API.
        """
        headers: Dict = await self.create_rest_headers()

        async with aiohttp.ClientSession() as session:
            if self.method == 'GET':
                async with session.get(
                    urljoin(self.base_http_url, self.endpoint),
                    headers=headers
                        ) as response:
                    status_code: int = response.status
                    response: Dict = await response.text()
            elif self.method == 'POST':
                async with session.post(
                    urljoin(self.base_http_url, self.endpoint),
                    headers=headers,
                    json=self.body
                        ) as response:
                    status_code: int = response.status
                    response: Dict = await response.text()
            elif self.method == 'PATCH':
                async with session.patch(
                    urljoin(self.base_http_url, self.endpoint),
                    headers=headers,
                    json=self.body
                        ) as response:
                    status_code: int = response.status
                    response: Dict = await response.text()
            elif self.method == 'DELETE':
                async with session.delete(
                    urljoin(self.base_http_url, self.endpoint),
                    headers=headers
                        ) as response:
                    status_code: int = response.status
                    response: Dict = {}

            return status_code, response

    async def rest_request(self) -> None:
        status_code, response = await self.http_client()
        logging.info(f'HTTP Request Response Status: {status_code}')
        logging.info(f'Response: {response}')


if __name__ == "__main__":
    # Logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        )

    # Paradigm Async Client Instantiation
    paradigm_client: ParadigmAsyncClient = ParadigmAsyncClient(
        operating_environment='TEST',
        access_key='KhPv3MCrcWrFzUG3Yk7RlrS8',
        secret_key='x2BRplx4481g0Kt0W4FBZEzpnYPNWGPvkAR67Wg/9fT9wQeL',
        method='PATCH',
        endpoint='/v1/grfq/rfqs/123/quotes/',
        body={
             "account": "ParadigmTestOne",
             "client_order_id": "456",
             "quantity": "500",
             "side": "BUY",
             "legs": [
                 {
                    "instrument": "BTC-PERPETUAL",
                    "price": "45000"
                  }
                ],
             "post_only": True
            }
        )
