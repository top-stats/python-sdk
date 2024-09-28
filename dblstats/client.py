from aiohttp import ClientSession, ClientTimeout
from asyncio import sleep
from io import BytesIO
from typing import Optional, Union

class Client:
  """
  The class that lets you interact with the API.

  :param token: The API token to use with the API.
  :type token: :py:class:`str`
  :param session: Whether to use an existing aiohttp client session for requesting or not. Defaults to ``None`` (creates a new one instead)
  :type session: Optional[:class:`aiohttp.ClientSession`]

  :raises Error: If ``token`` is ``None``.
  """

  __slots__ = ('__session', '__token')

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
          f'https://https://dblstatistics.com/api{path}',
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