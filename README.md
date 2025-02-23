# [topstats][pypi-url] [![pypi][pypi-image]][pypi-url] [![downloads][downloads-image]][pypi-url]

[pypi-image]: https://img.shields.io/pypi/v/topstats.svg?style=flat-square
[pypi-url]: https://pypi.org/project/topstats/
[downloads-image]: https://img.shields.io/pypi/dm/topstats?style=flat-square

The community-maintained Python API wrapper for [topstats.gg](https://topstats.gg).

## Installation

```console
pip install topstats
```

## Example

For more information, please read the [documentation](https://topstats.readthedocs.io/en/latest/).

```py
# Import the module.
import topstats

import asyncio
import os


async def main() -> None:
  
  # Declare the client. To retrieve your topstats.gg token, see https://docs.topstats.gg/authentication/tokens/.
  async with topstats.Client(os.getenv('TOPSTATS_TOKEN')) as ts:
    
    # Fetch a bot from its ID.
    bot = await ts.get_bot(432610292342587392)
    
    print(bot)

    # Fetch topstats.gg's top bots.
    bots = await ts.get_top_bots(sort_by=topstats.SortBy.server_count())
    
    for b in bots:
      print(b)
    
    # Fetch a bot's historical server count.
    sc = await ts.get_historical_bot_server_count(432610292342587392)

    for server_count in sc:
      print(server_count)
    
    # Compare two bots' historical server count.
    vs = await ts.compare_bot_server_count(432610292342587392, 437808476106784770)

    for first, second in vs:
      print(first, second)
    
    # Compare up to four bots' historical total vote count.
    vs2 = await ts.compare_bot_total_votes(
      topstats.Period.LAST_YEAR,
      339254240012664832,
      432610292342587392,
      408785106942164992,
      437808476106784770
    )

    for first, second, third, fourth in vs2:
      print(first, second, third, fourth)

if __name__ == '__main__':
  
  # See https://stackoverflow.com/questions/45600579/asyncio-event-loop-is-closed-when-getting-loop
  # for more details.
  if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
  
  asyncio.run(main())
```
