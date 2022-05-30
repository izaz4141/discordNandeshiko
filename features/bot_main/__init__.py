from discord import Embed, File, Intents, ActivityType, Activity, Message
from discord import Bot as BotClient
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import CommandNotFound, Context, BadArgument, MissingRequiredArgument, CommandOnCooldown, when_mentioned_or
from discord.ext.commands.errors import MissingPermissions, MissingRole, NSFWChannelRequired
from discord.errors import HTTPException, Forbidden, NotFound
from urllib3.exceptions import MaxRetryError
from requests.exceptions import SSLError
from ..utils.saucenao_api.errors import UnknownClientError, ShortLimitReachedError, LongLimitReachedError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
# from time import time
from json import loads, dumps
from glob import glob
from os import getenv
from traceback import format_exc
from random import choices, randint
from asyncio import sleep
from apscheduler.triggers.cron import CronTrigger


# system("git init && git remote add origin https://github.com/izaz4141/discordNandeshiko.git")
# system("git remote set_url origin https://github.com/izaz4141/discordNandeshiko.git")

from ..cogs.help import Help
from ..cloud.dropbox import *
from dropbox.exceptions import ApiError
from ..utils import wordle, kataple

try:
    download_from_dropbox("./data/db/nandeshiko-database.db", "/nandeshiko-database.db")
except ApiError:
    backup("./data/db/nandeshiko-database.db", "/nandeshiko-database.db")



from ..db import db

client = BotClient()
intents = Intents.all()
# intents.members = True
# intents.presences = True
# intents.message_content = True
# PREFIX = "+"
OWNER_IDS = [343962708166574090]
COGS = [path.split("\\")[-1][:-3] for path in glob("features/cogs/*.py")]
IGNORE_EXCEPTION = (CommandNotFound, BadArgument, NotFound)
DESKTOP_KEY = getenv("DESKTOP_KEY")

def remove_items(test_list, item):
    # using list comprehension to perform the tast for n in item:

    res = [i for i in set(test_list) if i != item]
  
    return res

def get_prefix(bot, message):
    if not isinstance(message.guild, type(None)):
        prefix = db.field("SELECT Prefix FROM guilds WHERE GuildID = ?", message.guild.id)
        return when_mentioned_or(prefix)(bot, message)
    else:
        return when_mentioned_or("+")(bot, message)
class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog.split("/")[-1], False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f" {cog} cog ready")

    def all_ready(self):
        return all([getattr(self, cog.split("/")[-1]) for cog in COGS])

