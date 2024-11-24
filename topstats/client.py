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
from typing import List, Optional, Tuple
from asyncio import sleep

from .bot import Bot, PartialBot, RecentBotStats
from .data import Period, SortBy, Timestamped
from .errors import Error, RequestError, Ratelimited


class Client:
  """
  The class that lets you interact with the API.

  :param token: The API token to use with the API.
  :type token: :py:class:`str`
  :param session: Whether to use an existing :class:`~aiohttp.ClientSession` for requesting or not. Defaults to :py:obj:`None` (creates a new one instead)
  :type session: Optional[:class:`~aiohttp.ClientSession`]

  :raises Error: If ``token`` is not a :py:class:`str`.
  """

  __slots__: Tuple[str, ...] = ('__own_session', '__session', '__token')

  def __init__(self, token: str, *, session: Optional[ClientSession] = None):
    if not isinstance(token, str):
      raise Error('An API token is required to use this API.')

    self.__own_session = session is None
    self.__session = session or ClientSession(timeout=ClientTimeout(total=5000.0))
    self.__token = token

  def __repr__(self) -> str:
    return f'<{__class__.__name__} {self.__session!r}>'

  async def __get(self, path: str) -> Optional[dict]:
    delay = 0.5

    while True:
      json = {}

      try:
        async with self.__session.get(
          f'https://api.topstats.gg/discord{path}',
          headers={
            'Authorization': self.__token,
            'Content-Type': 'application/json',
            'User-Agent': 'topstats (https://github.com/top-stats/dblstats.py 1.0.0) Python/',
          },
        ) as resp:
          try:
            json = await resp.json()
          except:
            pass

          json['message'] = json.get('message', resp.reason)
          json['statusCode'] = json.get('statusCode', resp.status)
          resp.raise_for_status()

          return json
      except Exception:
        code = json.get('statusCode')

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

    :param id: The requested ranked bot's ID.
    :type id: :py:class:`int`

    :exception RequestError: If the :class:`~aiohttp.ClientSession` used by the :class:`.Client` object is already closed, or if the :class:`.Client` couldn't send a web request to the web server.
    :exception Ratelimited: If the client got ratelimited and is not allowed to make requests for a period of time.

    :returns: The requested ranked bot. This can be :py:obj:`None` if it does not exist.
    :rtype: Optional[:class:`.Bot`]
    """

    b = await self.__get(f'/bots/{id}')
    return b and Bot(b)

  async def get_users_bot(self, id: int) -> Optional[List[Bot]]:
    """
    Fetches a user's ranked bots from their ID.

    :warning: Data returned by this method may be inaccurate! This is because bots moved to a team will remain on a users account irrespective of ownership.

    :param id: The requested user's ID.
    :type id: :py:class:`int`

    :exception RequestError: If the :class:`~aiohttp.ClientSession` used by the :class:`.Client` object is already closed, or if the :class:`.Client` couldn't send a web request to the web server.
    :exception Ratelimited: If the client got ratelimited and is not allowed to make requests for a period of time.

    :returns: The requested list of ranked bots made by this user. This can be :py:obj:`None` if it does not exist.
    :rtype: Optional[List[:class:`.Bot`]]
    """

    r = await self.__get(f'/users/{id}/bots')
    return r and [Bot(b) for b in r['bots']]

  async def __get_historical_bot_stats(
    self, kind: str, id: int, period: Optional[Period]
  ) -> Optional[List[Timestamped]]:
    if not isinstance(period, Period):
      period = Period.ALL_TIME

    response = await self.__get(
      f'/bots/{id}/historical?timeFrame={period.value}&type={kind}'
    )

    return response and [Timestamped(data, kind) for data in response['data']]

  async def get_historical_bot_monthly_votes(
    self, id: int, period: Optional[Period] = None
  ) -> Optional[List[Timestamped]]:
    """
    Fetches a list of a ranked bot's historical monthly votes for a certain period of time.

    :param id: The requested ranked bot's ID.
    :type id: :py:class:`int`
    :param period: The requested time period. Defaults to :attr:`.Period.ALL_TIME`.
    :type period: Optional[:class:`.Period`]

    :exception RequestError: If the :class:`~aiohttp.ClientSession` used by the :class:`.Client` object is already closed, or if the :class:`.Client` couldn't send a web request to the web server.
    :exception Ratelimited: If the client got ratelimited and is not allowed to make requests for a certain period of time.

    :returns: The requested list of this bot's historical monthly votes. This can be :py:obj:`None` if it does not exist.
    :rtype: Optional[List[:class:`.Timestamped`]]
    """

    return await self.__get_historical_bot_stats('monthly_votes', id, period)

  async def get_historical_bot_total_votes(
    self, id: int, period: Optional[Period] = None
  ) -> Optional[List[Timestamped]]:
    """
    Fetches a list of a ranked bot's historical total votes for a certain period of time.

    :param id: The requested ranked bot's ID.
    :type id: :py:class:`int`
    :param period: The requested time period. Defaults to :attr:`.Period.ALL_TIME`.
    :type period: Optional[:class:`.Period`]

    :exception RequestError: If the :class:`~aiohttp.ClientSession` used by the :class:`.Client` object is already closed, or if the :class:`.Client` couldn't send a web request to the web server.
    :exception Ratelimited: If the client got ratelimited and is not allowed to make requests for a period of time.

    :returns: The requested list of this bot's historical total votes. This can be :py:obj:`None` if it does not exist.
    :rtype: Optional[List[:class:`.Timestamped`]]
    """

    return await self.__get_historical_bot_stats('total_votes', id, period)

  async def get_historical_bot_server_count(
    self, id: int, period: Optional[Period] = None
  ) -> Optional[List[Timestamped]]:
    """
    Fetches a list of a ranked bot's historical server count for a certain period of time.

    :param id: The requested ranked bot's ID.
    :type id: :py:class:`int`
    :param period: The requested time period. Defaults to :attr:`.Period.ALL_TIME`.
    :type period: Optional[:class:`.Period`]

    :exception RequestError: If the :class:`~aiohttp.ClientSession` used by the :class:`.Client` object is already closed, or if the :class:`.Client` couldn't send a web request to the web server.
    :exception Ratelimited: If the client got ratelimited and is not allowed to make requests for a period of time.

    :returns: The requested list of this bot's historical server count. This can be :py:obj:`None` if it does not exist.
    :rtype: Optional[List[:class:`.Timestamped`]]
    """

    return await self.__get_historical_bot_stats('server_count', id, period)

  async def get_historical_bot_shard_count(
    self, id: int, period: Optional[Period] = None
  ) -> Optional[List[Timestamped]]:
    """
    Fetches a list of a ranked bot's historical shard count for a certain period of time.

    :param id: The requested ranked bot's ID.
    :type id: :py:class:`int`
    :param period: The requested time period. Defaults to :attr:`.Period.ALL_TIME`.
    :type period: Optional[:class:`.Period`]

    :exception RequestError: If the :class:`~aiohttp.ClientSession` used by the :class:`.Client` object is already closed, or if the :class:`.Client` couldn't send a web request to the web server.
    :exception Ratelimited: If the client got ratelimited and is not allowed to make requests for a period of time.

    :returns: The requested list of this bot's historical shard count. This can be :py:obj:`None` if it does not exist.
    :rtype: Optional[List[:class:`.Timestamped`]]
    """

    return await self.__get_historical_bot_stats('shard_count', id, period)

  async def get_recent_bot_stats(self, id: int) -> Optional[RecentBotStats]:
    """
    Fetches recent stats of a ranked bot for the past 30 hours and past month.

    :param id: The requested ranked bot's ID.
    :type id: :py:class:`int`

    :exception RequestError: If the :class:`~aiohttp.ClientSession` used by the :class:`.Client` object is already closed, or if the :class:`.Client` couldn't send a web request to the web server.
    :exception Ratelimited: If the client got ratelimited and is not allowed to make requests for a period of time.

    :returns: The requested recent bot stats for the past 30 hours and past month. This can be :py:obj:`None` if it does not exist.
    :rtype: Optional[:class:`.RecentBotStats`]
    """

    g = await self.__get(f'/bots/{id}/recent')
    return g and RecentBotStats(g)

  async def get_top_bots(
    self, sort_by: SortBy, *, limit: Optional[int] = None
  ) -> Optional[List[PartialBot]]:
    """
    Fetches a list of top bots ranked on topstats.gg based on a certain criteria.

    :param sort_by: The requested criteria and sorting method.
    :type sort_by: :class:`.SortBy`
    :param limit: Limit of data to be returned. Defaults to ``100``. This can't exceed ``500``.
    :type limit: Optional[:py:class:`int`]

    :raises Error: If ``sort_by`` is not a :class:`.SortBy`.
    :exception RequestError: If the :class:`~aiohttp.ClientSession` used by the :class:`.Client` object is already closed, or if the :class:`.Client` couldn't send a web request to the web server.
    :exception Ratelimited: If the client got ratelimited and is not allowed to make requests for a period of time.

    :returns: The requested list of top bots ranked on topstats.gg based on the requested criteria. This can be :py:obj:`None` if it does not exist.
    :rtype: Optional[List[:class:`.PartialBot`]]
    """

    if not isinstance(sort_by, SortBy):
      raise Error('The requested criteria is missing or invalid.')

    t = await self.__get(
      f'/rankings/bots?limit={max(min(limit or 100, 500), 1)}&{sort_by.q}'
    )
    return t and [PartialBot(bot) for bot in t['data']]

  async def close(self) -> None:
    """Closes the :class:`.Client` object. Nothing will happen if the client uses a pre-existing :class:`~aiohttp.ClientSession` or if the session is already closed."""

    if self.__own_session and not self.__session.closed:
      await self.__session.close()

  async def __aenter__(self) -> 'Client':
    return self

  async def __aexit__(self, *_, **__) -> None:
    await self.close()
