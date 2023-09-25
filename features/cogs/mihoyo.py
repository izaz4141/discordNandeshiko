from discord.ext.commands import Cog, command, slash_command
from discord import Embed, option

from typing import Optional
from datetime import datetime
import asyncio

from mihomo import Language, MihomoAPI
from mihomo.models import StarrailInfoParsed
from enkanetwork import EnkaNetworkAPI

from ..utils import hsr
from ..db import db


hsr_client = MihomoAPI(language=Language.EN)
gi_client = EnkaNetworkAPI()
OPTIONS = {
    "1️⃣": 0,
    "2⃣": 1,
    "3⃣": 2,
    "4⃣": 3,
    "5⃣": 4,
    "6️⃣": 5,
    "7️⃣": 6,
    "8️⃣": 7,
    "9️⃣": 8,
}

class MiHoYo(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="relic_scorer", aliases=["rs"])
    async def relic_scorer(self, ctx, *, uid: Optional[str]="0"):
        """Melihat Relic pada karakter di HSR

        Args:
            uid (Optional[int]): UID HSR
        """
        def _check(r, u):
            return (
                r.emoji in OPTIONS.keys()
                and u == ctx.author
                and r.message.id == msg.id
            )
        uid = int(uid)

        if uid == 0:
            uid = db.record("SELECT HSR_UID FROM exp WHERE UserID = ?", ctx.author.id)[0]
            if uid == 0:
                return await ctx.send("Mmmm... maaf, Nadeshiko tidak bisa menemukan UID HSR kakak~\nCoba command register_hsr untuk mendaftarkan UID-nya!")
        
        
        data: StarrailInfoParsed = await hsr_client.fetch_user(uid, replace_icon_name_with_url=True)
        choice = Embed(
            title= "Select Characters",
            description= "\n".join([f"{i}. {chara.name}" for i, chara in enumerate(data.characters)]),
            colour= ctx.author.colour,
            timestamp = datetime.utcnow()
        )
        msg = await ctx.send(embed=choice)
        for emoji in list(OPTIONS.keys())[:min(len(data.characters), len(OPTIONS))]:
            await msg.add_reaction(emoji)
        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=25.0, check=_check)
        except asyncio.TimeoutError:
            await msg.delete()
            return None
        else:
            await msg.delete()
            chara = data.characters[OPTIONS[reaction.emoji]]
            relics = hsr.relic_scorer(chara, uid)
            await ctx.send(embed=relics)
    @slash_command(name="relic_scorer", description="Melihat Relic pada karakter di HSR")
    @option("uid", int, description="UID HSR", default=None)
    async def relic_scorer_slash(self, ctx, uid):
        await self.relic_scorer(ctx, uid=uid)

    @command(name="register_hsr")
    async def register_hsr(self, ctx, *, uid):
        """Menyimpan UID HSR-mu

        Args:
            uid (int): UID HSR
        """
        if uid.isnumeric():
            uid = int(uid)
        else:
            return await ctx.send("Coba lagi kak (˶ᵔ ᵕ ᵔ˶)")
        
        db.execute("UPDATE exp SET HSR_UID = ? WHERE UserID = ?", uid, ctx.author.id)
        await ctx.send("Okeee~ lain kali kalau ngecek akun HSR tidak usah pake UID lagi!")
        return
    @slash_command(name="register_hsr", description="Menyimpan UID HSR-mu")
    @option("uid", int, description="UID HSR")
    async def register_hsr_slash(self, ctx, *, uid):
        db.execute("UPDATE exp SET HSR_UID = ? WHERE UserID = ?", uid, ctx.author.id)
        await ctx.respond("Okeee~ lain kali kalau ngecek akun HSR tidak usah pake UID lagi!")

    @command(name="register_gi")
    async def register_gi(self, ctx, *, uid):
        """Menyimpan UID GI-mu

        Args:
            uid (int): UID GI
        """
        if uid.isnumeric():
            uid = int(uid)
        else:
            return await ctx.send("Coba lagi kak (˶ᵔ ᵕ ᵔ˶)")
        
        db.execute("UPDATE exp SET GI_UID = ? WHERE UserID = ?", uid, ctx.author.id)
        await ctx.send("Okeee~ lain kali kalau ngecek akun GI tidak usah pake UID lagi!")
        return
    @slash_command(name="register_gi", description="Menyimpan UID GI-mu")
    @option("uid", int, description="UID GI")
    async def register_gi_slash(self, ctx, *, uid):
        db.execute("UPDATE exp SET GI_UID = ? WHERE UserID = ?", uid, ctx.author.id)
        await ctx.respond("Okeee~ lain kali kalau ngecek akun GI tidak usah pake UID lagi!")

    @command(name="artifact_eval", aliases=["ae"])
    async def artifact_eval(self, ctx, *, uid: Optional[str]="0"):
        """Melihat Artifact pada karakter di Genshin Impact

        Args:
            uid (Optional[int]): UID GI
        """
        def _check(r, u):
            return (
                r.emoji in OPTIONS.keys()
                and u == ctx.author
                and r.message.id == msg.id
            )
        uid = int(uid)

        if uid == 0:
            uid = db.record("SELECT GI_UID FROM exp WHERE UserID = ?", ctx.author.id)[0]
            if uid == 0:
                return await ctx.send("Mmmm... maaf, Nadeshiko tidak bisa menemukan UID GI kakak~\nCoba command register_gi untuk mendaftarkan UID-nya!")
        
        
        data = await gi_client.fetch_user(uid)
        choice = Embed(
            title= "Select Characters",
            description= "\n".join([f"{i}. {chara.name}" for i, chara in enumerate(data.characters)]),
            colour= ctx.author.colour,
            timestamp = datetime.utcnow()
        )
        msg = await ctx.send(embed=choice)
        for emoji in list(OPTIONS.keys())[:min(len(data.characters), len(OPTIONS))]:
            await msg.add_reaction(emoji)
        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=25.0, check=_check)
        except asyncio.TimeoutError:
            await msg.delete()
            return None
        else:
            await msg.delete()
            chara = data.characters[OPTIONS[reaction.emoji]]
            artifacts = hsr.artifact_eval(chara, uid)
            await ctx.send(embed=artifacts)
    @slash_command(name="artifact_eval", description="Melihat Relic pada karakter di Genshin Impact")
    @option("uid", int, description="UID GI", default=None)
    async def artifact_eval_slash(self, ctx, uid):
        await self.artifact_eval(ctx, uid=uid)

    @command(name="gi_profile", aliases=["gp"])
    async def gi_profile(self, ctx, *, uid: Optional[str]="0"):
        uid = int(uid)

        if uid == 0:
            uid = db.record("SELECT GI_UID FROM exp WHERE UserID = ?", ctx.author.id)[0]
            if uid == 0:
                return await ctx.send("Mmmm... maaf, Nadeshiko tidak bisa menemukan UID GI kakak~\nCoba command register_gi untuk mendaftarkan UID-nya!")
        
        data = await gi_client.fetch_user(uid)
        embed = Embed(
            title= f"{data.player.nickname}         ({data.player.level})",
            description= f"*{data.player.signature}*",
            color=ctx.author.colour
        )
        fields = [
            ("Abyss Floor", f"{data.player.abyss_floor} - {data.player.abyss_room}")
        ]
        for name, value in fields:
            if value == '':
                    value = "N/A"
            embed.add_field(name=name, value=value)
        embed.set_thumbnail(url= data.player.avatar.icon.url)
        embed.set_footer(text= f"UID: {uid}")

        await ctx.send(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("mihoyo")

def setup(bot):
    bot.add_cog(MiHoYo(bot))