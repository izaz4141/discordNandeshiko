from discord.ext.commands import Cog, command
from discord.ext.menus import MenuPages, ListPageSource
from discord.utils import get
from discord import Embed, File
from typing import Optional

Forbidden_Cog = ["developer"]

def syntax(command):
    cmd_and_alias = " | ".join([str(command), *command.aliases])
    params = []

    for key, value in command.params.items():
        if key not in ("self", "ctx"):
            params.append(f"{key}" if "NoneType" in str(value) else f"<{key}>")

    params = " ".join(params)

    return f"```{cmd_and_alias} {params}```"


class HelpMenu(ListPageSource):
    def __init__(self, ctx, data, cmd, owner_ids):
        self.ctx = ctx
        self.cmd = cmd
        self.owner_ids = owner_ids

        super().__init__(data, per_page=3)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*self.per_page) + 1
        len_data = len(self.entries)

        embed = Embed(title="Help",
                      description="Selamat datang ke Menu Help Campers!",
                      colour=self.ctx.author.colour)
        cog_command = {}
        for cog in fields:
            cog_command[cog] = []
        for comand in list(self.cmd):
            beneer = False
            for cog in fields:
                if comand.cog_name == cog:
                    cmdcog_name = cog
                    beneer = True
                    break
            if beneer is True:
                cog_command[cmdcog_name].append(syntax(comand))
        embed.set_thumbnail(url=self.ctx.guild.me.avatar_url)
        embed.set_footer(text=f"{offset:,} - {min(len_data, offset + self.per_page - 1):,} dari {len_data:,} Cog.")
        fields = []
        for name, value in zip(list(cog_command.keys()), list(cog_command.values())):
            value = "\n".join(value)
            if name == '':
                name = "Unknown Cog"
            
            elif value == '':
                value = "Tidak ada perintah dalam Cog ini"
            if name.lower() in Forbidden_Cog:
                if self.ctx.author.id in self.owner_ids:
                    fields.append((name, value))
            else:
                fields.append((name, value))
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        fields = []
        

        for entry in entries:
            fields.append(entry)

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

        embed.set_thumbnail(url=self.ctx.guild.me.avatar_url)
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
            menu = MenuPages(source=HelpMenu(ctx, list(self.bot.cogs.keys()), list(self.bot.commands), self.bot.owner_ids),
                            #  delete_message_after=True,
                            clear_reactions_after= True,
                             timeout=60.0)# bisa ditambah clear_reaction_after=True
            await menu.start(ctx)

        else:
            command = get(self.bot.commands, name=cmd)
            if command is True:
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
            description = f"Dibuat Oleh: {self.bot.get_user(self.bot.owner_ids[0]).name}#{self.bot.get_user(self.bot.owner_ids[0]).discriminator}",
            colour= ctx.author.colour
        )
        fields = [
            ("Invite Link", "https://bit.ly/3sTBi5K")
        ]
        embed.set_author(icon_url=self.bot.get_user(self.bot.owner_ids[0]).avatar_url, name= f"{self.bot.get_user(self.bot.owner_ids[0]).name}#{self.bot.get_user(self.bot.owner_ids[0]).discriminator}")
        embed.set_thumbnail(url=ctx.guild.me.avatar_url)
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
        embed.set_author(icon_url=self.bot.get_user(self.bot.owner_ids[0]).avatar_url, name= f"{self.bot.get_user(self.bot.owner_ids[0]).name}#{self.bot.get_user(self.bot.owner_ids[0]).discriminator}")
        embed.set_thumbnail(url=ctx.guild.me.avatar_url)
        await ctx.send(embed=embed)
        
            
    @Cog.listener()
    async def on_ready(self):
        self.bot.cogs_ready.ready_up("help")




def setup(bot):
    bot.add_cog(Help(bot))
