# -*- coding: utf-8 -*-
"""
MIT License
Copyright (c) 2020 Arthur
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

from datetime import datetime
from typing import Union

from .bot import Bot
from .dblstats_auctions import Auctions
from ..utils import represents, AsyncFetcher, endpoints


class Client:
    """
    Represents your dblstatistics.com client.

    This interacts with the api, so it allows you to fetch data.
    """

    def __init__(self, token: str):
        self.__fetcher = AsyncFetcher(token)
        self.auctions = Auctions(self.__fetcher)

    def __repr__(self):
        return represents(self)

    async def get_bot(self, id: Union[int, str]) -> Bot:
        """
        Fetch a bot from the dblstatistics website.

        :param id: The id of the bot that must be fetched.
        """
        bot = await self.__fetcher.get(endpoints.GET_BOT_URL.format(id=id))
        return Bot(bot["certified"], list(map(lambda i: int(i), bot.get("owners"))), bot.get("deleted"), bot.get("id"),
                   bot.get("name"), bot.get("def_avatar"), bot.get("avatar"), bot.get("short_desc"), bot.get("lib"),
                   bot.get("prefix"), bot.get("website"),
                   datetime.strptime(bot.get("approved_at"), "%Y-%m-%dT%H:%M:%S.%fZ"), bot.get("monthly_votes"),
                   bot.get("server_count"), bot.get("total_votes"), bot.get("shard_count"),
                   bot.get("monthly_votes_rank"), bot.get("server_count_rank"), bot.get("total_votes_rank"),
                   bot.get("shard_count_rank"), datetime.strptime(bot.get("timestamp"), "%Y-%m-%dT%H:%M:%S.%fZ"))
