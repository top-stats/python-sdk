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

from typing import Union

from discord import Intents, Member, User
from discord.ext import commands
from utilsx.discord import Cog, BotX
from utilsx.discord.objects import Footer, Field

import dblstats

DISCORD_BOT_TOKEN = "XXXYOURTOKENHEREXXX"
DBLSTATS_TOKEN = "XXXYOURTOKENHEREXXX"


class Bot(BotX):
    def __init__(self):
        super().__init__(Intents.all())
        self.add_cog(DBLStatsExtension(self))

    async def on_ready(self):
        print(f"Successfully started bot on {self.user.name}")


class DBLStatsExtension(Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.dblstats = dblstats.Client(DBLSTATS_TOKEN)

    @commands.command(name="bot")
    async def bot(self, ctx: commands.Context, target: Union[Member, User, int] = None):
        if target is None:
            return await self.embed(ctx, "Please provide a target!")

        id = target if isinstance(target, int) else target.id
        bot = await self.dblstats.get_bot(id)
        field_message = f"Owners: {', '.join(['<@' + str(owner) + '>' for owner in bot.owners])}\n" \
                        f"Library: `{bot.library}`\n" \
                        f"Prefix: `{bot.prefix}`\n" \
                        f"```" \
                        f"Montly Votes: {bot.monthly_votes}\tMonthly Votes Rank: {bot.monthly_votes_rank}\n" \
                        f"Server Count: {bot.server_count}\tServer Count Rank: {bot.server_count_rank}\n" \
                        f"Total Votes: {bot.total_votes}\tTotal Votes Rank: {bot.total_votes_rank}\n" \
                        f"Shard Count: {bot.shard_count}\tShard Count Rank: {bot.shard_count_rank}" \
                        f"```\n" \
                        f"Approved on {bot.approved_at.utcnow()}"
        await self.embed(ctx, bot.short_description, title=f"About {bot.name}:",
                         footer=Footer(text=bot.website, icon_url=bot.avatar),
                         fields=[Field(name="Top.gg Information", value=field_message)])


if __name__ == "__main__":
    Bot().run(DISCORD_BOT_TOKEN)
