from datetime import datetime
import asyncio

from discord import Embed, Colour
from discord.errors import Forbidden
from discord.ext.commands import Cog
from discord.ext.commands import command, has_permissions

from ..db import db

PILIHAN = {
    u"\u2705" : 0,
    u"\U0001F6AB" : 1
}

class Log(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log = {}
        
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
        
        
    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            # self.log_channel = self.bot.get_channel(823774055134920765)
            self.bot.cogs_ready.ready_up("log")

    @Cog.listener()
    async def on_user_update(self, before, after):
        if before.name != after.name:
            embed = Embed(title="Username change",
                            colour=after.colour,
                            timestamp=datetime.utcnow())

            fields = [("Before", before.name, False),
                        ("After", after.name, False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
            wic = []
            for guild in self.bot.guilds:
                if guild.get_member(before.id):
                    wic.append(guild.id)
            for gid in wic:
                log_channel = db.field("SELECT LogChannel FROM guilds WHERE GuildID = ?", gid)
                if db.field("SELECT Leg FROM guilds WHERE GuildID = ?", gid) == 'ON':
                    await self.bot.get_channel(log_channel).send(embed=embed)

        if before.discriminator != after.discriminator:
            embed = Embed(title="Discriminator change",
                            colour=after.colour,
                            timestamp=datetime.utcnow())

            fields = [("Before", before.discriminator, False),
                        ("After", after.discriminator, False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            wic = []
            for guild in self.bot.guilds:
                if guild.get_member(before.id):
                    wic.append(guild.id)
            for gid in wic:
                log_channel = db.field("SELECT LogChannel FROM guilds WHERE GuildID = ?", gid)
                if db.field("SELECT Leg FROM guilds WHERE GuildID = ?", gid) == 'ON':
                    await self.bot.get_channel(log_channel).send(embed=embed)

        if before.avatar_url != after.avatar_url:
            embed = Embed(title="Avatar change",
                            description="New image is below, old to the right.",
                            colour=Colour.dark_gold(),
                            timestamp=datetime.utcnow())

            embed.set_thumbnail(url=before.avatar_url)
            embed.set_image(url=after.avatar_url)

            wic = []
            for guild in self.bot.guilds:
                if guild.get_member(before.id):
                    wic.append(guild.id)
            for gid in wic:
                log_channel = db.field("SELECT LogChannel FROM guilds WHERE GuildID = ?", gid)
                if db.field("SELECT Leg FROM guilds WHERE GuildID = ?", gid) == 'ON':
                    await self.bot.get_channel(log_channel).send(embed=embed)

    @Cog.listener()
    async def on_member_update(self, before, after):
        if before.display_name != after.display_name:
            embed = Embed(title="Nickname change",
                            colour=after.colour,
                            timestamp=datetime.utcnow())

            fields = [("Before", before.display_name, False),
                        ("After", after.display_name, False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            wic = []
            for guild in self.bot.guilds:
                if guild.get_member(before.id):
                    wic.append(guild.id)
            for gid in wic:
                log_channel = db.field("SELECT LogChannel FROM guilds WHERE GuildID = ?", gid)
                if db.field("SELECT Leg FROM guilds WHERE GuildID = ?", gid) == 'ON':
                    await self.bot.get_channel(log_channel).send(embed=embed)

        elif before.roles != after.roles:
            embed = Embed(title="Role updates",
                            colour=after.colour,
                            timestamp=datetime.utcnow())

            fields = [("Before", ", ".join([r.mention for r in before.roles]), False),
                        ("After", ", ".join([r.mention for r in after.roles]), False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            wic = []
            for guild in self.bot.guilds:
                if guild.get_member(before.id):
                    wic.append(guild.id)
            for gid in wic:
                log_channel = db.field("SELECT LogChannel FROM guilds WHERE GuildID = ?", gid)
                if db.field("SELECT Leg FROM guilds WHERE GuildID = ?", gid) == 'ON':
                    await self.bot.get_channel(log_channel).send(embed=embed)

    # @Cog.listener()
    # async def on_message_edit(self, before, after):
    #     if not after.author.bot:
    #         if before.content != after.content:
    #             embed = Embed(title="Message edit",
    #                         description=f"Edit by {after.author.display_name}.",
    #                         colour=after.author.colour,
    #                         timestamp=datetime.utcnow())

    #             fields = [("Before", before.content, False),
    #                     ("After", after.content, False)]

    #             for name, value, inline in fields:
    #                 embed.add_field(name=name, value=value, inline=inline)

    #             await self.log_channel.send(embed=embed)

    # @Cog.listener()
    # async def on_message_delete(self, message):
    #     if not message.author.bot:
    #         embed = Embed(title="Message deletion",
    #                     description=f"Action by {message.author.display_name}.",
    #                     colour=message.author.colour,
    #                     timestamp=datetime.utcnow())

    #         fields = [("Content", message.content, False)]

    #         for name, value, inline in fields:
    #             embed.add_field(name=name, value=value, inline=inline)

    #         await self.log_channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Log(bot))