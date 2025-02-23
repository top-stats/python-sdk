from sys import stdout
import topstats
import asyncio
import os

INDENTATION = 2


def is_local(data: object) -> bool:
  return getattr(data, '__module__', '').startswith('topstats')


def _test_attributes(obj: object, indent_level: int) -> None:
  for name in getattr(obj.__class__, '__slots__', ()):
    stdout.write(f'{" " * indent_level}{obj.__class__.__name__}.{name}')
    data = getattr(obj, name)

    if isinstance(data, list):
      stdout.write('[0] -> ')

      for i, each in enumerate(data):
        if i > 0:
          stdout.write(f'{" " * indent_level}{obj.__class__.__name__}.{name}[{i}] -> ')

        print(repr(each))
        _test_attributes(each, indent_level + INDENTATION)

      continue

    print(f' -> {data!r}')

    if is_local(data):
      _test_attributes(data, indent_level + INDENTATION)


def test_attributes(obj: object) -> None:
  print(f'{obj!r} -> ')
  _test_attributes(obj, INDENTATION)


async def run() -> None:
  async with topstats.Client(os.getenv('TOPSTATS_TOKEN')) as ts:
    bot = await ts.get_bot(432610292342587392)

    test_attributes(bot)

    bots = await ts.get_top_bots(sort_by=topstats.SortBy.server_count())

    for b in bots:
      test_attributes(b)

    sc = await ts.get_historical_bot_server_count(432610292342587392)

    for server_count in sc:
      test_attributes(server_count)

    vs = await ts.compare_bot_server_count(432610292342587392, 437808476106784770)

    for first, second in vs:
      test_attributes(first)
      test_attributes(second)

    vs2 = await ts.compare_bot_total_votes(
      topstats.Period.LAST_YEAR,
      339254240012664832,
      432610292342587392,
      408785106942164992,
      437808476106784770,
    )

    for first, second, third, fourth in vs2:
      test_attributes(first)
      test_attributes(second)
      test_attributes(third)
      test_attributes(fourth)


if __name__ == '__main__':
  if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

  asyncio.run(run())
