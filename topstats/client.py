"""
The MIT License (MIT)

Copyright (c) 2020 Arthurdw
Copyright (c) 2024 null8626

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from aiohttp import ClientSession, ClientTimeout
from typing import Optional, Union, Tuple
from asyncio import sleep
from io import BytesIO

class Client:
  """
  The class that lets you interact with the API.

  :param token: The API token to use with the API.
  :type token: :py:class:`str`
  :param session: Whether to use an existing aiohttp client session for requesting or not. Defaults to ``None`` (creates a new one instead)
  :type session: Optional[:class:`aiohttp.ClientSession`]

  :raises Error: If ``token`` is ``None``.
  """

  __slots__: Tuple[str, ...] = ('__session', '__token')

  def __init__(self, token: str, *, session: Optional[ClientSession] = None):
    if not token:
      raise Exception('An API token is required to use this API.')

    self.__session = session or ClientSession(timeout=ClientTimeout(total=5000.0))
    self.__token = token
  
  async def __get(self, path: str, fetch_bytes: bool = False) -> Union[BytesIO, dict]:
    delay = 0.5

    while True:
      try:
        async with self.__session.get(
          f'https://topstats.gg/api{path}',
          headers={ 'Authorization': self.__token }
        ) as resp:
          json = {} if fetch_bytes else await resp.json()
          
          if resp.status >= 400:
            raise Exception(f'Error {resp.status}: {json.get("message", "received invalid status code")}')
          elif fetch_bytes:
            return BytesIO(await resp.read())
          
          return json
      except:
        if delay == 4:
          raise

        await sleep(delay)
        delay *= 2
  
  async def close(self):
    """Closes the :class:`Client` object. Nothing will happen if it's already closed."""

    if not self.__session.closed:
      await self.__session.close()

  async def __aenter__(self):
    return self

  async def __aexit__(self, *_, **__):
    await self.close()