from discord.ext.commands import Cog, command, is_owner
from discord.utils import get
from discord import Embed, User, Member

from os import execv, getenv
from sys import executable, argv
from subprocess import run, PIPE
from datetime import datetime
from urllib3 import PoolManager
from json import loads
import asyncio
import random
import shutil
import os

from ..db import db
from ..utils.menus import MenuPages, ListPageSource

urlp = PoolManager()

class IsiStatistik(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx

        super().__init__(data, per_page=1)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*1) + 1
        len_data = len(self.entries)

        embed = Embed(title=self.entries[menu.current_page][1],
                      description= f"Members: {len(list(filter(lambda m: not m.bot, self.entries[menu.current_page][2].members)))}\nBots: {len(list(filter(lambda m: m.bot, self.entries[menu.current_page][2].members)))}" ,
                      colour=self.ctx.author.colour)
        
        fields = []
        if self.entries[menu.current_page][0] == {} or self.entries[menu.current_page][0] == 0:
            embed.add_field(name="Commands", value="Server ini belum pernah memakai command")
        else:
            commands = sorted(self.entries[menu.current_page][0].keys())
            grup = [[command, self.entries[menu.current_page][0][command]] for command in commands]
            grup = sorted(grup, key= lambda y: y[1], reverse= True)
            grup = "\n".join([f"{command[0]}: {command[1]}" for command in grup])
            fields.append(("Commands", grup))
            # for command in commands:
            #     fields.append((commands, self.entries[menu.current_page][0][command]))
            
            for name, value in fields:
                if value == '':
                    value = 'Tidak Diketahui'
                embed.add_field(name=name,value=value,inline=True)
        if not isinstance(self.entries[menu.current_page][2].icon, type(None)):
            embed.set_thumbnail(url=self.entries[menu.current_page][2].icon.url)
        embed.set_footer(text=f"{offset:,} dari {len_data:,} server.")

        # for name, value in fields:
        #     embed.add_field(name=name, value=value, inline=False)
        return embed
    async def format_page(self, menu, entries):
        fields = []
        
        

        
        # fields.append((entries["title"], f"Score = {entries['score']:,.2f}\nTipe = {entries['type']}\nEpisodes = {entries['episodes']:,}\nSinopsis =\n{entries['synopsis']}"))

        return await self.write_page(menu, fields)
    
class IsiServerList(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx

        super().__init__(data, per_page=4)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*self.per_page) + 1
        len_data = len(self.entries)

        embed = Embed(title="Server List",
                      colour=self.ctx.author.colour)
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)
        
        embed.set_footer(text=f"{offset:,} - {min(len_data, offset + self.per_page - 1):,} dari {len_data:,} server.")
        return embed
    async def format_page(self, menu, entries):
        fields = []
        
        for entry in entries:
            wel = db.field("SELECT Welcome FROM guilds WHERE GuildID = ?", entry.id)
            leg = db.field("SELECT Leg FROM guilds WHERE GuildID = ?", entry.id)
            nqn = db.field("SELECT NQN FROM guilds WHERE GuildID = ?", entry.id)
            fields.append((entry.name, f"Members: {len(list(filter(lambda m: not m.bot, entry.members)))}\nBots: {len(list(filter(lambda m: m.bot, entry.members)))}\nWelcome: {wel}\nLog: {leg}\nNQN: {nqn}"))

        # fields.append((entries["title"], f"Score = {entries['score']:,.2f}\nTipe = {entries['type']}\nEpisodes = {entries['episodes']:,}\nSinopsis =\n{entries['synopsis']}"))

        return await self.write_page(menu, fields)

class IsiPendApp(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx

        super().__init__(data, per_page=10)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*self.per_page) + 1
        len_data = len(self.entries)

        embed = Embed(title="Pending Application Command",
                      colour=self.ctx.author.colour,
                      timestamp=datetime.utcnow())
        for name, value in fields:
            if value == "":
                value = "No Description"
            embed.add_field(name=name, value=value, inline=False)
        
        embed.set_footer(text=f"{offset:,} - {min(len_data, offset + self.per_page - 1):,} dari {len_data:,} server.")
        return embed
    async def format_page(self, menu, entries):
        fields = []
        
        for entry in entries:
            fields.append((entry.name, entry.description))

        # fields.append((entries["title"], f"Score = {entries['score']:,.2f}\nTipe = {entries['type']}\nEpisodes = {entries['episodes']:,}\nSinopsis =\n{entries['synopsis']}"))

        return await self.write_page(menu, fields)

