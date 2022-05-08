from discord.ext.commands import Cog, CheckFailure, command, has_permissions
import asyncio

from ..db import db

PILIHAN = {
    u"\u2705" : 0,
    u"\U0001F6AB" : 1
}

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
            
    @command(name="log_on")
    @has_permissions(manage_messages=True)
    async def log_on(self, ctx):
        def _check(r, u):
            return (
                r.emoji in PILIHAN.keys()
                and u == ctx.author
                and r.message.id == msg.id
            )
        msg = await ctx.send("Apakah kakak ingin menghidupkan dan mengubah channel ini menjadi channel log?")
        await msg.add_reaction(u"\u2705")
        await msg.add_reaction(u"\U0001F6AB")
        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=_check)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send("Perintah Log ON dibatalkan")
        else:
            if PILIHAN[reaction.emoji] == 0:
                db.execute("UPDATE guilds set Leg = ? WHERE GuildID = ?", 'ON', ctx.guild.id)
                db.execute("UPDATE guilds set LogChannel = ? WHERE GuildID = ?", ctx.channel.id, ctx.guild.id)
                await ctx.send(f"Fungsi Log bot diaktifkan pada Channel {ctx.channel.name}")
    
    @command(name="log_off")
    @has_permissions(manage_messages=True)
    async def log_off(self,ctx):
        db.execute("UPDATE guilds set Leg = ? WHERE GuildID = ?", 'OFF', ctx.guild.id)
        await ctx.send("Mematikan fungsi log bot...")
        
    @command(name= "welcome_on")
    @has_permissions(manage_messages=True)
    async def welcome_on(self,ctx):
        def _check(r, u):
            return (
                r.emoji in PILIHAN.keys()
                and u == ctx.author
                and r.message.id == msg.id
            )
        msg = await ctx.send("Apakah kakak ingin menghidupkan dan mengubah channel ini menjadi channel welcome?")
        await msg.add_reaction(u"\u2705")
        await msg.add_reaction(u"\U0001F6AB")
        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=_check)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send("Perintah Welcome ON dibatalkan")
        else:
            if PILIHAN[reaction.emoji] == 0:
                db.execute("UPDATE guilds set Welcome = ? WHERE GuildID = ?", 'ON', ctx.guild.id)
                db.execute("UPDATE guilds set WelChannel = ? WHERE GuildID = ?", ctx.channel.id, ctx.guild.id)
                await ctx.send(f"Fungsi Welcome bot diaktifkan pada Channel {ctx.channel.name}")
                
    @command(name="welcome_off")
    @has_permissions(manage_messages=True)
    async def welcome_off(self,ctx):
        db.execute("UPDATE guilds set Welcome = ? WHERE GuildID = ?", 'OFF', ctx.guild.id)
        await ctx.send("Mematikan fungsi Welcome bot...")
        
    @command(name="nqn_on")
    @has_permissions(manage_messages=True)
    async def NQN_ON(self,ctx):
        db.execute("UPDATE guilds set NQN = ? WHERE GuildID = ?", 'ON', ctx.guild.id)
        await ctx.send("Menghidupkan fungsi NQN bot...")
        
    @command(name="nqn_off")
    @has_permissions(manage_messages=True)
    async def NQN_OFF(self,ctx):
        db.execute("UPDATE guilds set NQN = ? WHERE GuildID = ?", 'OFF', ctx.guild.id)
        await ctx.send("Mematikan fungsi NQN bot...")
            
    @Cog.listener()
    async def on_guild_join(self, guild):
        self.bot.update_db()
    async def on_guild_remove(self,guild):
        self.bot.update_db()
    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("misc")


def setup(bot):
    bot.add_cog(Misc(bot))