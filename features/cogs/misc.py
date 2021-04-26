from discord.ext.commands import Cog, CheckFailure, command, has_permissions

from ..db import db

class Misc(Cog):
    def __init__(self,bot):
        self.bot = bot

    @command(name="prefix")
    @has_permissions(manage_guild=True)
    async def change_prefix(self, ctx, new:str):
        """Mengganti prefix server (default= **+**)
        
        Contoh:
        ```prefix %```
        """
        if len(new) > 5:
            await ctx.send("Prefixnya terlalu panjang")

        else:
            db.execute("UPDATE guilds SET Prefix = ? WHERE GuildID = ?", new, ctx.guild.id)
            await ctx.send(f"Prefix server diubah menjadi {new}")


    @change_prefix.error
    async def change_prefix_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Kakak tidak berhak melakukan perintah itu")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("misc")


def setup(bot):
    bot.add_cog(Misc(bot))