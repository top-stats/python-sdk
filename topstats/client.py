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

from .bot import Bot
from .errors import Error, RequestError, Ratelimited


class Client:
  """
  The class that lets you interact with the API.

  :param token: The API token to use with the API.
  :type token: str
  :param session: Whether to use an existing aiohttp client session for requesting or not. Defaults to ``None`` (creates a new one instead)
  :type session: Optional[:class:`~aiohttp.ClientSession`]

  :raises Error: If ``token`` is ``None``.
  """

  __slots__: Tuple[str, ...] = ('__own_session', '__session', '__token')

  def __init__(self, token: str, *, session: Optional[ClientSession] = None):
    if not token:
      raise Error('An API token is required to use this API.')

    self.__own_session = session is None
    self.__session = session or ClientSession(timeout=ClientTimeout(total=5000.0))
    self.__token = token

  def __repr__(self) -> str:
    return f'<{__class__.__name__} {self.__session!r}>'

  async def __get(
    self, path: str, fetch_bytes: bool = False
  ) -> Optional[Union[BytesIO, dict]]:
    delay = 0.5

    while True:
      json = {}

      try:
        async with self.__session.get(
          f'https://api.topstats.gg{path}', headers={'Authorization': self.__token}
        ) as resp:
          if not fetch_bytes:
            try:
              json = await resp.json()
            except:
              pass

          json['message'] = json.get('message', resp.reason)
          resp.raise_for_status()

          if fetch_bytes:
            return BytesIO(await resp.read())

          return json
      except Exception:
        code = json.get('code')

        if code == 404:
          return None
        elif code == 429:
          raise Ratelimited(json)
        elif delay == 4:
          raise RequestError(json)

        await sleep(delay)
        delay *= 2

  async def get_bot(self, id: int) -> Optional[Bot]:
    """
    Fetches a ranked bot from its ID.

    :param id: The requested ranked bot's ID. This can be ``None``.
    :type id: int

    :exception RequestError: If the aiohttp client session used by the :class:`~.Client` object is already closed, or if the :class:`~.Client` cannot send a web request to the web server.
    :exception Ratelimited: If the client got ratelimited and not allowed to make requests for a period of time.

    :returns: The requested ranked bot. This can be ``None`` if it does not exist.
    :rtype: Optional[:class:`~.bot.Bot`]
    """

    b = await self.__get(f'/bots/{id}')
    return b and Bot(b)

  async def close(self) -> None:
    """Closes the :class:`~.Client` object. Nothing will happen if the client uses a pre-existing :class:`~aiohttp.ClientSession` or if the session is already closed."""

    if self.__own_session and not self.__session.closed:
      await self.__session.close()

  async def __aenter__(self) -> 'Client':
    return self

  async def __aexit__(self, *_, **__) -> None:
    await self.close()
