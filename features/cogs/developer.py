from discord.ext.commands import Cog, command
from discord.utils import get
from discord import Embed


class Developer(Cog):
    def __init__(self,bot):
        self.bot = bot
        
    @command(name="serverlist")
    async def server_list(self,ctx):
        if not ctx.author.id in self.bot.owner_ids:
            return
        embed = Embed(title= "Server List",
                      colour= ctx.author.colour)
        
        servers = []
        for guild in self.bot.guilds:
            embed.add_field(name=guild.name,
                            value= f"Members: {len(list(filter(lambda m: not m.bot, guild.members)))}\nBots: {len(list(filter(lambda m: m.bot, guild.members)))}")
        embed.set_thumbnail(url=ctx.guild.me.avatar_url)
        await ctx.send(embed=embed)
        
    @command(name="leaveguild")
    async def leave_guild(self, ctx, guild_name):
        guild = get(self.bot.guilds, name=guild_name)
        if guild is None:
            return ctx.send("Lapor, Tidak ada server dengan nama itu Komandan!")
        await guild.leave() # Guild found
        await ctx.send(f"Nadeshiko meninggalkan **{guild.name}**!")
        
    @Cog.listener()
    async def on_message(self, message):
        if message.author.id in self.bot.owner_ids:
            if message.content == "update db" :
                self.bot.update_db_intoCloud()
        

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("developer")

def setup(bot):
    bot.add_cog(Developer(bot))