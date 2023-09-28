from discord.ext.commands import Cog, command, slash_command
from discord import Embed, option

import asyncio
from typing import Optional
from datetime import datetime
from cryptography.fernet import Fernet
from json import loads, dumps, JSONDecodeError

from mihomo import Language, MihomoAPI
from mihomo.models import StarrailInfoParsed
from enkanetwork import EnkaNetworkAPI
from genshin import Client
from genshin.types import Game
from genshin.errors import AlreadyClaimed, DataNotPublic, RedemptionClaimed, RedemptionInvalid

from ..utils import hsr
from ..db import db


hsr_client = MihomoAPI(language=Language.EN)
gi_client = EnkaNetworkAPI()
base_cookie = {"ltuid": 119480035, "ltoken": "cnF7TiZqHAAvYqgCBoSPx5EjwezOh1ZHoqSHf7dT"}

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

    @command(name="profile_gi", aliases=["pg"])
    async def profile_gi(self, ctx, *, uid: Optional[str]="0"):
        uid = int(uid)

        if uid == 0:
            uid = db.record("SELECT GI_UID FROM exp WHERE UserID = ?", ctx.author.id)[0]
            if uid == 0:
                return await ctx.send("Mmmm... maaf, Nadeshiko tidak bisa menemukan UID GI kakak~\nCoba command register_gi untuk mendaftarkan UID-nya!")
        
        data = await gi_client.fetch_user(uid)
        try:
            hoyocookie = db.record("SELECT HoyoCookie FROM exp WHERE UserID = ?", ctx.author.id)[0]
            hoyocookie = loads(hoyocookie)
        except JSONDecodeError:
            return await ctx.send("Maaf, Kakak belom mengeset cookie hoyolab ๑•́ㅿ•̀๑) ᔆᵒʳʳᵞ\nCoba melakukan command set_hoyo_cookie terlebih dahulu~")
        fernet = Fernet(hoyocookie['salt'])
        cookie = {'ltuid': int(fernet.decrypt(hoyocookie['ltuid'].encode('utf-8')).decode()), 'ltoken': fernet.decrypt(hoyocookie['ltoken'].encode('utf-8')).decode()}
        g_client = Client(cookie)
        try:
            notes = await g_client.get_genshin_notes(uid)
        except DataNotPublic:
            return await ctx.send("Data HoyoLab Kakak belum publik!\nData Battle Chronicles dapat dipublikkan dari setting privasi HoyoLab")
        embed = Embed(
            title= f"{data.player.nickname}         ({data.player.level})",
            description= f"*{data.player.signature}*",
            color=ctx.author.colour
        )
        exped = 0
        for expedition in notes.expeditions:
            if expedition.finished:
                exped += 1
        fields = [
            ("Resin", f"{notes.current_resin}/{notes.max_resin}"),
            ("Daily Commision", f"{notes.completed_commissions}/{notes.max_commissions}\nClaimed: {notes.claimed_commission_reward}"),
            ("Expedition", f"Finished: { exped }/{notes.max_expeditions}"),
            ("Abyss Floor", f"{data.player.abyss_floor} - {data.player.abyss_room}"),
            ("Teapot Coin", f"{notes.current_realm_currency}/{notes.max_realm_currency}")
        ]
        for name, value in fields:
            if value == '':
                    value = "N/A"
            embed.add_field(name=name, value=value, inline=True)
        embed.set_thumbnail(url= data.player.avatar.icon.url)
        embed.set_footer(text= f"UID: {uid}")

        await ctx.send(embed=embed)

    @command(name="profile_hsr", aliases=["ph"])
    async def profile_hsr(self, ctx, uid: Optional[str]="0"):
        uid = int(uid)

        if uid == 0:
            uid = db.record("SELECT HSR_UID FROM exp WHERE UserID = ?", ctx.author.id)[0]
            if uid == 0:
                return await ctx.send("Mmmm... maaf, Nadeshiko tidak bisa menemukan UID HSR kakak~\nCoba command register_hsr untuk mendaftarkan UID-nya!")

        data: StarrailInfoParsed = await hsr_client.fetch_user(uid, replace_icon_name_with_url=True)
        try:
            hoyocookie = db.record("SELECT HoyoCookie FROM exp WHERE UserID = ?", ctx.author.id)[0]
            hoyocookie = loads(hoyocookie)
        except JSONDecodeError:
            return await ctx.send("Maaf, Kakak belom mengeset cookie hoyolab ๑•́ㅿ•̀๑) ᔆᵒʳʳᵞ\nCoba melakukan command set_hoyo_cookie terlebih dahulu~")
        fernet = Fernet(hoyocookie['salt'])
        cookie = {'ltuid': int(fernet.decrypt(hoyocookie['ltuid'].encode('utf-8')).decode()), 'ltoken': fernet.decrypt(hoyocookie['ltoken'].encode('utf-8')).decode()}
        g_client = Client(cookie)
        try:
            notes = await g_client.get_starrail_notes(uid)
            celeng = await g_client.get_starrail_challenge(uid)
        except DataNotPublic:
            return await ctx.send("Data HoyoLab Kakak belum publik!\nData Battle Chronicles dapat dipublikkan dari setting privasi HoyoLab")

        embed = Embed(
            title= f"{data.player.name}         ({data.player.level})",
            description= f"*{data.player.signature}*",
            color=ctx.author.colour
        )
        sec = notes.stamina_recover_time.seconds
        jam = int(sec/3600)
        menit = int((sec % 3600)/60)
        detik = sec % 60
        finished = 0
        for expedition in notes.expeditions:
            if expedition.finished:
                finished += 1 
        waktu_MoC = celeng.end_time.datetime - datetime.utcnow()
        if waktu_MoC.days == 0:
            sc = waktu_MoC.seconds
            j = int(sc/3600)
            m = int((sc % 3600)/60)
            d = sc % 60
            waktu_MoC = f"{j} jam {m} menit {d} detik"
        else:
            waktu_MoC = f"{waktu_MoC.days} hari" 
        fields = [
            ("Trailblaze Power", f"{notes.current_stamina}/{notes.max_stamina}\n{jam} jam {menit} menit {detik} detik"),
            ("Daily Commision", f"{notes.current_train_score}/{notes.max_train_score}"),
            ("Assignments", f"Finished: { finished }/{notes.total_expedition_num}"),
            ("Simulated Universe", f"{notes.current_rogue_score}/{notes.max_rogue_score}"),
            ("Echo of War", f"{notes.remaining_weekly_discounts}/{notes.max_weekly_discounts}"),
            ("Memory of Chaos", f"{celeng.total_stars}/30\n{waktu_MoC}"),
        ]
        for name, value in fields:
            if value == '':
                    value = "N/A"
            embed.add_field(name=name, value=value, inline=True)
        embed.set_thumbnail(url= data.player.avatar.icon)
        embed.set_footer(text= f"UID: {uid}")
        await ctx.send(embed=embed)

    @command(name="set_hoyo_cookie")
    async def set_hoyo_cookie(self, ctx, *, cookie):
        """Mengeset HoyoLab Cookie untuk melakukan claim reward, dll

        Args:
            ctx (_type_): _description_
            cookie (str): Berisikan ltuid <spasi> ltoken
        Contoh:
            +set_hoyo cookie 3223424 j23hv4kj23gv4j23hv52j3kh
        """
        cookie = cookie.split(" ")
        ltuid = cookie[0]
        ltoken = cookie[1]
        salt = Fernet.generate_key()
        salt_string = salt.decode()
        fernet = Fernet(salt)
        ltuid_encrypted = fernet.encrypt(ltuid.encode('utf-8')).decode()
        ltoken_encrypted = fernet.encrypt(ltoken.encode('utf-8')).decode()
        cookie_dict = {
            'ltuid': ltuid_encrypted,
            'ltoken': ltoken_encrypted,
            'key': salt_string
        }
        db.execute("UPDATE exp SET HoyoCookie = ? WHERE UserID = ?", dumps(cookie_dict), ctx.author.id)
        await ctx.message.delete()
        await ctx.send("Oke kak, Cookie HoyoLab sudah Nadeshiko simpan~")

    @slash_command(name="set_hoyo_cookie", description="Mengeset HoyoLab Cookie untuk melakukan claim reward, dll")
    @option("ltuid", int)
    @option("ltoken", str)
    async def set_hoyo_cookie_slash(self, ctx, ltuid, ltoken):
        salt = Fernet.generate_key()
        salt_string = salt.decode()
        fernet = Fernet(salt)
        ltuid_encrypted = fernet.encrypt(str(ltuid).encode('utf-8')).decode()
        ltoken_encrypted = fernet.encrypt(ltoken.encode('utf-8')).decode()
        cookie_dict = {
            'ltuid': ltuid_encrypted,
            'ltoken': ltoken_encrypted,
            'salt': salt_string
        }
        db.execute("UPDATE exp SET HoyoCookie = ? WHERE UserID = ?", dumps(cookie_dict), ctx.author.id)
        await ctx.respond("Oke kak, Cookie HoyoLab sudah Nadeshiko simpan~", ephemeral=True)

    @command(name="checkin")
    async def checkin(self, ctx, *, game):
        """Check-in Game MiHoYo pada HoyoLab (butuh Hoyolab Cookie)
        """
        game = game.lower()
        if game != "gi" and game != "hsr":
            return await ctx.send("Game yang bisa dipilih hanyalah gi (Genshin Impact) atau hsr (Honkai: Star Rail)")
        if game == "gi":
            game = Game.GENSHIN
        elif game == "hsr":
            game = Game.STARRAIL

        try:
            hoyocookie = db.record("SELECT HoyoCookie FROM exp WHERE UserID = ?", ctx.author.id)[0]
            hoyocookie = loads(hoyocookie)
        except JSONDecodeError:
            return await ctx.send("Maaf, Kakak belom mengeset cookie hoyolab ๑•́ㅿ•̀๑) ᔆᵒʳʳᵞ\nCoba melakukan command set_hoyo_cookie terlebih dahulu~")
        fernet = Fernet(hoyocookie['salt'])
        cookie = {'ltuid': int(fernet.decrypt(hoyocookie['ltuid'].encode('utf-8')).decode()), 'ltoken': fernet.decrypt(hoyocookie['ltoken'].encode('utf-8')).decode()}
        g_client = Client(cookie)
        try:
            reward = await g_client.claim_daily_reward(game=game)
            msg = Embed(
                title= "Daily Check-in",
                description= f"{reward.name} x{reward.amount}",
                colour= ctx.author.colour,
                timestamp= datetime.utcnow()
            )
            msg.set_thumbnail(url=reward.icon)
            await ctx.send(embed=msg)
        except AlreadyClaimed:
            return await ctx.send("Kakak sudah mendapatkan hadiah untuk hari ini~ Coba lagi besok!")

    @command(name="redeem")
    async def redeem_code(self, ctx, *, game: str= "none", code=""):
        """Redeem code untuk game di HoyoLab

        Args:
            game : Tipe game (gi atau hsr)
            code: Kode redeemnya
        Contoh:
            +redeem gi AOUIJ281IA6Z
        """

        game = game.split(" ")
        code = game[1]
        game = game[0].lower()

        if game != "gi" and game != "hsr":
            return await ctx.send("Game yang bisa dipilih hanyalah gi (Genshin Impact) atau hsr (Honkai: Star Rail)")
        if game == "gi":
            game = Game.GENSHIN
            uid = db.record("SELECT GI_UID FROM exp WHERE UserID = ?", ctx.author.id)[0]
            if uid == 0:
                return await ctx.send("Mmmm... maaf, Nadeshiko tidak bisa menemukan UID GI kakak~\nCoba command register_gi untuk mendaftarkan UID-nya!")
        elif game == "hsr":
            game = Game.STARRAIL
            uid = db.record("SELECT HSR_UID FROM exp WHERE UserID = ?", ctx.author.id)[0]
            if uid == 0:
                return await ctx.send("Mmmm... maaf, Nadeshiko tidak bisa menemukan UID GI kakak~\nCoba command register_hsr untuk mendaftarkan UID-nya!")
        try:
            hoyocookie = db.record("SELECT HoyoCookie FROM exp WHERE UserID = ?", ctx.author.id)[0]
            hoyocookie = loads(hoyocookie)
        except JSONDecodeError:
            return await ctx.send("Maaf, Kakak belom mengeset cookie hoyolab ๑•́ㅿ•̀๑) ᔆᵒʳʳᵞ\nCoba melakukan command set_hoyo_cookie terlebih dahulu~")
        fernet = Fernet(hoyocookie['salt'])
        cookie = {'ltuid': int(fernet.decrypt(hoyocookie['ltuid'].encode('utf-8')).decode()), 'ltoken': fernet.decrypt(hoyocookie['ltoken'].encode('utf-8')).decode()}
        g_client = Client(cookies=cookie)
        try:
            await g_client.redeem_code(code=code, uid=uid, game=game)
        except RedemptionClaimed:
            await ctx.send("Maaf, kode sudah diredeem sebelumnya")
        except RedemptionInvalid:
            await ctx.send("Maaf, kode yang diberikan tidak benar")

    @command(name="remind")
    async def reminder(self, ctx, *, game:str):
        """Reminder jika stamina sudah 80% penuh (In progress)

        Args:
            game (str): GI atau HSR
        """
        if game.lower() != "gi" and game.lower() != "hsr":
            return await ctx.send("Game yang bisa dipilih hanyalah gi (Genshin Impact) atau hsr (Honkai: Star Rail)")
        game = game.upper()
        try:
            remind = db.record(f"SELECT Remind FROM exp WHERE UserID = ?", ctx.author.id)[0]
            remind = loads(remind)
        except JSONDecodeError:
            remind = { game: True }
            db.execute("UPDATE exp SET Remind = ? WHERE UserID = ?", dumps(remind), ctx.author.id)
            return await ctx.send(f"Reminder Stamina untuk {game} diaktifkan")
        try:
            remind[game] = not remind[game]
        except KeyError:
            remind[game] = True
        db.execute("UPDATE exp SET Remind = ? WHERE UserID = ?", dumps(remind), ctx.author.id)
        await ctx.send(f"Reminder Stamina untuk {game} di{'aktifkan' if not remind[game] else 'nonaktifkan'}")


    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("mihoyo")

def setup(bot):
    bot.add_cog(MiHoYo(bot))