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
            embed.set_footer(text=f"Invoked by {before.name + '#' + before.discriminator}")
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
            embed.set_footer(text=f"Invoked by {before.name + '#' + before.discriminator}")
            wic = []
            for guild in self.bot.guilds:
                if guild.get_member(before.id):
                    wic.append(guild.id)
            for gid in wic:
                log_channel = db.field("SELECT LogChannel FROM guilds WHERE GuildID = ?", gid)
                if db.field("SELECT Leg FROM guilds WHERE GuildID = ?", gid) == 'ON':
                    await self.bot.get_channel(log_channel).send(embed=embed)
        if hasattr(before.avatar, "url") and hasattr(after.avatar, "url"):
            if before.avatar.url != after.avatar.url:
                if before.id == 706758905585336350:
                    return
                embed = Embed(title="Avatar change",
                                description="New image is below, old to the right.",
                                colour=Colour.dark_gold(),
                                timestamp=datetime.utcnow())

                embed.set_thumbnail(url=before.avatar.url)
                embed.set_image(url=after.avatar.url)
                embed.set_footer(text=f"Invoked by {before.name + '#' + before.discriminator}")
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
            embed.set_footer(text=f"Invoked by {before.name + '#' + before.discriminator}")
            gid = before.guild.id
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
            embed.set_footer(text=f"Invoked by {before.name + '#' + before.discriminator}")
            gid = before.guild.id
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