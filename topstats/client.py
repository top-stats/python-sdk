"""
The MIT License (MIT)

Copyright (c) 2020 Arthurdw
Copyright (c) 2024-2025 null8626

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

from typing import Iterable, Optional, Tuple, Union, Any, Dict
from aiohttp import ClientSession, ClientTimeout
from collections import namedtuple
from asyncio import sleep
from time import time
from re import sub

from .errors import Error, RequestError, Ratelimited
from .bot import Bot, PartialBot, RecentBotStats
from .data import Period, SortBy, Timestamped
from .ratelimiter import Ratelimiter

BASE_URL = 'https://api.topstats.gg/discord'
MAXIMUM_DELAY_THRESHOLD = 5.0


class Client:
  """
  The class that lets you interact with the API.

  :param token: The API token to use with the API. To retrieve your topstats.gg API token, see https://docs.topstats.gg/authentication/tokens/.
  :type token: :py:class:`str`
  :param session: Whether to use an existing :class:`~aiohttp.ClientSession` for requesting or not. Defaults to :py:obj:`None` (creates a new one instead)
  :type session: Optional[:class:`~aiohttp.ClientSession`]

  :exception TypeError: If ``token`` is not a :py:class:`str`.
  """

  __slots__: Tuple[str, ...] = (
    '__own_session',
    '__session',
    '__token',
    '__ratelimiters',
    '__current_ratelimits',
  )

  def __init__(self, token: str, *, session: Optional[ClientSession] = None):
    if not isinstance(token, str) or not token:
      raise TypeError('An API token is required to use this API.')

    self.__own_session = session is None
    self.__session = session or ClientSession(
      timeout=ClientTimeout(total=MAXIMUM_DELAY_THRESHOLD * 1000.0)
    )
    self.__token = token

    endpoint_ratelimits = namedtuple(
      'EndpointRatelimits',
      'bots bots_historical bots_recent compare compare_historical rankings_bots users_bots',
    )

    self.__ratelimiters = endpoint_ratelimits(
      bots=Ratelimiter(59, 60),
      bots_historical=Ratelimiter(59, 60),
      bots_recent=Ratelimiter(59, 60),
      compare=Ratelimiter(59, 60),
      compare_historical=Ratelimiter(59, 60),
      rankings_bots=Ratelimiter(59, 60),
      users_bots=Ratelimiter(59, 60),
    )
    self.__current_ratelimits = endpoint_ratelimits(
      None, None, None, None, None, None, None
    )

  def __repr__(self) -> str:
    return f'<{__class__.__name__} {self.__session!r}>'

  async def __get(
    self,
    path: str,
    default_value: Optional[Any] = None,
    **params: Dict[str, Union[str, int]],
  ) -> Union[Dict[str, Any], Optional[Any]]:
    if self.__session.closed:
      raise Error('Client session is already closed.')

    ratelimiter_key = sub(
      '_{2,}', '_', sub(r'\d+', '', path).strip('/').replace('/', '_')
    )
    current_ratelimit = getattr(self.__current_ratelimits, ratelimiter_key)

    if current_ratelimit is not None:
      current_time = time()

      if current_time < current_ratelimit:
        raise Ratelimited(current_ratelimit - current_time)
      else:
        setattr(self.__current_ratelimits, ratelimiter_key, None)

    ratelimiter = getattr(self.__ratelimiters, ratelimiter_key)

    status = None
    retry_after = None
    json = {}

    async with ratelimiter:
      try:
        async with self.__session.get(
          BASE_URL + path,
          headers={
            'Authorization': self.__token,
            'Content-Type': 'application/json',
            'User-Agent': 'topstats (https://github.com/top-stats/python-sdk 1.1.1) Python/',
          },
          params=params,
        ) as resp:
          status = resp.status
          retry_after = float(json.get('expiresIn', 0)) / 1000.0

          json = await resp.json()

          resp.raise_for_status()

          return json
      except:
        if status == 404:
          return default_value
        elif status == 429 and retry_after is not None:
          if retry_after > MAXIMUM_DELAY_THRESHOLD:
            setattr(self.__current_ratelimits, ratelimiter_key, time() + retry_after)

            raise Ratelimited(retry_after) from None

          await sleep(retry_after)

          return await self.__get(path, default_value=default_value, **params)

        raise RequestError(json.get('message'), status) from None

  @staticmethod
  def __validate_ids(*ids: int) -> Iterable[str]:
    ids = tuple(set(ids))
    ids_len = len(ids)

    if not (2 <= ids_len <= 4):
      raise IndexError(f'Expected 2 to 4 unique bot IDs to compare, but got {ids_len}.')

    return map(str, ids)

  async def get_bot(self, id: int) -> Optional[Bot]:
    """
    Fetches a Discord bot from its ID.

    :param id: The requested bot's ID.
    :type id: :py:class:`int`

    :exception Error: If the :class:`~aiohttp.ClientSession` used by the client is already closed.
    :exception RequestError: If the client received a non-favorable response from the API.
    :exception Ratelimited: If the client got blocked by the API because it exceeded its ratelimits.

    :returns: The requested bot. This can be :py:obj:`None` if it does not exist.
    :rtype: Optional[:class:`.Bot`]
    """

    b = await self.__get(f'/bots/{id}')
    return b and Bot(b)

  async def compare_bots(self, *ids: int) -> Optional[Iterable[Bot]]:
    """
    Fetches and yields several Discord bots from a set of IDs.

    :param ids: Set of bot IDs to compare. The API currently only accepts 2 to 4 IDs.
    :type ids: :py:class:`int`

    :exception IndexError: If the amount of IDs provided are not within range.
    :exception Error: If the :class:`~aiohttp.ClientSession` used by the client is already closed.
    :exception RequestError: If the client received a non-favorable response from the API.
    :exception Ratelimited: If the client got blocked by the API because it exceeded its ratelimits.

    :returns: The requested list of bots to compare. This can be :py:obj:`None` if they do not exist.
    :rtype: Optional[Iterable[:class:`.Bot`]]
    """

    c = await self.__get(f'/compare/{"/".join(Client.__validate_ids(*ids))}')
    return c and map(Bot, c['data'])

  async def get_users_bot(self, id: int) -> Iterable[Bot]:
    """
    Fetches a Discord user's Discord bots from their ID.

    :warning: Data returned by this method may be inaccurate! This is because bots moved to a team will remain on a user's account irrespective of ownership.

    :param id: The requested user's ID.
    :type id: :py:class:`int`

    :exception Error: If the :class:`~aiohttp.ClientSession` used by the client is already closed.
    :exception RequestError: If the client received a non-favorable response from the API.
    :exception Ratelimited: If the client got blocked by the API because it exceeded its ratelimits.

    :returns: The requested list of bots made by this user.
    :rtype: Iterable[:class:`.Bot`]
    """

    b = await self.__get(f'/users/{id}/bots', default_value={})
    return map(Bot, b.get('bots', ()))

  async def __get_historical_bot_stats(
    self, kind: str, id: int, period: Optional[Period]
  ) -> Optional[Iterable[Timestamped]]:
    if not isinstance(period, Period):
      period = Period.ALL_TIME

    response = await self.__get(
      f'/bots/{id}/historical', timeFrame=period.value, type=kind
    )

    return response and (Timestamped(data, kind) for data in response['data'])

  async def __compare_historical_bot_stats(
    self, kind: str, period: Optional[Union[Period, int]], *ids: int
  ) -> Optional[Iterable[Tuple[Timestamped, ...]]]:
    if not isinstance(period, Period):
      if isinstance(period, int):
        ids = period, *ids

      period = Period.ALL_TIME

    ids = tuple(Client.__validate_ids(*ids))
    c = await self.__get(
      f'/compare/historical/{"/".join(ids)}', timeFrame=period.value, type=kind
    )
    d = c['data']

    return c and zip(*((Timestamped(t, kind) for t in d[i]) for i in ids))

  async def get_historical_bot_monthly_votes(
    self, id: int, period: Optional[Period] = None
  ) -> Optional[Iterable[Timestamped]]:
    """
    Fetches and yields a Discord bot's historical monthly vote count for a certain period of time.

    :param id: The requested bot's ID.
    :type id: :py:class:`int`
    :param period: The requested time period. Defaults to :attr:`.Period.ALL_TIME`.
    :type period: Optional[:class:`.Period`]

    :exception Error: If the :class:`~aiohttp.ClientSession` used by the client is already closed.
    :exception RequestError: If the client received a non-favorable response from the API.
    :exception Ratelimited: If the client got blocked by the API because it exceeded its ratelimits.

    :returns: The requested list of this bot's monthly vote counts. This can be :py:obj:`None` if it does not exist.
    :rtype: Optional[Iterable[:class:`.Timestamped`]]
    """

    return await self.__get_historical_bot_stats('monthly_votes', id, period)

  async def compare_bot_monthly_votes(
    self, period: Optional[Union[Period, int]], *ids: int
  ) -> Optional[Iterable[Tuple[Timestamped, ...]]]:
    """
    Fetches and yields several Discord bots' historical monthly vote count for a certain period of time.

    :param period: The requested time period. Defaults to :attr:`.Period.ALL_TIME`. If this argument is an :py:class:`int`, then it will be treated as a bot ID as a part of the second argument.
    :type period: Optional[Union[:class:`.Period`, :py:class:`int`]]
    :param ids: Set of bot IDs to compare. The API currently only accepts 2 to 4 IDs.
    :type ids: :py:class:`int`

    :exception IndexError: If the amount of IDs provided are not within range.
    :exception Error: If the :class:`~aiohttp.ClientSession` used by the client is already closed.
    :exception RequestError: If the client received a non-favorable response from the API.
    :exception Ratelimited: If the client got blocked by the API because it exceeded its ratelimits.

    :returns: The requested list of monthly vote counts to compare. This can be :py:obj:`None` if it does not exist.
    :rtype: Optional[Iterable[Tuple[:class:`.Timestamped`, ...]]]
    """

    return await self.__compare_historical_bot_stats('monthly_votes', period, *ids)

  async def get_historical_bot_total_votes(
    self, id: int, period: Optional[Period] = None
  ) -> Optional[Iterable[Timestamped]]:
    """
    Fetches and yields a Discord bot's historical total vote count for a certain period of time.

    :param id: The requested bot's ID.
    :type id: :py:class:`int`
    :param period: The requested time period. Defaults to :attr:`.Period.ALL_TIME`.
    :type period: Optional[:class:`.Period`]

    :exception Error: If the :class:`~aiohttp.ClientSession` used by the client is already closed.
    :exception RequestError: If the client received a non-favorable response from the API.
    :exception Ratelimited: If the client got blocked by the API because it exceeded its ratelimits.

    :returns: The requested list of this bot's total vote counts. This can be :py:obj:`None` if it does not exist.
    :rtype: Optional[Iterable[:class:`.Timestamped`]]
    """

    return await self.__get_historical_bot_stats('total_votes', id, period)

  async def compare_bot_total_votes(
    self, period: Optional[Union[Period, int]], *ids: int
  ) -> Optional[Iterable[Tuple[Timestamped, ...]]]:
    """
    Fetches and yields several Discord bots' historical total vote count for a certain period of time.

    :param period: The requested time period. Defaults to :attr:`.Period.ALL_TIME`. If this argument is an :py:class:`int`, then it will be treated as a bot ID as a part of the second argument.
    :type period: Optional[Union[:class:`.Period`, :py:class:`int`]]
    :param ids: Set of bot IDs to compare. The API currently only accepts 2 to 4 IDs.
    :type ids: :py:class:`int`

    :exception IndexError: If the amount of IDs provided are not within range.
    :exception Error: If the :class:`~aiohttp.ClientSession` used by the client is already closed.
    :exception RequestError: If the client received a non-favorable response from the API.
    :exception Ratelimited: If the client got blocked by the API because it exceeded its ratelimits.

    :returns: The requested list of total vote counts to compare. This can be :py:obj:`None` if it does not exist.
    :rtype: Optional[Iterable[Tuple[:class:`.Timestamped`, ...]]]
    """

    return await self.__compare_historical_bot_stats('total_votes', period, *ids)

  async def get_historical_bot_server_count(
    self, id: int, period: Optional[Period] = None
  ) -> Optional[Iterable[Timestamped]]:
    """
    Fetches and yields a Discord bot's historical server count for a certain period of time.

    :param id: The requested bot's ID.
    :type id: :py:class:`int`
    :param period: The requested time period. Defaults to :attr:`.Period.ALL_TIME`.
    :type period: Optional[:class:`.Period`]

    :exception Error: If the :class:`~aiohttp.ClientSession` used by the client is already closed.
    :exception RequestError: If the client received a non-favorable response from the API.
    :exception Ratelimited: If the client got blocked by the API because it exceeded its ratelimits.

    :returns: The requested list of this bot's server counts. This can be :py:obj:`None` if it does not exist.
    :rtype: Optional[Iterable[:class:`.Timestamped`]]
    """

    return await self.__get_historical_bot_stats('server_count', id, period)

  async def compare_bot_server_count(
    self, period: Optional[Union[Period, int]], *ids: int
  ) -> Optional[Iterable[Tuple[Timestamped, ...]]]:
    """
    Fetches and yields several Discord bots' historical server count for a certain period of time.

    :param period: The requested time period. Defaults to :attr:`.Period.ALL_TIME`. If this argument is an :py:class:`int`, then it will be treated as a bot ID as a part of the second argument.
    :type period: Optional[Union[:class:`.Period`, :py:class:`int`]]
    :param ids: Set of bot IDs to compare. The API currently only accepts 2 to 4 IDs.
    :type ids: :py:class:`int`

    :exception IndexError: If the amount of IDs provided are not within range.
    :exception Error: If the :class:`~aiohttp.ClientSession` used by the client is already closed.
    :exception RequestError: If the client received a non-favorable response from the API.
    :exception Ratelimited: If the client got blocked by the API because it exceeded its ratelimits.

    :returns: The requested list of server counts to compare. This can be :py:obj:`None` if it does not exist.
    :rtype: Optional[Iterable[Tuple[:class:`.Timestamped`, ...]]]
    """

    return await self.__compare_historical_bot_stats('server_count', period, *ids)

  async def get_recent_bot_stats(self, id: int) -> Optional[RecentBotStats]:
    """
    Fetches recent stats of a Discord bot for the past 30 hours and past month.

    :param id: The requested bot's ID.
    :type id: :py:class:`int`

    :exception Error: If the :class:`~aiohttp.ClientSession` used by the client is already closed.
    :exception RequestError: If the client received a non-favorable response from the API.
    :exception Ratelimited: If the client got blocked by the API because it exceeded its ratelimits.

    :returns: The requested recent bot stats for the past 30 hours and past month. This can be :py:obj:`None` if it does not exist.
    :rtype: Optional[:class:`.RecentBotStats`]
    """

    g = await self.__get(f'/bots/{id}/recent')
    return g and RecentBotStats(g)

  async def get_top_bots(
    self, sort_by: SortBy, *, limit: Optional[int] = None
  ) -> Iterable[PartialBot]:
    """
    Fetches and yields a list of top bots based on a certain criteria.

    :param sort_by: The requested criteria and sorting method.
    :type sort_by: :class:`.SortBy`
    :param limit: Limit of data to be returned. Defaults to ``100``. This can't exceed ``500``.
    :type limit: Optional[:py:class:`int`]

    :exception TypeError: If the requested sorting criteria is of invalid type.
    :exception Error: If the :class:`~aiohttp.ClientSession` used by the client is already closed.
    :exception RequestError: If the client received a non-favorable response from the API.
    :exception Ratelimited: If the client got blocked by the API because it exceeded its ratelimits.

    :returns: The requested list of top bots based on the requested criteria.
    :rtype: Iterable[:class:`.PartialBot`]
    """

    if not isinstance(sort_by, SortBy):
      raise TypeError('The requested sorting criteria is of invalid type.')

    t = await self.__get(
      '/rankings/bots',
      default_value={},
      limit=max(min(limit or 100, 500), 1),
      sortBy=sort_by._SortBy__by,
      sortMethod=sort_by._SortBy__method,
    )
    return map(PartialBot, t.get('data', ()))

  async def close(self) -> None:
    """Closes the :class:`.Client` object. Nothing will happen if the client uses a pre-existing :class:`~aiohttp.ClientSession` or if the session is already closed."""

    if self.__own_session and not self.__session.closed:
      await self.__session.close()

  async def __aenter__(self) -> 'Client':
    return self

  async def __aexit__(self, *_, **__) -> None:
    await self.close()