class Developer(Cog):
    def __init__(self,bot):
        self.bot = bot
        
    async def download_image(self, url, file_path, file_name):
        full_path = file_path + file_name + '.jpg'
        loop = self.bot.loop or asyncio.get_event_loop()
        with open(full_path, 'wb') as out:
            r = await loop.run_in_executor(None, lambda: urlp.request('GET', url, preload_content=False))
            shutil.copyfileobj(r, out)
            r.release_conn()
        
    @command(name="serverlist")
    async def server_list(self,ctx):
        """Menampilkan seluruh server yang Nadeshiko masuki
        """
        if not ctx.author.id in self.bot.owner_ids:
            return
        
        servers = [[guild, guild.name] for guild in self.bot.guilds if not guild.name in self.bot.SERVER_EXCEPTION]
        servers = sorted(servers, key= lambda y: y[1])
        servers = [server[0] for server in servers]
        menu = MenuPages(source=IsiServerList(ctx, servers),
                        # delete_message_after=True,
                        timeout=60.0)# bisa ditambah clear_reaction_after=True
        await menu.start(ctx)
        
    @command(name="servercommandstatistics", aliases=['scs'])
    async def server_command_statistics(self,ctx):
        """Menampilkan statistik command yang diinvoke tiap server
        """
        if not ctx.author.id in self.bot.owner_ids:
            return
        statistics = []
        for guild in self.bot.guilds:
            stat = db.record("SELECT Statistics FROM guilds WHERE GuildID = ?", guild.id)[0]
            try:
                stat = loads(stat)
            except Exception:
                stat = 0
            if not guild.name in self.bot.SERVER_EXCEPTION:
                statistics.append([stat, guild.name, guild])
        statistics = sorted(statistics, key= lambda y: y[1])
        menu = MenuPages(source=IsiStatistik(ctx, statistics),
                        # delete_message_after=True,
                        timeout=60.0)# bisa ditambah clear_reaction_after=True
        await menu.start(ctx)
    
    @command(name="guildsplash", aliases=['gs'])
    async def guild_splash(self,ctx, *, nama):
        """Melihat Url Splash Invite Server

        Args:
            nama (str): Nama Server
        """
        if not ctx.author.id in self.bot.owner_ids:
            return
        servers = {}
        for guild in self.bot.guilds:
            servers[guild.name] = guild.id
        if not nama in servers.keys():
            return await ctx.send(f"Maaf kak server dengan nama {nama} tidak ditemukan...")
        guild = self.bot.get_guild(servers[nama])
        await ctx.send(guild.splash.url)
        
    @command(name="leaveguild")
    async def leave_guild(self, ctx, *, guild_name):
        """Meninggalkan server berdasar nama servernya

        Args:
            guild_name (str): Nama server yang ingin ditinggalkan
        """
        if not ctx.author.id in self.bot.owner_ids:
            return
        guild = get(self.bot.guilds, name=guild_name)
        if guild is None:
            return ctx.send("Lapor, Tidak ada server dengan nama itu Komandan!")
        await guild.leave() # Guild found
        await ctx.send(f"Nadeshiko meninggalkan **{guild.name}**!")
        
    @command(name="changeavatar", aliases=["ca"])
    async def change_avatar(self, ctx, *, link="Takda"):
        """Mengganti Avatar Nandeshikyot

        Args:
            link (str, optional): Link Gambar Baru. Defaults to "Takda".
        """
        if not ctx.author.id in self.bot.owner_ids:
            return
        if link == "Takda":
            img_format = ["jpg", "png", "gif", "jpeg"]
            if ctx.message.reference:
                link = await ctx.fetch_message(ctx.message.reference.message_id)
            elif not ctx.message.attachments == []:
                link = ctx.message
            else:
                def _check(m):
                    if m.author == ctx.author:
                        
                        for forma in img_format:
                            try:
                                if forma in m.attachments[0].filename:
                                    return True
                            except IndexError:
                                if forma in m.content:
                                    return True
                msg = await ctx.send("Kirim gambar kak")
                
                try:
                    link = await self.bot.wait_for("message", timeout=60, check=_check)
                except asyncio.TimeoutError:
                    await msg.delete()
                    await ctx.send("Ih kacang")
            if not link =="Takda":
                file_name = "Avatar" + str(random.randint(1, 101))
                await self.download_image(link.attachments[0].url, "./data/temp-image/", file_name)
                # Read Image
                with open(f"./data/temp-image/{file_name}.jpg", 'rb') as image:
                    await self.bot.user.edit(avatar=image.read())
                
                os.remove(f"./data/temp-image/{file_name}.jpg")
                await ctx.send("Foto Profil telah berhasil diubah~")
                
        else:
            file_name = "Avatar" + str(random.randint(1, 101))
            await self.download_image(link, "./data/temp-image/", file_name)
            # Read Image
            with open(f"./data/temp-image/{file_name}.jpg", 'rb') as image:
                await self.bot.user.edit(avatar=image.read())
            
            os.remove(f"./data/temp-image/{file_name}.jpg")
            await ctx.send("Foto Profil telah berhasil diubah~")
            
    @command(name= "user_info")
    async def us_info(self,ctx,*,target):
        if not ctx.author.id in self.bot.owner_ids:
            return
        if target.isdigit():
            target = self.bot.get_user(int(target))
            if isinstance(target, type(None)):
                return await ctx.send("Maaf kak Nadeshiko tidak dapat menemukan user dengan ID tersebut >_<'")
        else:
            return await ctx.send("Argumen Harus merupakan suatu ID Int")

        embed = Embed(title="Info User",
                      colour=target.colour,
                      timestamp = datetime.utcnow())
        if isinstance(target, User):
            fields = [("Nama", f"{target.name}#{target.discriminator}", True),
                    ("ID", target.id, False),
                    ("Tanggal Akun Dibuat", target.created_at.strftime("%d/%m/%Y %H:%M:%S"), False),
                    ("Mutual Guilds", '\n'.join([guild.name for guild in target.mutual_guilds]), False),
                    ("Hp Status", f"{str(target.mutual_guilds[0].get_member(target.id).mobile_status)}", True),
                    ("Web Status", f"{str(target.mutual_guilds[0].get_member(target.id).web_status)}", True),
                    ("Desktop Status", f"{str(target.mutual_guilds[0].get_member(target.id).desktop_status)}", True),
                    ("Client Status", f"{''.join(''.join(str(target.mutual_guilds[0].get_member(target.id)._client_status).split('{')).split('}'))}", False)
                    ]
        for name, value, inline in fields:
            if value == '':
                value = "Tidak Diketahui"
            embed.add_field(name=name, value=value, inline=inline)
        if not isinstance(target.avatar, type(None)):
            embed.set_thumbnail(url=target.avatar.url)
        await ctx.send(embed=embed)

    @command(name="pendingappcmd", aliases=["pac"])
    async def pending_app_comand(self,ctx):
        """
        Melihat Application command yang masih pending
        """
        apps = [[app, app.name] for app in self.bot.pending_application_commands]
        apps = sorted(apps, key= lambda y: y[1])
        apps = [app[0] for app in apps]
        menu = MenuPages(source=IsiPendApp(ctx, apps),
                        # delete_message_after=True,
                        timeout=60.0)# bisa ditambah clear_reaction_after=True
        await menu.start(ctx)
        
    @command(name="fullrestart")
    async def full_restart(self, ctx):
        """Restart bot dengan menjalankan launcher
        """
        if not ctx.author.id in self.bot.owner_ids:
            return
        await ctx.send("Restarting bot...")
        execv(executable, ['python'] + argv)
        
    @command(name="terminal")
    async def terminal(self, ctx, *, command):
        """Menjalankan command terminal

        Args:
            command (str): Command yang ingin dijalankan
        """
        if not ctx.author.id in self.bot.owner_ids:
            return
        commands = command.split(' ')
        loop = self.bot.loop or asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: run(commands, stdout= PIPE))
        output = result.stdout.decode('utf-8')
        await ctx.send(output[:2000])
    
    @command(name="secrets")
    async def show_your_secrets(self, ctx):
        """Menunjukkan Access Token yang dipakai"""
        if not ctx.author.id in self.bot.owner_ids:
            return
        discord_key = getenv("DIS_KEY")
        dropbox_key = getenv("DROPBOX_KEY")
        openai_key = getenv("OPENAI_KEY")
        key_list = {
            'Discord': discord_key,
            'Dropbox': dropbox_key,
            'OpenAI': openai_key
        }

        for i in range(3):
            await ctx.send(f"{list(key_list.keys())[i]} = {list(key_list.values())[i]}")
            await asyncio.sleep(1.5)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("developer")
        
def setup(bot):
    bot.add_cog(Developer(bot))