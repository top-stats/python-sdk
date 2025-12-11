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
async def test_Client_basic_error_handling_works() -> None:
  with pytest.raises(TypeError, match='^An API token is required to use this API.$'):
    async with topstats.Client(''):
      pass

  with pytest.raises(topstats.Error, match='^Client session is already closed.$'):
    token = getenv('TOPSTATS_TOKEN')

    if TYPE_CHECKING:
      assert token is not None, 'Missing topstats.gg API token'

    test_client = topstats.Client(token)

    await test_client.close()
    await test_client.get_bot(432610292342587392)


@pytest.mark.asyncio
async def test_Client_request_error_handling_works(
  monkeypatch: pytest.MonkeyPatch, client: topstats.Client
) -> None:
  with RequestMock(
    404,
    'Not Found',
    {
      'code': 404,
      'message': 'User does not exist, or no data exists for the provided id.',
    },
  ) as request:
    monkeypatch.setattr('aiohttp.ClientSession.get', request)

    with pytest.raises(
      topstats.RequestError,
      match="^Got 404: 'User does not exist, or no data exists for the provided id.'$",
    ) as raises:
      await client.get_bot(432610292342587392)

    _test_attributes(raises.value)

    request.assert_called_once()

  with RequestMock(429, 'Ratelimited', {'expiresIn': 6000}) as request:
    monkeypatch.setattr('aiohttp.ClientSession.get', request)

    for _ in range(2):
      with pytest.raises(
        topstats.Ratelimited,
        match='^The client is blocked by the API. Please try again in ',
      ) as raises:
        await client.get_bot(432610292342587392)

      _test_attributes(raises.value)
      assert 0 <= (6.0 - raises.value.retry_after) < 0.001

    request.assert_called_once()


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


@pytest.mark.parametrize(
  'sort_by_type', ('monthly_votes', 'total_votes', 'server_count', 'review_count')
)
@pytest.mark.asyncio
async def test_Client_get_top_bots_works(
  monkeypatch: pytest.MonkeyPatch, client: topstats.Client, sort_by_type: str
) -> None:
  sort_by = getattr(topstats.SortBy, sort_by_type)

  with RequestMock(200, 'OK', 'mocks/get_top_bots.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.get', request)

    bots = await client.get_top_bots(sort_by=sort_by())

    for bot in bots:
      _test_attributes(bot)

    request.assert_called_once()


@pytest.mark.asyncio
async def test_Client_get_users_bot_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topstats.Client,
) -> None:
  with RequestMock(200, 'OK', 'mocks/get_users_bot.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.get', request)

    bots = await client.get_users_bot(121919449996460033)

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
  with pytest.raises(
    topstats.Error, match='^Either a bot name or tag must be specified.$'
  ):
    await client.search_bots()

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
  method = getattr(client, f'get_historical_bot_{ty}')

  with RequestMock(200, 'OK', f'mocks/get_historical_bot_{ty}.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.get', request)

    bots = await method(432610292342587392)

    for bot in bots:
      _test_attributes(bot)

    request.assert_called_once()


@pytest.mark.asyncio
async def test_Client_compare_bot_works(
  monkeypatch: pytest.MonkeyPatch, client: topstats.Client
) -> None:
  with pytest.raises(
    IndexError, match='^Expected 2 to 4 unique bot IDs to compare, but got '
  ):
    await client.compare_bots()

  with pytest.raises(
    IndexError, match='^Expected 2 to 4 unique bot IDs to compare, but got '
  ):
    await client.compare_bots(1026525568344264724)

  with RequestMock(200, 'OK', 'mocks/compare_bots.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.get', request)

    bots = await client.compare_bots(1026525568344264724, 432610292342587392)

    for bot in bots:
      _test_attributes(bot)

    request.assert_called_once()


@pytest.mark.parametrize(
  'ty', ('monthly_votes', 'review_count', 'server_count', 'total_votes')
)
@pytest.mark.asyncio
async def test_Client_specific_compare_bot_works(
  monkeypatch: pytest.MonkeyPatch, client: topstats.Client, ty: str
) -> None:
  method = getattr(client, f'compare_bot_{ty}')

  with RequestMock(200, 'OK', f'mocks/compare_bot_{ty}.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.get', request)

    vs = await method(432610292342587392, 437808476106784770)

    for first, second in vs:
      _test_attributes(first)
      _test_attributes(second)

    request.assert_called_once()


@pytest.mark.asyncio
async def test_Client_compare_bot_total_votes_4x_works(
  monkeypatch: pytest.MonkeyPatch, client: topstats.Client
) -> None:
  period = topstats.Period.LAST_YEAR

  _test_attributes(period)

  with RequestMock(200, 'OK', 'mocks/compare_bot_total_votes_4x.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.get', request)

    vs = await client.compare_bot_total_votes(
      period,
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
