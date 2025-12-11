from os import getenv, path
import sys

sys.path.insert(0, path.join(path.dirname(path.realpath(__file__)), '..'))


from typing import AsyncGenerator, TYPE_CHECKING
from collections import deque
from time import time
import pytest_asyncio
import pytest

import topstats

from util import _test_attributes, RequestMock


@pytest_asyncio.fixture
async def client(
  monkeypatch: pytest.MonkeyPatch,
) -> AsyncGenerator[topstats.Client, None]:
  token = getenv('TOPSTATS_TOKEN')

  if TYPE_CHECKING:
    assert token is not None, 'Missing topstats.gg API token'

  client = topstats.Client(token)

  monkeypatch.setattr(topstats.Ratelimiter, '_calls', deque([time()]))

  yield client
  await client.close()


def test_Client_attributes_work(client: topstats.Client) -> None:
  _test_attributes(client)


@pytest.mark.asyncio
async def test_Client_get_bot_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topstats.Client,
) -> None:
  with RequestMock(200, 'OK', 'mocks/get_bot.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.get', request)

    bot = await client.get_bot(432610292342587392)

    _test_attributes(bot)

    request.assert_called_once()


@pytest.mark.asyncio
async def test_Client_get_top_bots_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topstats.Client,
) -> None:
  with RequestMock(200, 'OK', 'mocks/get_top_bots.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.get', request)

    bots = await client.get_top_bots(sort_by=topstats.SortBy.server_count())

    for bot in bots:
      _test_attributes(bot)

    request.assert_called_once()


@pytest.mark.asyncio
async def test_Client_get_recent_bot_stats_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topstats.Client,
) -> None:
  with RequestMock(200, 'OK', 'mocks/get_recent_bot_stats.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.get', request)

    stats = await client.get_recent_bot_stats(1026525568344264724)

    _test_attributes(stats)

    request.assert_called_once()


@pytest.mark.asyncio
async def test_Client_search_bots_by_name_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topstats.Client,
) -> None:
  with RequestMock(200, 'OK', 'mocks/search_bots_by_name.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.get', request)

    bots = await client.search_bots(name='MEE6')

    for bot in bots:
      _test_attributes(bot)

    request.assert_called_once()


@pytest.mark.asyncio
async def test_Client_search_bots_by_tag_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topstats.Client,
) -> None:
  with RequestMock(200, 'OK', 'mocks/search_bots_by_tag.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.get', request)

    bots = await client.search_bots(tag='anime')

    for bot in bots:
      _test_attributes(bot)

    request.assert_called_once()


@pytest.mark.parametrize(
  'ty', ('monthly_votes', 'review_count', 'server_count', 'total_votes')
)
@pytest.mark.asyncio
async def test_Client_get_historical_bot_works(
  monkeypatch: pytest.MonkeyPatch, client: topstats.Client, ty: str
) -> None:
  with RequestMock(200, 'OK', f'mocks/get_historical_bot_{ty}.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.get', request)

    method = getattr(client, f'get_historical_bot_{ty}')
    bots = await method(432610292342587392)

    for bot in bots:
      _test_attributes(bot)

    request.assert_called_once()


@pytest.mark.parametrize(
  'ty', ('monthly_votes', 'review_count', 'server_count', 'total_votes')
)
@pytest.mark.asyncio
async def test_Client_compare_bot_works(
  monkeypatch: pytest.MonkeyPatch, client: topstats.Client, ty: str
) -> None:
  with RequestMock(200, 'OK', f'mocks/compare_bot_{ty}.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.get', request)

    method = getattr(client, f'compare_bot_{ty}')
    vs = await method(432610292342587392, 437808476106784770)

    for first, second in vs:
      _test_attributes(first)
      _test_attributes(second)

    request.assert_called_once()


@pytest.mark.asyncio
async def test_Client_compare_bot_total_votes_4x_works(
  monkeypatch: pytest.MonkeyPatch, client: topstats.Client
) -> None:
  with RequestMock(200, 'OK', 'mocks/compare_bot_total_votes_4x.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.get', request)

    vs = await client.compare_bot_total_votes(
      topstats.Period.LAST_YEAR,
      339254240012664832,
      432610292342587392,
      408785106942164992,
      437808476106784770,
    )

    for first, second, third, fourth in vs:
      _test_attributes(first)
      _test_attributes(second)
      _test_attributes(third)
      _test_attributes(fourth)

    request.assert_called_once()
