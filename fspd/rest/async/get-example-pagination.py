"""
Description:
    Paradigm RESToverHTTP [GET] Asyncio Pagination Example.

Usage:
    python3.9 dbt-authenticated-example.py

SRequirements:
    - aiohttp >= 3.8.1
"""

# built ins
import asyncio
import logging
from typing import Tuple, Dict
import base64
import hmac
import time

# installed
import aiohttp


class main:
    def __init__(
        self,
        connection_url: str,
        endpoint: str,
        access_key: str,
        secret_key: str
            ) -> None:
        self.connection_url: str = connection_url
        self.endpoint: str = endpoint
        self.access_key: str = access_key
        self.secret_key: str = secret_key

        # Instance Variables
        self.cursor: str = ''

        asyncio.get_event_loop().run_until_complete(
            self.manager()
            )

    async def manager(self) -> None:
        """
        Coroutine to manage the async pagination.
        """
        # Initial request
        status_code, response = await self.get_request(
            endpoint=self.endpoint
            )
        # Cursor value
        _cursor: str = response['next']

        if _cursor:
            # Pagination
            while _cursor:
                endpoint: str = f'{self.endpoint}&cursor={_cursor}'
                status_code, response = await self.get_request(
                    endpoint=endpoint
                    )
                logging.info(f'Status Code: {status_code}')

    def sign_request(
        self,
        endpoint: str
            ) -> Tuple[str, base64.b64encode]:
        """
        Creates the request timestamp and Paradigm authentication signature.
        """
        signing_key = base64.b64decode(self.secret_key)
        timestamp = str(int(time.time() * 1000)).encode('utf-8')
        message = b'\n'.join(
            [
                timestamp,
                'GET'.encode('utf-8').upper(),
                endpoint.encode('utf-8'),
                ''.encode('utf-8')
            ]
            )
        digest = hmac.digest(signing_key, message, 'sha256')
        signature = base64.b64encode(digest)
        return timestamp, signature

    def create_headers(
        self,
        timestamp,
        signature: base64.b64encode
            ) -> Dict:
        """
        Returns HTTP headers to be used in a Paradigm request.
        """
        return {
                'Paradigm-API-Timestamp': timestamp.decode('utf-8'),
                'Paradigm-API-Signature': signature.decode('utf-8'),
                'Authorization': f'Bearer {self.access_key}'
                }

    async def get_request(
        self,
        endpoint: str
            ) -> Tuple[int, Dict]:
        """
        - Creates the [GET] request timestamp & signature
        - Creates the headers for the request
        - Returns the response HTTP Status Code and Payload
        """
        # Create request timestamp and signature
        timestamp, signature = self.sign_request(
            endpoint=endpoint
            )
        # Create request headers
        headers: Dict = self.create_headers(
            timestamp=timestamp,
            signature=signature
            )
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.connection_url+endpoint,
                headers=headers
                    ) as resp:
                status_code: int = resp.status
                response: Dict = await resp.json(content_type=None)
                return status_code, response


if __name__ == "__main__":
    # Logging
    logging.basicConfig(
        level='INFO'.upper(),
        format='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
        )

    # Paradigm LIVE RESToverHTTP Connection URL
    # connection_url: str = 'https://api.fs.chat.paradigm.co'
    # Paradigm TEST RESToverHTTP Connection URL
    connection_url: str = 'https://api.fs.test.paradigm.co'

    # Paradigm RESToverHTTP Endpoint + Query String Parameter(s)
    endpoint: str = '/v1/fs/trades?page_size=100'

    # Paradigm Access Key
    access_key: str = '<access-key>'
    # Paradigm Secret Key
    secret_key: str = '<secret-key>'

    main(
        connection_url=connection_url,
        endpoint=endpoint,
        access_key=access_key,
        secret_key=secret_key
        )
