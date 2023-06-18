from discord.ext.commands import Cog, command

from os import getenv
import asyncio
from characterai import PyAsyncCAI

client = PyAsyncCAI(getenv('CHARAI_KEY'))

class Chat_CharacterAI(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.char = 'Hqec4AxMR-ghpMfuFiBNjHYJ2S76Gce-s4dZe8PVq6M'
        self.history_id = 'Q4WRSP_eHDZmsilsW_gyBKGF10Gboz78xnX3mtVCANA'
    @command(name="chat", aliases=["c"])
    async def chat(self, ctx, *, message):
        """Chatting With Nandeshikyot (deprecated/need money)

            Args:
                message (str): Inquiries
        """
        message = f"{ctx.author.name}: {message}"
        data = await client.chat.send_message(
            self.char, message, history_external_id=self.history_id, tgt=self.tgt, wait= True
        )

        text = data['replies'][0]['text']
        ctx.send(text)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            await client.start()
            self.chat = await client.chat.get_chat(self.char, wait=True)

            self.participants = self.chat['participants']
            # In the list of "participants",
            # a character can be at zero or in the first place
            if not self.participants[0]['is_human']:
                self.tgt = self.participants[0]['user']['username']
            else:
                self.tgt = self.participants[1]['user']['username']

            self.bot.cogs_ready.ready_up("chat_CharacterAI")

def setup(bot):
    bot.add_cog(Chat_CharacterAI(bot))
