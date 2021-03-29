from discord.ext.commands import Cog, command

from ..db import db

class Welcome(Cog):
    def __init__(self,bot):
        self.bot = bot
        

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("welcome")

    @Cog.listener()
    async def on_member_join(self, member):
        db.execute("INSERT INTO exp (UserID) VALUES (?)", member.id)
        await self.bot.get_channel(752543820402655312).send(f"Selamat datang ke dalam **{member.guild.name}** {member.mention}!\nSemoga Betah")
        #untuk dm try:
        #  await member.send(text)
        # except Forbidden: 
        #  pass
        #untuk add role = await member.add_roles(role1, role2) or await member.add_roles(*(member.guild.get_role(id_) for id_ in (id1, id2)))
        # await member.edit(roles=[*member.roles, *[member.guild.get_role(id_) for id_ in (id1,id2)]])

    @Cog.listener()
    async def on_member_remove(self, member):
        db.execute("DELETE FROM exp WHERE (UserID) = (?)", member.id)
        await self.bot.get_channel(752543820402655312).send(f"**{member.display_name}** telah meninggalkan **{member.guild.name}** Press F")


def setup(bot):
    bot.add_cog(Welcome(bot))