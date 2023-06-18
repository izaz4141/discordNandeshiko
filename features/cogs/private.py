from discord.ext.commands import Cog, command
from typing import Optional
# from tenacity import retry, stop_after_attempt, wait_fixed
from asyncio import get_event_loop

from ..utils.menkrep import get_status_2

class Private(Cog):
    def __init__(self, bot):
        self.bot = bot

    # @retry(stop=stop_after_attempt(5), wait=wait_fixed(1))
    async def passive_mc_status(self, ctx, link):
        link = link or None
        embed, online = await get_status_2(link)
        await ctx.send(embed=embed)

    @command(name="mcstatus", aliases= ["mcs"])
    async def minecraft_server_status(self, ctx, *, link: Optional[str]):
        """Mengambil status dari server java minecraft

        Args:
            link (Optional[str]): Link server minecraft, jika tidak diisi akan mengambil server elang.
        """
        if not ctx.author.id in self.bot.owner_ids:
            return
        await self.passive_mc_status(ctx, link)
        

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("private")

def setup(bot):
    bot.add_cog(Private(bot))