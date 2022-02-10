from discord.ext.commands import Cog, command, is_owner
from discord.utils import get
from discord import Embed

from os import execv
from sys import executable, argv
from subprocess import run, PIPE


class Developer(Cog):
    def __init__(self,bot):
        self.bot = bot
        
    @command(name="serverlist")
    async def server_list(self,ctx):
        """Menampilkan seluruh server yang Nadeshiko masuki
        """
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
        """Meninggalkan server berdasar nama servernya

        Args:
            guild_name (str): Nama server yang ingin ditinggalkan
        """
        if not ctx.author.id in self.bot.owner_ids:
            return
        guild = get(self.bot.guilds, name=guild_name)
        if guild is None:
            return ctx.send("Lapor, Tidak ada server dengan nama itu Komandan!")
        await guild.leave() # Guild found
        await ctx.send(f"Nadeshiko meninggalkan **{guild.name}**!")
        
    @command(name="fullrestart")
    async def full_restart(self, ctx):
        """Restart bot dengan menjalankan launcher
        """
        if not ctx.author.id in self.bot.owner_ids:
            return
        await ctx.send("Restarting bot...")
        execv(executable, ['python'] + argv)
        
    @command(name="terminal")
    async def terminal(self, ctx, command):
        """Menjalankan command terminal

        Args:
            command (str): Command yang ingin dijalankan
        """
        if not ctx.author.id in self.bot.owner_ids:
            return
        commands = command.split[' ']
        result = run(commands, stdout= PIPE)
        output = result.stdout.decode('utf-8')
        await ctx.send(output[:2000])
        

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("developer")

def setup(bot):
    bot.add_cog(Developer(bot))