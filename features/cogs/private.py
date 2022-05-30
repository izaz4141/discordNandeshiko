from discord.ext.commands import Cog, command
from typing import Optional

from asyncio import get_event_loop

from ..utils.menkrep import get_status

class Private(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="mcstatus")
    async def minecraft_server_status(self, ctx, *, link: Optional[str]):
        """Mengambil status dari server minecraft

        Args:
            link (Optional[str]): Link server minecraft, jika tidak diisi akan mengambil server elang.
        """
        if not ctx.author.id in self.bot.owner_ids:
            return
        loop = self.bot.loop or get_event_loop()
        link = link or None
        embed = await loop.run_in_executor(None, lambda: get_status(link))
        await ctx.send(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("private")

def setup(bot):
    bot.add_cog(Private(bot))