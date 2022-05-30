from discord.ext.commands import Cog, command
from ..utils.menus import MenuPages, ListPageSource
from discord.utils import get
from discord import Embed, File
from typing import Optional

Forbidden_Cog = ["developer", "private"]

def syntax(command):
    cmd_and_alias = " | ".join([str(command), *command.aliases])
    params = []

    for key, value in command.params.items():
        if key not in ("self", "ctx"):
            params.append(f"{key}" if "NoneType" in str(value) else f"<{key}>")

    params = " ".join(params)

    return f"```{cmd_and_alias} {params}```"


class HelpMenu(ListPageSource):
    def __init__(self, ctx, data, owner_ids):
        self.ctx = ctx
        self.owner_ids = owner_ids

        super().__init__(data, per_page=3)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*self.per_page) + 1
        len_data = len(self.entries)

        embed = Embed(title="Help",
                      description="Selamat datang ke Menu Help Campers!",
                      colour=self.ctx.author.colour)
        
        embed.set_thumbnail(url=self.ctx.guild.me.avatar.url)
        embed.set_footer(text=f"{offset:,} - {min(len_data, offset + self.per_page - 1):,} dari {len_data:,} Cog.")

        for name, value in fields:
            if name in Forbidden_Cog and not self.ctx.author.id in self.owner_ids:
                continue
            if value == '':
                value = "Cog ini tidak memiliki perintah!"
            embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        fields = []
        
        for entry in entries:
            cmd_line = '\n'.join([syntax(cmd) for cmd in entry[0]])
            fields.append((entry[1], cmd_line))

        return await self.write_page(menu, fields)

class HelpCogMenu(ListPageSource):
    def __init__(self, ctx, data, cog):
        self.ctx = ctx
        self.cog = cog
        super().__init__(data, per_page=7)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*self.per_page) + 1
        len_data = len(self.entries)

        embed = Embed(title=f"Help {self.cog}",
                      description="Selamat datang ke Menu Help Campers!",
                      colour=self.ctx.author.colour)

        embed.set_thumbnail(url=self.ctx.guild.me.avatar.url)
        embed.set_footer(text=f"{offset:,} - {min(len_data, offset + self.per_page - 1):,} dari {len_data:,} perintah.")

        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        fields = []
        
        for entry in entries:
            if entry.help is None:
                fields.append((">: " + syntax(entry), entry.help or "Tidak ada deskripsi."))
            else:
                fields.append((">: " + syntax(entry), entry.help.split("\n")[0] if not None else "Tidak ada deskripsi."))

        return await self.write_page(menu, fields)

