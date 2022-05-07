from discord.ext.commands import Cog, command, is_owner
from discord.utils import get
from discord import Embed

from os import execv
from sys import executable, argv
from subprocess import run, PIPE
from datetime import datetime
import asyncio



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
        embed.set_thumbnail(url=ctx.guild.me.avatar.url)
        await ctx.send(embed=embed)
        
    @command(name="server_info")
    async def ser_inf(self, ctx, *, nama):
        """Memberikan info server dengan input nama

        Args:
            nama (str): Nama Server
        """
        servers = {}
        for guild in self.bot.guilds:
            servers[guild.name] = guild.id
        if not nama in servers.keys():
            return await ctx.send(f"Maaf kak server dengan nama {nama} tidak ditemukan...")
        guild = self.bot.get_guild(servers[nama])
        embed = Embed(title="Server information",
                      colour=guild.owner.colour,
                      timestamp=datetime.utcnow())
        try:
            embed.set_thumbnail(url=guild.icon.url)
        except Exception:
            pass

        statuses = [len(list(filter(lambda m: str(m.status) == "online", guild.members))),
                    len(list(filter(lambda m: str(m.status) == "idle", guild.members))),
                    len(list(filter(lambda m: str(m.status) == "dnd", guild.members))),
                    len(list(filter(lambda m: str(m.status) == "offline", guild.members)))]

        fields = [("ID", guild.id, True),
                ("Owner", guild.owner, False),
                ("Region", guild.region, True),
                ("Created at", guild.created_at.strftime("%d/%m/%Y %H:%M:%S"), False),
                ("Members", len(guild.members), True),
                ("Humans", len(list(filter(lambda m: not m.bot, guild.members))), True),
                ("Bots", len(list(filter(lambda m: m.bot, guild.members))), True),
                ("Banned members", len(await guild.bans().flatten()), True),
                ("Invites", len(await guild.invites()), True),
                ("Text channels", len(guild.text_channels), True),
                ("Voice channels", len(guild.voice_channels), True),
                ("Categories", len(guild.categories), True),
                ("Roles", len(guild.roles), True),
                ("Statuses", f"🟢 {statuses[0]} 🟠 {statuses[1]} 🔴 {statuses[2]} ⚪ {statuses[3]}", True),
                ("\u200b", "\u200b", True)]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        await ctx.send(embed=embed)
        
        
        
    @command(name="leaveguild")
    async def leave_guild(self, ctx, *, guild_name):
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
    async def terminal(self, ctx, *, command):
        """Menjalankan command terminal

        Args:
            command (str): Command yang ingin dijalankan
        """
        if not ctx.author.id in self.bot.owner_ids:
            return
        commands = command.split(' ')
        loop = self.bot.loop or asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: run(commands, stdout= PIPE))
        output = result.stdout.decode('utf-8')
        await ctx.send(output[:2000])
        

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("developer")

def setup(bot):
    bot.add_cog(Developer(bot))