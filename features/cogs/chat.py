from discord.ext.commands import Cog, command
from discord.utils import get

from ..cogs.help import Help
from chatterbot import ChatBot
from chatterbot.response_selection import get_random_response
from random import choices
from datetime import datetime


class Chat(Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @command(name="chat")
    async def chatting(self, ctx, *, query):
        cbot = ChatBot( name= "Nadeshiko",
                        read_only= True,
                        storage_adapter='chatterbot.storage.SQLStorageAdapter',
                        logic_adapters= [
                            {
                                "import_path": "chatterbot.logic.BestMatch",
                                "response_selection_method": get_random_response,
                                "default_response": "Maaf kak, Nadeshiko tidak paham...",
                                "maximum_similarity_threshold": 0.60
                            }
                        ],
                        database_uri='sqlite:///database.sqlite3'
                        )
        try:
            bot_response = cbot.get_response(query)
            if bot_response.text =="waktu":
                jam = datetime.now().strftime('%I:%M %p')
                waktu = [f"Sekarang pukul {jam} Kak.", f"Ini jam {jam}"]
                response = choices(waktu)
                await ctx.send(response)
            elif bot_response.text == "help":
                await Help(self.bot).cmd_help(ctx, get(self.bot.commands, name="help"))
            else:
                await ctx.send(bot_response.text)

        # Press ctrl-c or ctrl-d on the keyboard to exit
        except Exception:
            await ctx.send("Maaf kak, Nadeshiko tidak paham...")
        
        
    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("chat")


def setup(bot):
    bot.add_cog(Chat(bot))