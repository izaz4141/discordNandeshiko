from types import NoneType
from discord.ext.commands import Cog
from discord.errors import NotFound

from os import getenv

from ..db import db

DESKTOP_KEY = getenv("DESKTOP_KEY")

class NQN(Cog):
    def __init__(self, bot):
        self.bot = bot
        
    async def act(self, message, emoji):
        nick = message.author.nick or message.author.name
        webhook = await message.channel.create_webhook(name=nick)
        await webhook.send(
            str(emoji), username=message.author.nick, avatar_url=message.author.avatar.url)

        webhooks = await message.channel.webhooks()
        for webhook in webhooks:
                await webhook.delete()
        
    @Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            if DESKTOP_KEY == "benar":
                if not message.author.id in self.bot.owner_ids:
                    return
            elif self.maintenance is True:
                if message.content == "maintenance off" and message.author.id in self.bot.owner_ids:
                    self.maintenance = False
                    return
                return
            if message.author.id in self.bot.owner_ids:
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
            if not message.content == '':
                if isinstance(message.guild, type(None)):
                    return
                if db.field("SELECT NQN FROM guilds WHERE GuildID = ?", message.guild.id) == 'ON':
                    l_kata = message.content.split(" ")
                    a = {}
                    bener = False
                    for i, kata in enumerate(l_kata):
                        # sa = time()
                        try:
                            if ":" == kata[0] and ":" == kata[-1]:
                                
                                bener = True
                                total_emojis =  self.bot.emojis
                                total_emojis_set = set(total_emojis)
                                emoji_name = kata[1:-1]
                                kum_emoji = emoji_name.split('::')
                                # kumpul_emoji = "".join(kumpula_emoji)
                                # kum_emoji = kumpul_emoji.split(': :')
                                # kum_emoji_set = set(kum_emoji)
                                for n, nama_emoji in enumerate(kum_emoji):
                                    for emoji in total_emojis_set:
                                        if nama_emoji.lower() == emoji.name.lower():
                                            a[f"{nama_emoji}_{i}_{n}"] = str(emoji)
                                            break
                                        
                                        
                            else:
                                a[i] = kata
                        except IndexError:
                            pass
                    salah = False
                    for key in a.keys():
                        if a[key][0] == "<" and a[key][-1] == ">":
                            salah = True
                            break
                    
                    if bener is True and salah is True:
                        ass = []
                        for key in a.keys():
                            ass.append(a[key])
                            
                        print_emoji = " ".join(ass)
                        try:
                            await message.delete()
                            await self.act(message, print_emoji)
                            # print(f"{time()-sa}")

                        except NotFound:
                            pass
        
    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("nqn")
            
def setup(bot):
    bot.add_cog(NQN(bot))