class Bot(BotBase):
    def __init__(self):
        # self.PREFIX = PREFIX
        self.ready = False
        self.cogs_ready = Ready()
        self.guild = None
        self.scheculer = AsyncIOScheduler()
        self.maintenance = False

        db.autosave(self.scheculer)
        super().__init__(command_prefix=get_prefix, owner_ids=OWNER_IDS, intents=intents)
    
    def setup(self):
        for cog in COGS:
            cog = cog.split("/")[-1]
            self.load_extension(f"features.cogs.{cog}")
            print(f" {cog} cog loaded")
            
    def update_db_intoCloud(self):
        backup("./data/db/nandeshiko-database.db", "/nandeshiko-database.db")

    def update_db(self):
        db.multiexec("INSERT OR IGNORE INTO guilds (GuildID,GuildName) VALUES (?,?)", ((guild.id, guild.name,) for guild in self.guilds))
        for guild in self.guilds:
            db.execute("UPDATE guilds set GuildName = ? WHERE GuildID = ?", guild.name, guild.id)
        
        db.multiexec("INSERT OR IGNORE INTO exp (UserID,UserName) VALUES (?,?)", ((member.id, f"{member.name}#{member.discriminator}",) for guild in self.guilds for member in guild.members if not member.bot ))
        for guild in self.guilds:
            for member in guild.members:
                if not member.bot:
                    db.execute("UPDATE exp set UserName = ? Where UserID = ?", f"{member.name}#{member.discriminator}", member.id)
        
        # memb = {}
        # for guild in self.guilds:
        guilds_past = db.column("SELECT GuildID FROM guilds")
        to_remove = []
        exist = []
        
        for id_ in guilds_past:
            if not self.get_guild(id_):
                to_remove.append(id_)

            elif self.get_guild(id_):
                exist.append(id_)
        for id_ in exist:
            try :
                to_remove = remove_items(to_remove, id_ )

            except ValueError:
                pass


        db.multiexec("DELETE FROM guilds WHERE GuildID = ?", ((id_,) for id_ in to_remove))
        
        members_past = db.column("SELECT UserID FROM exp")
        to_remove = []
        exist = []

        for id_ in members_past:
            usar = self.get_user(id_)
            if not usar:
                to_remove.append(id_)

            elif usar:
                if not usar.bot:
                    exist.append(id_)
                else:
                    to_remove.append(id_)
        for id_ in exist:
            try :
                to_remove = remove_items(to_remove, id_ )

            except ValueError:
                pass


        db.multiexec("DELETE FROM exp WHERE UserID = ?", ((id_,) for id_ in to_remove))

        db.commit()

    def run(self, version):
        self.VERSION = version

        print("running setup")
        self.setup()
        self.TOKEN = getenv('DIS_KEY')

        print("running bot...")
        super().run(self.TOKEN, reconnect=True)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls= Context)
        if self.ready:
            if ctx.command and not isinstance(ctx.guild, type(None)):
                statistics = db.record("SELECT Statistics FROM guilds WHERE GuildID = ?", ctx.guild.id)[0]
                try:
                    statistics = loads(statistics)
                except Exception:
                    statistics = statistics
                try:
                    statistics[ctx.command.name] += 1
                except KeyError:
                    statistics[ctx.command.name] = 1
                baru = dumps(statistics)
                db.execute("UPDATE guilds SET Statistics = ? WHERE GuildID = ?", baru, ctx.guild.id)
            await self.invoke(ctx)
        else:
            if not ctx.prefix is None:
                await ctx.send("Bentar kak lagi siap - siap")
        
        



    async def on_connect(self):
        print("bot connected")

    async def on_disconnect(self):
        print("bot disconnected")

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("?")
        else:
            channel = self.get_channel(757478450490638376) 
            await channel.send("Ada sesuatu yang salah")
        
        await self.get_user(OWNER_IDS[0]).send(format_exc())
        raise

    async def on_command_error(self, ctx, exc):
        if any([isinstance(exc, error) for error in IGNORE_EXCEPTION]):
            pass
        elif isinstance(ctx.guild, type(None)):
            await ctx.send("Kata kak Glicole gaboleh ikutin orang di tempat sepi!")
        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send("Perintahnya tidak lengkap kak")
            await Help(self).cmd_help(ctx, ctx.command)
        
        elif isinstance(exc, MissingPermissions):
            await ctx.send("Kamu siapa? kamu bukan temanku!!")

        elif isinstance(exc, CommandOnCooldown):
            if exc.retry_after < 60:
                await ctx.send(f"Sabar kak, sedang terjadi {str(exc.type).split('.')[-1]} cooldown.\nCoba lagi dalam {exc.retry_after:,.2f} detik.")

            elif exc.retry_after < 3600:
                await ctx.send(f"Sabar kak, sedang terjadi {str(exc.type).split('.')[-1]} cooldown.\nCoba lagi dalam {exc.retry_after/60:,.2f} menit.")

            else:
                await ctx.send(f"Sabar kak, sedang terjadi {str(exc.type).split('.')[-1]} cooldown.\nCoba lagi dalam {exc.retry_after/3600:,.4f} jam.")
                
        elif isinstance(exc, MissingRole):
            await ctx.send(f"Maaf kakak tidak dapat mengakses perintah ini karena belum bergabung dalam **{exc.missing_role}**")
        
        elif isinstance(exc, NSFWChannelRequired):
            await ctx.send(file= File('./data/image/pout.png'))
            
        elif hasattr(exc, "original"):
            if isinstance(exc.original, HTTPException):
                await ctx.send("Perasaanku tidak dapat disampaikan dengan kata - kata")
                raise exc.original
            elif isinstance(exc.original, Forbidden):
                await ctx.send("Tidak memiliki authoritas")
            elif isinstance(exc.original, SSLError):
                print(f"Halaman yang diakses {ctx.author.name} terblokir (coba pakai vpn)")
                
            elif isinstance(exc.original, UnknownClientError):
                await ctx.send("Maaf! Hasil cari tidak ditemukan")
            elif isinstance(exc.original, ShortLimitReachedError):
                await ctx.send("Maaf! Aku sedang sibuk, coba beberapa saat lagi.")
            elif isinstance(exc.original, LongLimitReachedError):
                await ctx.send("Maaf! Limit sauce yang boleh dicari hari ini sudah tercapai")
            

            else:
                raise exc.original

        else:
            raise exc

    async def on_ready(self):
        if not self.ready:
            # self.guilds = await self.fetch_guilds(limit= 5)
            await self.change_presence(activity= Activity(type=ActivityType.watching, name= "Yuru Camp △", details= "@Nandeshikyot help", state="Comfy"))
            self.guild = self.get_guild(605057520955818010) #KALAU HANYA SATU SERVER
            self.comfy = self.get_guild(823535615609667624)
            self.stdout = self.get_channel(757478450490638376)
            self.SERVER_EXCEPTION = ['wo1', 'wo2']
            self.totalE = []
            for guild in self.guilds:
                if not guild.name in self.SERVER_EXCEPTION:
                    for i in range(len(guild.emojis)-1):
                        self.totalE.append(guild.emojis[i])
            if DESKTOP_KEY == "benar":
                self.maintenance = True
            minute = [19, 39, 59]
            for minu in minute:
                self.scheculer.add_job(self.update_db_intoCloud, CronTrigger(minute= minu))
            self.scheculer.start()
            self.update_db()
            while not self.cogs_ready.all_ready():
                await sleep(0.5)
            self.ready = True
            print("bot ready")

            
            #await self.stdout.send("Online")

            embed = Embed(title="Now Online", description="Nandeshikyot paling kyot",
                          colour=0xFFB6C1, timestamp=datetime.utcnow())
            #fields = [("Status", "Nandeshikyot Now Online", True)]
            #for name, value, inline in fields:
            #    embed.add_field(name=name, value=value, inline=inline)
            embed.set_author(name=self.guild.me.display_name, icon_url=self.guild.me.avatar.url)
            #embed.set_footer(text="footer")
            #embed.set_thumbnail(url=self.guild.icon_url)
            # embed.set_image(url=self.guild.icon_url)
            ow_ids = [f"<@{ids}>" for ids in OWNER_IDS]
            await self.stdout.send(" ".join(ow_ids))
            await self.stdout.send(embed=embed)

        else:
            print("bot reconnected")
    
    

    @client.event
    async def on_message(self, message):
        if not message.author.bot:
            if DESKTOP_KEY == "benar":
                if not message.author.id in self.owner_ids:
                    return
            elif self.maintenance is True:
                if message.content == "maintenance off" and message.author.id in self.owner_ids:
                    self.maintenance = False
                    return
                return
            if message.author.id in self.owner_ids:
                if message.content == "upload db" :
                    return self.update_db_intoCloud()
                elif message.content == "update db":
                    return self.update_db()
                elif message.content == "maintenance on":
                    self.maintenance = True
                    return
                elif message.content == "maintenance off":
                    self.maintenance = False
                    return
            if "nandeshi" in message.content or "nadeshi" in message.content:
                total_emojis = self.totalE
                await message.channel.send(choices(["Apa kak?", "Ui", str(total_emojis[randint(0, len(total_emojis)-1)])], weights= [1, 1, 2], k=1)[0])
            if message.reference:
                if isinstance(message.reference.resolved, Message):
                    parent = message.reference.resolved
                    if parent.embeds:
                        embed = parent.embeds[0]
                        if embed.title == "Wordle":
                            await wordle.process_message_as_guess(self, message)
                        elif embed.title == "Kataple":
                            await kataple.process_message_as_guess(self, message)
                
            await self.process_commands(message)
            
            

            

bot = Bot()