class Help(Cog):
    def __init__(self, bot):
        self.bot = bot
        for ccom in self.bot.commands:
            if ccom.name == "help":
                try:
                    if not ccom.aliases[0] == "helps":
                        self.bot.remove_command("help")
                        break
                except IndexError:
                     self.bot.remove_command("help")

    async def cmd_help(self, ctx, command):
        if command.cog_name.lower() in Forbidden_Cog:
            if not ctx.author.id in self.bot.owner_ids:
                await ctx.send("Kakak tau perintah ini dari siapa? 🔪🔪🔪")
                return await ctx.send(file= File('./data/image/smiring.jpg'))
        embed = Embed(title=f"Help with `{command}`",
                      description=syntax(command),
                      colour=ctx.author.colour)
        embed.add_field(name="Deskripsi perintah", value=command.help)
        await ctx.send(embed=embed)
        
    async def cog_help(self, ctx, cog):
        if cog.lower() in Forbidden_Cog :
            if not ctx.author.id in self.bot.owner_ids:
                await ctx.send("Kakak tau perintah ini dari siapa? 🔪🔪🔪")
                return await ctx.send(file= File('./data/image/smiring.jpg'))
        cog_command = []
        for comand in list(self.bot.commands):
            if comand.cog_name.lower() == cog.lower():
                cog_command.append(comand)
                
        menu = MenuPages(source=HelpCogMenu(ctx, cog_command, cog),
                            #  delete_message_after=True,
                            clear_reactions_after= True,
                             timeout=60.0)# bisa ditambah clear_reaction_after=True
        await menu.start(ctx)

    @command(name="help", aliases= ["helps"])
    async def show_help(self, ctx, cmd: Optional[str]):
        """Menu help untuk semua perintah (tanpa argumen), cog, perintah individu

        Contoh : 
        ```help fun```
        """
        if cmd is None:
            cogs = {}
            for cmd in self.bot.commands:
                try:
                    cogs[cmd.cog_name].append(cmd)
                except Exception:
                    cogs[cmd.cog_name] = [cmd]
            cogg = [[cogs[cog], cog] for cog in cogs.keys()]
            cogs_sorted = sorted(cogg, key= lambda y: y[1])
            menu = MenuPages(source=HelpMenu(ctx, cogs_sorted, self.bot.owner_ids),
                            #  delete_message_after=True,
                            clear_reactions_after= True,
                             timeout=60.0)# bisa ditambah clear_reaction_after=True
            await menu.start(ctx)

        else:
            command = get(self.bot.commands, name=cmd)
            if command:
                await self.cmd_help(ctx, command)
            
            elif cmd.lower() in [key.lower() for key in list(self.bot.cogs.keys())]:
                await self.cog_help(ctx, cmd)

            else:
                coom = list(self.bot.commands)
                aliasess = {}
                benar = False
                for comman in coom:
                    aliasess[comman.name] = [alias for alias in comman.aliases]
                for i, value in enumerate(list(aliasess.values())):
                    if benar is True:
                        break
                    for  cooom in value:
                        if cmd == cooom:
                            comand = list(aliasess.keys())[i]
                            for en,com_name in enumerate(coom):
                                if com_name.name.lower() == comand.lower():
                                    command_obj = coom[en]
                                    break
                            try:
                                await self.cmd_help(ctx, command_obj)
                                benar = True
                            except Exception:
                                pass
                            break
                if benar is False:
                    await ctx.send("Nandeshiko belum bisa melakukan perintah itu")
    @command(name="about")
    async def about_bot(self,ctx):
        """Segalanya Tentang Nandeshikyot-bot!"""
        embed = Embed(
            title= "About Nandeshikyot-bot",
            description = f"Dibuat Oleh: {self.bot.get_user(self.bot.owner_ids[0]).name}#{self.bot.get_user(self.bot.owner_ids[0]).discriminator}\nFacebook: https://web.facebook.com/Glicole/",
            colour= ctx.author.colour
        )
        fields = [
            ("Invite Link", "https://bit.ly/3sTBi5K")
        ]
        embed.set_author(icon_url=self.bot.get_user(self.bot.owner_ids[0]).avatar.url, name= f"{self.bot.get_user(self.bot.owner_ids[0]).name}#{self.bot.get_user(self.bot.owner_ids[0]).discriminator}")
        embed.set_thumbnail(url=ctx.guild.me.avatar.url)
        for name, value in fields:
            embed.add_field(name=name, value=value)
        await ctx.send(embed=embed)
        
    @command(name="invite", aliases= ["invitelink"])
    async def invite_link(self,ctx):
        """Menunjukkan link untuk mengundang Nandeshikyot-bot"""
        embed = Embed(
            title= "Invite Link",
            description= "https://bit.ly/3sTBi5K",
            colour = ctx.author.colour
        )
        embed.set_author(icon_url=self.bot.get_user(self.bot.owner_ids[0]).avatar.url, name= f"{self.bot.get_user(self.bot.owner_ids[0]).name}#{self.bot.get_user(self.bot.owner_ids[0]).discriminator}")
        embed.set_thumbnail(url=ctx.guild.me.avatar.url)
        await ctx.send(embed=embed)
        
            
    @Cog.listener()
    async def on_ready(self):
        self.bot.cogs_ready.ready_up("help")




def setup(bot):
    bot.add_cog(Help(bot))
