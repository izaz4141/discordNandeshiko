from discord import Embed, File, Client, Intents
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import CommandNotFound, Context, BadArgument, MissingRequiredArgument, CommandOnCooldown, when_mentioned_or
from discord.ext.commands.errors import MissingPermissions, BotMissingPermissions
from discord.errors import HTTPException, Forbidden, NotFound
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from time import time
from glob import glob
from os import system
from random import choices, randint
from asyncio import sleep
from apscheduler.triggers.cron import CronTrigger

from ..db import db

system("python -m pip install -U git+https://github.com/Rapptz/discord-ext-menus")

client = Client()
intents = Intents.default()
intents.members = True
intents.presences = True
# PREFIX = "+"
OWNER_IDS = [343962708166574090]
COGS = [path.split("\\")[-1][:-3] for path in glob("features/cogs/*.py")]
IGNORE_EXCEPTION = (CommandNotFound, BadArgument, NotFound)

def remove_items(test_list, item):
      

    # using list comprehension to perform the tast for n in item:

    res = [i for i in set(test_list) if i != item]
  
    return res

def get_prefix(bot, message):
    prefix = db.field("SELECT Prefix FROM guilds WHERE GuildID = ?", message.guild.id)
    return when_mentioned_or(prefix)(bot, message)

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

        db.autosave(self.scheculer)
        super().__init__(command_prefix=get_prefix, owner_ids=OWNER_IDS, intents=intents)
    
    def setup(self):
        for cog in COGS:
            cog = cog.split("/")[-1]
            self.load_extension(f"features.cogs.{cog}")
            print(f" {cog} cog loaded")
            
    def update_github(self):
        system('git add . && git commit -m "Add existing file"')
        system('git push origin')

    def update_db(self):
        db.multiexec("INSERT OR IGNORE INTO guilds (GuildID) VALUES (?)", ((guild.id,) for guild in self.guilds))

        db.multiexec("INSERT OR IGNORE INTO exp (UserID,UserName) VALUES (?,?)", ((member.id, f"{member.name}#{member.discriminator}",) for guild in self.guilds for member in guild.members if not member.bot ))
        
        members_past = db.column("SELECT UserID FROM exp")
        to_remove = []
        exist = []

        for id_ in members_past:
            for guild in self.guilds:
                if not guild.get_member(id_):
                    to_remove.append(id_)

                if guild.get_member(id_):
                    exist.append(id_)
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

        with open("features/bot_main/token", "r", encoding = "utf-8") as tf:
            self.TOKEN = tf.read()

        print("running bot...")
        super().run(self.TOKEN, reconnect=True)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls= Context)

        if self.ready:
            await self.invoke(ctx)
        else:
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
        raise

    async def on_command_error(self, ctx, exc):
        if any([isinstance(exc, error) for error in IGNORE_EXCEPTION]):
            pass
        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send("Perintahnya tidak lengkap kak")
        
        elif isinstance(exc, MissingPermissions):
            await ctx.send("Kamu siapa? kamu bukan temenku!!")

        elif isinstance(exc, CommandOnCooldown):
            if exc.retry_after < 60:
                await ctx.send(f"Sabar kak, sedang terjadi {str(exc.cooldown.type).split('.')[-1]} cooldown.\nCoba lagi dalam {exc.retry_after:,.2f} detik.")

            elif exc.retry_after < 3600:
                await ctx.send(f"Sabar kak, sedang terjadi {str(exc.cooldown.type).split('.')[-1]} cooldown.\nCoba lagi dalam {exc.retry_after/60:,.2f} menit.")

            else:
                await ctx.send(f"Sabar kak, sedang terjadi {str(exc.cooldown.type).split('.')[-1]} cooldown.\nCoba lagi dalam {exc.retry_after/3600:,.4f} jam.")
        
        
        elif hasattr(exc, "original"):
            if isinstance(exc.original, HTTPException):
                await ctx.send("Perasaanku tidak dapat disampaikan dengan kata - kata")
            elif isinstance(exc.original, Forbidden):
                await ctx.send("Tidak memiliki authoritas")
            else:
                raise exc.original

        else:
            raise exc

    async def on_ready(self):
        if not self.ready:
            # self.guilds = await self.fetch_guilds(limit= 5)
            self.guild = self.get_guild(605057520955818010) #KALAU HANYA SATU SERVER
            self.comfy = self.get_guild(823535615609667624)
            self.stdout = self.get_channel(757478450490638376)
            self.scheculer.add_job(self.update_github, CronTrigger(minute= 19 or 39 or 59))
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
            embed.set_author(name=self.guild.me.display_name, icon_url=self.guild.me.avatar_url)
            #embed.set_footer(text="footer")
            #embed.set_thumbnail(url=self.guild.icon_url)
            # embed.set_image(url=self.guild.icon_url)

            await self.stdout.send(embed=embed)

        else:
            print("bot reconnected")

    @client.event
    async def on_message(self, message):
        
        if not message.author.bot:
            if message.content == '':
                pass
            
            elif "nandeshi" in message.content :
                total_emojis =  self.guild.emojis + self.comfy.emojis
                await message.channel.send(choices(["Apa kak?", "Ui", str(total_emojis[randint(0, len(total_emojis))])], weights= [1, 1, 2], k=1)[0])
                
            else:
                await self.process_commands(message)
            
            if not message.content == '':
                l_kata = message.content.split(" ")
                a = {}
                for i, kata in enumerate(l_kata):
                    sa = time()
                    if ":" == kata[0] and ":" == kata[-1]:
                        
                        
                        total_emojis =  self.guild.emojis + self.comfy.emojis
                        total_emojis_set = set(total_emojis)
                        emoji_name = kata[1:-1]
                        kum_emoji = emoji_name.split('::')
                        # kumpul_emoji = "".join(kumpula_emoji)
                        # kum_emoji = kumpul_emoji.split(': :')
                        kum_emoji_set = set(kum_emoji)
                        for n, nama_emoji in enumerate(kum_emoji):
                            for emoji in total_emojis_set:
                                if nama_emoji.lower() == emoji.name.lower():
                                    a[f"{nama_emoji}_{i}_{n}"] = str(emoji)
                                    break
                                
                                
                    else:
                        a[i] = kata
                
                bener = False
                for key in a.keys():  
                    if a[key][0] == "<" and a[key][-1] == ">":
                        bener = True
                        break
                if bener is True:
                    ass = []
                    for key in a.keys():
                        ass.append(a[key])
                        
                    print_emoji = " ".join(ass)
                    try:
                        await message.delete()
                        await message.channel.send(print_emoji)
                        print(f"{time()-sa}")

                    except NotFound:
                        pass

            

bot = Bot()