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

from discord import Intents
from discord.ext import commands
from utilsx.discord import Cog, BotX

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

    @commands.group(name="auction", aliases=["auctions", "ac", "auc"], invoke_without_command=True)
    async def auction_group(self, ctx):
        """Receive statistics about the Top.gg auctions."""
        await self.embed(ctx, "Please use a valid subcommand.\n"
                              f"See `{self.bot.get_default_prefix()}help {ctx.command.qualified_name}`")

    @auction_group.command(name="tags")
    async def tags(self, ctx: commands.Context):
        tags = await self.dblstats.auctions.get_tags()
        await self.embed(ctx, ", ".join(tags.bot), title="Bot tags", color=0xff131a)

    @auction_group.command(name="current")
    async def current(self, ctx: commands.Context):
        bets = await self.dblstats.auctions.get_current()

        bot_msg = ""
        for idx, (topic, users) in enumerate(bets.bot.items()):
            if idx >= 10:
                break
            bot_msg += f"{topic}: **{len(users)}** bidders\n"

        await self.embed(ctx, bot_msg, title="Most recent bot bets. (10)", color=0xff131a)


if __name__ == "__main__":
    Bot().run(DISCORD_BOT_TOKEN)
