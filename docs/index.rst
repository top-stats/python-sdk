.. topstats documentation master file, created by
   sphinx-quickstart on Sat Oct 14 19:20:61 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=========
topstats_
=========

|pypi|_ |downloads|_

.. _topstats: https://pypi.org/project/topstats/
.. |pypi| image:: https://img.shields.io/pypi/v/topstats.svg?style=flat-square
.. _pypi: https://pypi.org/project/topstats/
.. |downloads| image:: https://img.shields.io/pypi/dm/topstats?style=flat-square
.. _downloads: https://pypi.org/project/topstats/

A simple API wrapper for `topstats.gg <https://topstats.gg/>`_ written in Python.

Getting started
---------------

Make sure you already have an API token handy. See `this page <https://docs.topstats.gg/authentication/tokens>_` on how to retrieve it.

After that, run the following command in your terminal:

.. code-block:: console

  $ pip install topstats

Examples
--------

.. code-block:: python

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

.. toctree::
   :maxdepth: 2
   :hidden:

   client
   bot
   support-server
   repository
   raw-api-reference