from discord.ext.commands import Cog, CheckFailure, command, has_permissions, has_role

from datetime import datetime, timedelta
from random import randint
from ..db import db

inBattle = []






class Game(Cog):
    def __init__(self,bot):
        self.bot = bot

    async def process_xp(self, message):
        xp, lvl, xplock = db.record("SELECT XP, Level, XPLock FROM exp WHERE UserID = ?", message.author.id)

        if datetime.fromisoformat(xplock) < datetime.utcnow():
            await self.add_xp(message, xp, lvl)

    async def add_xp(self, message, xp, lvl):
        xp_to_add = randint(10,20)
        new_level = int(((xp+xp_to_add)//42) ** 0.55)

        db.execute("UPDATE exp SET XP = XP + ? , Level = ?, XPLock = ? WHERE UserID = ?",
                    xp_to_add, new_level, (datetime.utcnow()+timedelta(seconds=45)).isoformat(), message.author.id)

        if new_level > lvl:
            await self.levelup_channel.send(f"**{message.author.display_name}** telah mencapai level {new_level:,}, GJ")
        
    # def battle(self, message):
    #     self.

    



    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.levelup_channel = self.bot.get_channel(823774055134920765)
            self.bot.cogs_ready.ready_up("game")

    @Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            await self.process_xp(message)


def setup(bot):
    bot.add_cog(Game(bot))