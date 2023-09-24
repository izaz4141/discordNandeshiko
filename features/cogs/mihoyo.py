from discord.ext.commands import Cog, command, slash_command
from discord import Embed, option

from typing import Optional
from datetime import datetime
import asyncio

from mihomo import Language, MihomoAPI
from mihomo.models import StarrailInfoParsed

from ..utils import hsr
from ..db import db


client = MihomoAPI(language=Language.EN)
OPTIONS = {
    "1️⃣": 0,
    "2⃣": 1,
    "3⃣": 2,
    "4⃣": 3,
    "5⃣": 4,
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
        
        
        data: StarrailInfoParsed = await client.fetch_user(uid, replace_icon_name_with_url=True)
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

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("mihoyo")

def setup(bot):
    bot.add_cog(MiHoYo(bot))