from typing import Union

from discord import User, Member, Intents, File
from discord.ext import commands
from discord.ext.commands import Context
from utilsx.discord import BotX, Cog

from dblstats import Client as DBLStatsClient, widgets

DISCORD_BOT_TOKEN = "XXXYOURTOKENHEREXXX"
DBLSTATS_TOKEN = "XXXYOURTOKENHEREXXX"


class Bot(BotX):
    def __init__(self):
        super().__init__(Intents.all())
        self.add_cog(Widgets(self))

    async def on_ready(self):
        print(f"Successfully started bot on {self.user.name}")


class Widgets(Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.dblstats = DBLStatsClient(DBLSTATS_TOKEN)

        self.servers_widget = widgets.Widget(widgets.WidgetType.servers)
        self.total_votes_widget = widgets.Widget(widgets.WidgetType.total_votes)
        self.monthly_votes_widget = widgets.Widget(widgets.WidgetType.monthly_votes)
        self.shard_count_widget = widgets.Widget(widgets.WidgetType.shard_count)
        self.ranks_widget = widgets.RanksWidget()

    @staticmethod
    def get_bot_id(bot: Union[User, Member, int, str]):
        return str(bot if not isinstance(bot, (User, Member)) else bot.id)

    async def send_file_embedded(self, ctx: Context, file: File, name: str):
        embed = await self.embed(ctx, "", image=f"attachment://{name}", get_embed=True)
        await self.send(ctx, "", embed=embed, file=file)

    @commands.group(name="widget", invoke_without_command=True)
    async def widget(self, ctx: Context, bot: Union[User, Member, int, str] = None):
        if not bot or not ctx.invoked_subcommand:
            return await self.embed(ctx, "Please use a valid subcommand or provide a bot")
        await self.widget_servers(ctx, bot)

    @widget.command(name="servers")
    async def widget_servers(self, ctx: Context, bot: Union[User, Member, int, str]):
        file, name = await self.dblstats.get_widget_file(self.get_bot_id(bot), self.servers_widget)
        await self.send_file_embedded(ctx, file, name)

    @widget.command(name="total_votes")
    async def widget_total_votes(self, ctx: Context, bot: Union[User, Member, int, str]):
        file, name = await self.dblstats.get_widget_file(self.get_bot_id(bot), self.total_votes_widget)
        await self.send_file_embedded(ctx, file, name)

    @widget.command(name="monthly_votes")
    async def widget_monthly_votes(self, ctx: Context, bot: Union[User, Member, int, str]):
        file, name = await self.dblstats.get_widget_file(self.get_bot_id(bot), self.monthly_votes_widget)
        await self.send_file_embedded(ctx, file, name)

    @widget.command(name="shard_count")
    async def widget_shard_count(self, ctx: Context, bot: Union[User, Member, int, str]):
        file, name = await self.dblstats.get_widget_file(self.get_bot_id(bot), self.shard_count_widget)
        await self.send_file_embedded(ctx, file, name)

    @widget.command(name="ranks")
    async def widget_ranks(self, ctx: Context, bot: Union[User, Member, int, str]):
        file, name = await self.dblstats.get_widget_file(self.get_bot_id(bot), self.ranks_widget)
        await self.send_file_embedded(ctx, file, name)


if __name__ == "__main__":
    Bot().run(DISCORD_BOT_TOKEN)
