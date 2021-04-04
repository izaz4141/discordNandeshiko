from discord.ext.commands import Cog, command, BadArgument, cooldown, BucketType
from random import choice, randint
from discord import Member, Embed, Client
from discord.errors import HTTPException, Forbidden
from typing import Optional
from aiohttp import request
from jikanpy import Jikan
from datetime import datetime

from ..db import db



class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot


    @command(name="luck")
    @cooldown(1, 60*60*24, BucketType.user)  #Parameternya(jumlah dipakai sebelum cd, waktu cd, type cd : member, user, guild, default)
    async def luck(self, ctx):
        luck = randint(1,100)
        if luck <= 30:
            await ctx.send('Haha ampas')
        elif luck <= 50:
            await ctx.send('Mayan lucknya, 50% berhasil. Sisa 50%nya lagi diisi dengan semangat aja!')
        elif luck <= 80:
            await ctx.send('Kalau dihitung dari pergerakan bintang dan snezhnaya keberuntungan kaka hari ini BAIK!! :thumbsup:')
        elif luck <= 99:
            await ctx.send('Enaknyaa~ aku juga pengen laksek... bagi dong ka lucknya!')
        elif luck == 100:
            await ctx.send("(0 o 0 ) Gila beuhh")
            
        

    @command(name="dice")
    async def roll_n_dice(self, ctx, die_string: str):
        dice, value = (int(msg) for msg in die_string.split("d"))
        rolls = [randint(1, value) for i in range(dice)]
        await ctx.send(" + ".join([str(r) for r in rolls]) + f" = {sum(rolls)}")
    
    
    @command(name="bilang")
    async def say(self, ctx, *, message):
        await ctx.message.delete()
        await ctx.send(f"{message} <:nandeshikyot:752500122415267850>")

    @command(name="slap")
    async def slap_member(self, ctx, member: Member, *, reason: Optional[str] = "ngeselin"):
        if member.id == self.bot.owner_ids[0]:
            await ctx.send("Gamau")
        else: 
            await ctx.send(f"Nandeshiko menampar {member.mention} karena {reason}")
        # print(member)
    @slap_member.error
    async def slap_member_error(self, ctx, exc):
        if isinstance(exc, BadArgument):
            await ctx.send("Siapa itu?")




    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")



def setup(bot):
    bot.add_cog(Fun(bot))