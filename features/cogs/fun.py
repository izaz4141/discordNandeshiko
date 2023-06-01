from discord.ext.commands import Cog, command, BadArgument, cooldown, BucketType, slash_command
from random import choice, randint
from discord import Member, Embed, ApplicationContext, option
from discord.errors import HTTPException, Forbidden
from ..utils.menus import MenuPages, ListPageSource
from typing import Optional
from aiohttp import request
# from jikanpy import Jikan
# from datetime import datetime
from pybooru import Danbooru, Moebooru
from pygelbooru import Gelbooru
from tenacity import retry, stop_after_attempt, wait_fixed
# from difflib import get_close_matches
from ..utils.saucenao_api.saucenao_api import SauceNao
from ..utils import wordle, kataple

import asyncio
from ..db import db

dclient = Danbooru("danbooru")
sclient = Danbooru("safebooru")
kclient = Moebooru("konachan")
yclient = Moebooru("yandere")
lclient = Moebooru("lolibooru")
gclient = Gelbooru()
sauce = SauceNao(api_key="b6bf271b3608983569e56e08ef9c7244fc424ac8")

# class IsiTagsList(ListPageSource):
#     def __init__(self, ctx, data, animek):
#         self.ctx = ctx
#         self.animek = animek

#         super().__init__(data, per_page=20)

#     async def write_page(self, menu, fields=[]):
#         offset = (menu.current_page*self.per_page) + 1
#         len_data = len(self.entries)
#         chara = "\n".join(cr for cr in fields)
#         embed = Embed(title=self.animek,
#                       description = f"```{chara}```",
#                       colour=self.ctx.author.colour)
        
#         # for name, value in fields:
#         #     embed.add_field(name=name,value=value,inline=False)

#         embed.set_footer(text=f"{offset:,} - {min(len_data, offset + self.per_page - 1):,} dari {len_data:,} hasil.")


#         return embed

#     async def format_page(self, menu, entries):
#         fields = []
        
        

#         for entry in entries:
#             fields.append(entry)

#         return await self.write_page(menu, fields)

class PostListD(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx

        super().__init__(data, per_page=1)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*1) + 1
        len_data = len(self.entries)
        post_detail = self.entries[menu.current_page]
        try:
            embed = Embed(title= " ".join(f"[{char}]" for char in post_detail["tag_string_character"].split(" ")[:5]),
                        description= post_detail["id"],
                        colour=self.ctx.author.colour)
        except KeyError :
            embed = Embed(title= " ".join(f'[{char}]' for char in post_detail["tag_string_character"].split(" ")[:5]),
                        description= "No Id",
                        colour= self.ctx.author.colour)
        if not post_detail["pixiv_id"] is None:
            sauce =  "https://www.pixiv.net/artworks/" + str(post_detail["pixiv_id"])
        else:
            sauce = post_detail["source"]
        
        artis = post_detail["tag_string_artist"]
        fields = [
            ("Artist", artis),
            ("Source", sauce),
            ("Tags", "```"+" ".join(f'[{tag}]' for tag in post_detail["tag_string_general"].split(" ")[:20])+"```")
        ]
        
        for name, value in fields:
            if value == '':
                value = "Tidak Diketahui"
            embed.add_field(name=name, value=value, inline=False)
        img_format = ["jpg", "png", "gif", "jpeg"]
        vid_format = ["webm", "mp4", "mkv"]
        try:
            imag = False
            for forma in img_format:
                if forma in post_detail["file_ext"]:
                    imag = True
                    embed.set_image(url=post_detail["file_url"])
                    break
                    
            if imag is False:
                embed.set_image(url=post_detail["preview_file_url"])
            
        
                    
        except KeyError:
            pass
        
        try:
            for forma in vid_format:
                large_fu = post_detail["large_file_url"]
                if forma in post_detail["file_ext"]:
                    embed.add_field(name="Video", value= post_detail["file_url"], inline=False)
                
                elif forma in large_fu:
                    embed.add_field(name="Video", value= post_detail["large_file_url"], inline=False)
        except KeyError:
            pass
            
        
        
        embed.set_footer(text=f"{offset:,} of {len_data:,} hasil.")

        # for name, value in fields:
        #     embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        fields = []
        
        
        return await self.write_page(menu, fields)
    
class IsiSearchTag(ListPageSource):
    def __init__(self, ctx, data, term):
        self.ctx = ctx
        self.term = term

        super().__init__(data, per_page=20)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*self.per_page) + 1
        len_data = len(self.entries)
        chara = "\n".join(cr for cr in fields)
        embed = Embed(title=f"Hasil Search: {self.term}",
                      description = f"```{chara}```",
                      colour=self.ctx.author.colour)
        
        # for name, value in fields:
        #     embed.add_field(name=name,value=value,inline=False)

        embed.set_footer(text=f"{offset:,} - {min(len_data, offset + self.per_page - 1):,} dari {len_data:,} hasil.")


        return embed

    async def format_page(self, menu, entries):
        fields = []
        
        

        for entry in entries:
            fields.append(entry)

        return await self.write_page(menu, fields)
    
class PostListK(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx

        super().__init__(data, per_page=1)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*1) + 1
        len_data = len(self.entries)
        post_detail = self.entries[menu.current_page]
        embed = Embed(title= post_detail["author"],
                    description= f"({post_detail['width']}X{post_detail['height']})",
                    colour=self.ctx.author.colour)
        
        sauce = post_detail["source"]
        if sauce == "":
            sauce = "Unknown"
        elif "pximg" in sauce:
            sauced = sauce.split("/")[-1].split("_")[0]
            sauce = "https://pixiv.net/artworks/" + str(sauced)
        
        fields = [
            ("Source", sauce),
            ("Tags", "```"+" ".join(f'[{tag}]' for tag in post_detail["tags"].split(" ")[:20])+"```")
        ]
        
        for name, value in fields:
            if value == '':
                value = "Tidak Diketahui"
            embed.add_field(name=name, value=value, inline=False)
            
        try:
            embed.set_image(url=post_detail["jpeg_url"])
        except KeyError:
            pass
        embed.set_footer(text=f"{offset:,} of {len_data:,} hasil.")

        # for name, value in fields:
        #     embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        fields = []
        
        
        return await self.write_page(menu, fields)
    
class PostListL(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx

        super().__init__(data, per_page=1)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*1) + 1
        len_data = len(self.entries)
        post_detail = self.entries[menu.current_page]
        embed = Embed(title= post_detail["author"],
                    description= f"({post_detail['width']}X{post_detail['height']})",
                    colour=self.ctx.author.colour)
        
        sauce = post_detail["source"]
        if sauce == "":
            sauce = "Unknown"
        elif "pximg" in sauce:
            sauced = sauce.split("/")[-1].split("_")[0]
            sauce = "https://pixiv.net/artworks/" + str(sauced)
        
        fields = [
            ("Source", sauce),
            ("Tags", "```"+" ".join(f"[{tag}]" for tag in post_detail["tags"].split(" ")[:20])+"```")
        ]
        
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)
            
        try:
            embed.set_image(url=post_detail["preview_url"])
        except KeyError:
            pass
        embed.set_footer(text=f"{offset:,} of {len_data:,} hasil.")

        # for name, value in fields:
        #     embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        fields = []
        
        
        return await self.write_page(menu, fields)
    
class PostListG(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx

        super().__init__(data, per_page=1)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*1) + 1
        len_data = len(self.entries)
        post_detail = self.entries[menu.current_page]
        embed = Embed(title= post_detail.id,
                    description= f"({post_detail.width}X{post_detail.height})",
                    colour=self.ctx.author.colour)
        
        sauce = post_detail.source
        if sauce is None:
            sauce = "Unknown"
        elif "pximg" in sauce:
            sauced = sauce.split("/")[-1].split("_")[0]
            sauce = "https://www.pixiv.net/artworks/" + str(sauced)
        
        fields = [
            ("Source", sauce),
            ("Tags", "```"+" ".join(f"[{tag}]" for tag in post_detail.tags[:20])+"```")
        ]
        
        for name, value in fields:
            if value == '':
                value = "Tidak Diketahui"
            embed.add_field(name=name, value=value, inline=False)
            
        try:
            embed.set_image(url=post_detail.file_url)
        except KeyError:
            pass
        embed.set_footer(text=f"{offset:,} of {len_data:,} hasil.")

        # for name, value in fields:
        #     embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        fields = []
        
        
        return await self.write_page(menu, fields)
    
class IsiSauceNao(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx

        super().__init__(data, per_page=1)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*1) + 1
        len_data = len(self.entries)
        post_detail = self.entries[menu.current_page]
        embed = Embed(title= post_detail.title,
                    description= f"Similarity : {post_detail.similarity}%",
                    colour=self.ctx.author.colour)
        
        sauce = "\n".join(post_detail.urls)
        if "pximg" in sauce:
            sauced = sauce.split("/")[-1].split("_")[0]
            sauce = "https://www.pixiv.net/artworks/" + str(sauced)
            
        autor = post_detail.author
        
        fields = [("Author", autor),
            ("Source", sauce)
        ]
        
        for name, value in fields:
            if value == '':
                value = "Tidak Diketahui"
            embed.add_field(name=name, value=value, inline=False)
            
        try:
            embed.set_image(url=post_detail.thumbnail)
        except Exception:
            pass
        embed.set_footer(text=f"{offset:,} of {len_data:,} hasil.")

        # for name, value in fields:
        #     embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        fields = []
        
        
        return await self.write_page(menu, fields)

class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @command(name="luck")
    @cooldown(3, 60*60*24, BucketType.user)  #Parameternya(jumlah dipakai sebelum cd, waktu cd, type cd : member, user, guild, default)
    async def luck(self, ctx, app=False):
        """Meramalkan keberuntunganmu hari ini

        Mungkin terdapat suatu mekanisme rahasia?
        """
        luck = randint(1,100)
        if luck <= 30:
            teks = f'{luck}! Haha ampas'
        elif luck <= 50:
            teks = f'{luck}! Mayan lucknya, {luck}% berhasil. Sisanya diisi dengan semangat aja!'
        elif luck <= 80:
            ateks = f'{luck}! Kalau dihitung dari pergerakan bintang dan snezhnaya keberuntungan kaka hari ini BAIK!! :thumbsup:'
        elif luck <= 99:
            teks = f'{luck}! Enaknyaa~ aku juga pengen laksek... bagi dong ka lucknya!'
        elif luck == 100:
            teks = f"{luck}! (0 o 0 ) Gila beuhh"
        if app:
            await ctx.respond(teks)
        else:
            await ctx.send(teks)
        db.execute("UPDATE exp SET Luck = ? WHERE UserID = ?", luck, ctx.author.id)
        
    @slash_command(name='luck', description='Mengecek Stat Luck-mu')
    @cooldown(3, 60*60*24, BucketType.user)
    async def luck_slash(self, ctx):
        await self.luck(ctx, True)

    @slash_command(name="tes", description="Test CMD", guild_ids=[823535615609667624])
    async def testo(self,ctx):
        await ctx.respond("tis")

    @command(name="dice")
    async def roll_n_dice(self, ctx, die_string: str):
        dice, value = (int(msg) for msg in die_string.split("d"))
        rolls = [randint(1, value) for i in range(dice)]
        await ctx.send(" + ".join([str(r) for r in rolls]) + f" = {sum(rolls)}")
    
    @command(name="kataple")
    async def wordle_indo(self,ctx):
        """Memulai game Wordle Indonesia
        
        untuk menjawab, reply ke embed Nandeshikyot
        """
        embed = kataple.generate_puzzle_embed(ctx.author, kataple.random_puzzle_id())
        await ctx.reply(embed=embed)
        
    @command(name="wordle")
    async def wordle(self,ctx):
        """Memulai game Wordle
        
        untuk menjawab, reply ke embed Nandeshikyot
        """
        embed = wordle.generate_puzzle_embed(ctx.author, wordle.random_puzzle_id())
        await ctx.reply(embed=embed)
    
    @command(name="bilang")
    async def say(self, ctx, *, message, app=False):
        """Meminta Nandeshikyot untuk bilang sesuatu"""
        await ctx.message.delete()
        if app:
            await ctx.respond(f"{message} <:nandeshikyot:752500122415267850>")
        else:
            await ctx.send(f"{message} <:nandeshikyot:752500122415267850>")

    @slash_command(name="bilang", description="Meminta Nandeshikyot untuk bilang sesuatu")
    @option("message", description="Masukkan kata-kata ke mulut Nadeshiko")
    async def say_slash(self, ctx, message: str):
        await self.say(ctx, message=message, app=True)

    @command(name="slap")
    async def slap_member(self, ctx, member: Member, *, reason: Optional[str] = "ngeselin"):
        """Meminta Nandeshikyot untuk menampar seseorang
        Dapat disertakan alasan setelah mention member
        
        Contoh:
        ```slap @Netorare tag laknat```
        """
        if member.id == self.bot.owner_ids[0]:
            await ctx.send("Gamau")
        else: 
            await ctx.send(f"Nandeshiko menampar {member.mention} karena {reason}")
        # print(member)
    @slap_member.error
    async def slap_member_error(self, ctx, exc):
        if isinstance(exc, BadArgument):
            await ctx.send("Siapa itu?")

    @command(name="danbooru", aliases=['db'])
    async def danbooru_postList(self, ctx, *, tagss, app=False):
        """Mencari gambar/video dengan tag yang diberikan (random) (maksimal 1 tags)
        Dapat dicari kombinasi tag dengan pemisah ^
        Spasi otomatis dikonversi ke underscore (untuk kemudahan)
        
        Contoh:
        ```danbooru large breasts```
        """
        tagss = " ".join("_".join(tagss.split(" ")).split("^"))
        tagss = tagss.lower()
        hasil_post = dclient.post_list(tags=tagss, random=True, limit= 50)
        if hasil_post == []:
            if app:
                await ctx.respond(f"Tidak ditemukan post dengan tag {tagss}")
            else:
                await ctx.send(f"Tidak ditemukan post dengan tag {tagss}")
            tagl = tagss.split(" ")
            hasil_passSearch = {}
            for tagg in tagl:
                hasil_passSearch[tagg] = await self.gelbooru_passiveSearch(ctx, tagg)
            tagsatu = True
            
            for key in hasil_passSearch.keys():
                exact_tag = False
                if not len(hasil_passSearch[key]) == 1:
                    for char in hasil_passSearch[key]:
                        if char.name == key:
                            exact_tag = True
                            hasil_passSearch[key] = [char.name]
                            break
                    if exact_tag is False:
                        tagsatu = False
                        break
            if tagsatu is True:
                lis_tag = []
                for ab in hasil_passSearch.values():
                    lis_tag.append(ab[0])
                
                await self.danbooru_passivePost(ctx, tagss="^".join(lis_tag), app=app)
            else:
                for tagg in tagl:
                    await self.gelbooru_tagSearch(ctx, term=tagg)
        else:
            menu = MenuPages(source=PostListD(ctx, hasil_post),
                             clear_reactions_after=True,
                            timeout=60.0)# bisa ditambah clear_reaction_after=True
            await menu.start(ctx)

    @slash_command(name="danbooru", description="Mencari art di forum danbooru")
    @option("tag", description="Basis tag yang dicari (max 1)")
    async def danbooru_slash(self, ctx: ApplicationContext, tag):
        await self.danbooru_postList(ctx, tagss=tag, app=True)
            
            
    async def danbooru_passivePost(self,ctx, tagss, app=False):
        tagss = tagss.lower()
        tagss = " ".join("_".join(tagss.split(" ")).split("^"))
        hasil_post = dclient.post_list(tags=tagss, random=True, limit= 50)
        if hasil_post == []:
            if app:
                await ctx.respond(f"Tidak ditemukan post dengan tag {tagss}")
            else:
                await ctx.send(f"Tidak ditemukan post dengan tag {tagss}")
            
        else:
            if app:
                await ctx.respond(f"Ditemukan post dengan tag {tagss}")
            else:
                await ctx.send(f"Ditemukan post dengan tag {tagss}")
            menu = MenuPages(source=PostListD(ctx, hasil_post),
                             clear_reactions_after=True,
                            timeout=60.0)# bisa ditambah clear_reaction_after=True
            await menu.start(ctx)
            
            
    @command(name= "safebooru", aliases=['sb'])
    async def safebooru_postList(self, ctx, *, tagss):
        """Mencari gambar/video dengan tag yang diberikan (random) (maksimal 1 tags)
        Dapat dicari kombinasi tag dengan pemisah ^
        Spasi otomatis dikonversi ke underscore (untuk kemudahan)
        
        Contoh:
        ```safebooru breast grab```
        """
        tagss = " ".join("_".join(tagss.split(" ")).split("^"))
        tagss = tagss.lower()
        hasil_post = sclient.post_list(tags=tagss, random=True, limit= 50)
        if hasil_post == []:
            await ctx.send(f"Tidak ditemukan post dengan tag {tagss}")
            tagl = tagss.split(" ")
            hasil_passSearch = {}
            for tagg in tagl:
                hasil_passSearch[tagg] = await self.gelbooru_passiveSearch(ctx, tagg)
            tagsatu = True
            
            for key in hasil_passSearch.keys():
                exact_tag = False
                if not len(hasil_passSearch[key]) == 1:
                    for char in hasil_passSearch[key]:
                        if char.name == key:
                            exact_tag = True
                            hasil_passSearch[key] = [char.name]
                            break
                    if exact_tag is False:
                        tagsatu = False
                        break
            if tagsatu is True:
                lis_tag = []
                for ab in hasil_passSearch.values():
                    lis_tag.append(ab[0])
                
                await self.safebooru_passivePost(ctx, tagss="^".join(lis_tag))
            else:
                for tagg in tagl:
                    await self.gelbooru_tagSearch(ctx, term=tagg)
        else:
            menu = MenuPages(source=PostListD(ctx, hasil_post),
                             clear_reactions_after=True,
                            timeout=60.0)# bisa ditambah clear_reaction_after=True
            await menu.start(ctx)
            
    async def safebooru_passivePost(self,ctx, tagss):
        tagss = tagss.lower()
        tagss = " ".join("_".join(tagss.split(" ")).split("^"))
        hasil_post = sclient.post_list(tags=tagss, random=True, limit= 50)
        if hasil_post == []:
            await ctx.send(f"Tidak ditemukan post dengan tag {tagss}")
            
        else:
            await ctx.send(f"Ditemukan post dengan tag {tagss}")
            menu = MenuPages(source=PostListD(ctx, hasil_post),
                             clear_reactions_after=True,
                            timeout=60.0)# bisa ditambah clear_reaction_after=True
            await menu.start(ctx)
    # @command(name= "danboorutaglist", aliases=["dtl"])
    # async def danbooru_tagList(self, ctx, *, animek):
    #     animek = "_".join(animek.split(" "))
    #     animek = animek.lower()
    #     tags_list = dclient.tag_related(query= animek)
    #     char_list = False
    #     for key in tags_list["other_wikis"].keys():
    #         if "list_of_" in key and "characters" in key:
    #             wiki_tag = tags_list["other_wikis"][key]
    #             char_list = True
    #     if not char_list is True:
    #         wiki_tag = tags_list["wiki_page_tags"]
    #     if wiki_tag == []:
    #         await ctx.send(f"Tidak ditemukan tag {animek}")
    #     if not wiki_tag == []:
    #         tagss = []
    #         for i, tag in enumerate(wiki_tag):
    #             tagss.append(f"{i+1}.  {tag[0]}")
    #         # desc = "\n".join(tagss)
    #         # embed = Embed(title=animek,
    #         #               description= f"{desc:.1024s}",
    #         #               colour= ctx.author.colour)
    #         # await ctx.send(embed=embed)
    #         menu = MenuPages(source=IsiTagsList(ctx, tagss, animek),
    #                          clear_reactions_after=True,
    #                         timeout=60.0)# bisa ditambah clear_reaction_after=True
    #         await menu.start(ctx)

    @command(name="konachan", aliases=['kb'])
    async def konachan_postList(self, ctx, *, tagss):
        """Pencarian gambar/video dengan tag yang diberikan (tidak random) oleh konachan
        Dapat dicari kombinasi tag dengan pemisah ^
        Spasi otomatis dikonversi ke underscore (untuk kemudahan)
        Dapat dicari dengan dua argumen:
        tags : str dengan pemisah ^
        halaman : int dengan pemisah ::

        Contoh:
        ```konachan kagamihara nadeshiko^smile^looking at viewer::3```
        """
        pagee = 1
        if "::" in tagss:
            try:
                pagee = int(tagss.split("::")[-1])
                tagss = " ".join("_".join(tagss.split(" ")).split("::")[0].split("^"))
                tagss = tagss.lower()
                hasil_post = kclient.post_list(tags=tagss, limit= 50, page= pagee)
            except ValueError:
                await ctx.send("Halaman yang dimasukkan harus berupa bilangan bulat")
        else:
            tagss = " ".join("_".join(tagss.split(" ")).split("^"))
            tagss = tagss.lower()
            hasil_post = kclient.post_list(tags=tagss, limit= 50)
        if hasil_post == []:
            await ctx.send(f"Tidak ditemukan post dengan tag {tagss}")
            tagl = tagss.split(" ")
            hasil_passSearch = {}
            for tagog in tagl:
                hasil_passSearch[tagog] = await self.gelbooru_passiveSearch(ctx, tagog)
            tagsatu = True
            
            for key in hasil_passSearch.keys():
                exact_tag = False
                if not len(hasil_passSearch[key]) == 1:
                    for char in hasil_passSearch[key]:
                        if char.name == key:
                            exact_tag = True
                            hasil_passSearch[key] = [char.name]
                            break
                    if exact_tag is False:
                        tagsatu = False
                        break
            if tagsatu is True :
                lis_tag = []
                for ab in hasil_passSearch.values():
                    lis_tag.append(ab[0])
                
                await self.konachan_passivePost(ctx, tagss=lis_tag, pagee=pagee)
            else:
                for tagog in tagl:
                    await self.gelbooru_tagSearch(ctx, term=tagog)
        else:
            try:
                menu = MenuPages(source=PostListK(ctx, hasil_post),
                                clear_reactions_after=True,
                                timeout=60.0)# bisa ditambah clear_reaction_after=True
                await menu.start(ctx)
            except HTTPException:
                menu = MenuPages(source=PostListL(ctx, hasil_post),
                                clear_reactions_after=True,
                                timeout=60.0)# bisa ditambah clear_reaction_after=True
                await menu.start(ctx)
    
    async def konachan_passivePost(self,ctx, tagss:list, pagee:Optional[int]=0):
        hasil_post = kclient.post_list(tags=tagss, limit= 50, page= pagee)
        if hasil_post == []:
            await ctx.send(f"Post dengan query `{'^'.join(tagss)}::{pagee}` tidak ditemukan")
        if not hasil_post == []:
            await ctx.send(f"Ditemukan post dengan query `{'^'.join(tagss)}::{pagee}`")
            try:
                menu = MenuPages(source=PostListK(ctx, hasil_post),
                                clear_reactions_after=True,
                                timeout=60.0)# bisa ditambah clear_reaction_after=True
                await menu.start(ctx)
            except HTTPException:
                menu = MenuPages(source=PostListL(ctx, hasil_post),
                                clear_reactions_after=True,
                                timeout=60.0)# bisa ditambah clear_reaction_after=True
                await menu.start(ctx)

    @command(name="yanbooru", aliases=['yb'])
    async def yandere_postList(self, ctx, *, tagss):
        """Pencarian gambar/video dengan tag yang diberikan (tidak random) oleh yan.dere
        Dapat dicari kombinasi tag dengan pemisah ^
        Spasi otomatis dikonversi ke underscore (untuk kemudahan)
        Dapat dicari dengan dua argumen:
        tags : str dengan pemisah ^
        halaman : int dengan pemisah ::

        Contoh:
        ```yanbooru kagamihara nadeshiko^smile^looking at viewer::3```
        """
        pagee = 1
        if "::" in tagss:
            try:
                pagee = int(tagss.split("::")[-1])
                tagss = " ".join("_".join(tagss.split(" ")).split("::")[0].split("^"))
                tagss = tagss.lower()
                hasil_post = yclient.post_list(tags=tagss, limit= 50, page= pagee)
            except ValueError:
                await ctx.send("Halaman yang dimasukkan harus berupa bilangan bulat")
        else:
            tagss = " ".join("_".join(tagss.split(" ")).split("^"))
            tagss = tagss.lower()
            hasil_post = yclient.post_list(tags=tagss, limit= 50)
        if hasil_post == []:
            await ctx.send(f"Tidak ditemukan post dengan tag {tagss}")
            tagl = tagss.split(" ")
            hasil_passSearch = {}
            for tagog in tagl:
                hasil_passSearch[tagog] = await self.gelbooru_passiveSearch(ctx, tagog)
            tagsatu = True
            
            for key in hasil_passSearch.keys():
                exact_tag = False
                if not len(hasil_passSearch[key]) == 1:
                    for char in hasil_passSearch[key]:
                        if char.name == key:
                            exact_tag = True
                            hasil_passSearch[key] = [char.name]
                            break
                    if exact_tag is False:
                        tagsatu = False
                        break
            if tagsatu is True :
                lis_tag = []
                for ab in hasil_passSearch.values():
                    lis_tag.append(ab[0])
                
                await self.yandere_passivePost(ctx, tagss=lis_tag, pagee=pagee)
            else:
                for tagog in tagl:
                    await self.gelbooru_tagSearch(ctx, term=tagog)
        else:
            try:
                menu = MenuPages(source=PostListK(ctx, hasil_post),
                                clear_reactions_after=True,
                                timeout=60.0)# bisa ditambah clear_reaction_after=True
                await menu.start(ctx)
            except HTTPException:
                menu = MenuPages(source=PostListL(ctx, hasil_post),
                                clear_reactions_after=True,
                                timeout=60.0)# bisa ditambah clear_reaction_after=True
                await menu.start(ctx)
    async def yandere_passivePost(self,ctx, tagss:list, pagee:Optional[int]=0):
        hasil_post = yclient.post_list(tags=tagss, limit= 50, page= pagee)
        if hasil_post == []:
            await ctx.send(f"Post dengan query `{'^'.join(tagss)}::{pagee}` tidak ditemukan")
        if not hasil_post == []:
            await ctx.send(f"Ditemukan post dengan query `{'^'.join(tagss)}::{pagee}`")
            try:
                menu = MenuPages(source=PostListK(ctx, hasil_post),
                                clear_reactions_after=True,
                                timeout=60.0)# bisa ditambah clear_reaction_after=True
                await menu.start(ctx)
            except HTTPException:
                menu = MenuPages(source=PostListL(ctx, hasil_post),
                                clear_reactions_after=True,
                                timeout=60.0)# bisa ditambah clear_reaction_after=True
                await menu.start(ctx)
    @command(name= "lolibooru", aliases=['lb'])
    async def lolibooru_postList(self, ctx, *, tagss):
        """Pencarian gambar/video dengan tag yang diberikan (tidak random) oleh lolibooru
        Dapat dicari kombinasi tag dengan pemisah ^
        Spasi otomatis dikonversi ke underscore (untuk kemudahan)
        Dapat dicari dengan dua argumen:
        tags : str dengan pemisah ^
        halaman : int dengan pemisah ::

        Contoh:
        ```lolibooru kagamihara nadeshiko^smile^looking at viewer::3```
        """
        pagee = 1
        if "::" in tagss:
            try:
                pagee = int(tagss.split("::")[-1])
                tagss = " ".join("_".join(tagss.split(" ")).split("::")[0].split("^"))
                tagss = tagss.lower()
                hasil_post = lclient.post_list(tags=tagss, limit= 50, page= pagee)
            except ValueError:
                await ctx.send("Halaman yang dimasukkan harus berupa bilangan bulat")
        else:
            tagss = " ".join("_".join(tagss.split(" ")).split("^"))
            tagss = tagss.lower()
            hasil_post = lclient.post_list(tags=tagss, limit= 50)
        if hasil_post == []:
            await ctx.send(f"Tidak ditemukan post dengan tag {tagss}")
            tagl = tagss.split(" ")
            hasil_passSearch = {}
            for tagog in tagl:
                hasil_passSearch[tagog] = await self.gelbooru_passiveSearch(ctx, tagog)
            tagsatu = True
            
            for key in hasil_passSearch.keys():
                exact_tag = False
                if not len(hasil_passSearch[key]) == 1:
                    for char in hasil_passSearch[key]:
                        if char.name == key:
                            exact_tag = True
                            hasil_passSearch[key] = [char.name]
                            break
                    if exact_tag is False:
                        tagsatu = False
                        break
            if tagsatu is True :
                lis_tag = []
                for ab in hasil_passSearch.values():
                    lis_tag.append(ab[0])
                
                await self.lolibooru_passivePost(ctx, tagss=lis_tag, pagee=pagee)
            else:
                for tagog in tagl:
                    await self.gelbooru_tagSearch(ctx, term=tagog)
        else:
            try:
                menu = MenuPages(source=PostListK(ctx, hasil_post),
                                clear_reactions_after=True,
                                timeout=60.0)# bisa ditambah clear_reaction_after=True
                await menu.start(ctx)
            except HTTPException:
                menu = MenuPages(source=PostListL(ctx, hasil_post),
                                clear_reactions_after=True,
                                timeout=60.0)# bisa ditambah clear_reaction_after=True
                await menu.start(ctx)
    
    async def lolibooru_passivePost(self,ctx, tagss:list, pagee:Optional[int]=0):
        hasil_post = lclient.post_list(tags=tagss, limit= 50, page= pagee)
        if hasil_post == []:
            await ctx.send(f"Post dengan query `{'^'.join(tagss)}::{pagee}` tidak ditemukan")
        if not hasil_post == []:
            await ctx.send(f"Ditemukan post dengan query `{'^'.join(tagss)}::{pagee}`")
            try:
                menu = MenuPages(source=PostListK(ctx, hasil_post),
                                clear_reactions_after=True,
                                timeout=60.0)# bisa ditambah clear_reaction_after=True
                await menu.start(ctx)
            except HTTPException:
                menu = MenuPages(source=PostListL(ctx, hasil_post),
                                clear_reactions_after=True,
                                timeout=60.0)# bisa ditambah clear_reaction_after=True
                await menu.start(ctx)

    async def gelbooru_passivePost(self,ctx, tagss:list, exclude_tags: Optional[list]=[], pagee:Optional[int]=0):
        if exclude_tags == []:
            hasil_post = await gclient.search_posts(tags=tagss, limit= 50, page=pagee)
        if not exclude_tags == []:
            hasil_post = await gclient.search_posts(tags=tagss, exclude_tags=exclude_tags, limit= 50, page=pagee)
                
        if hasil_post == []:
            await ctx.send(f"Post dengan query `{'^'.join(tagss)}///{'^'.join(exclude_tags)}::{pagee}` tidak ditemukan")
        if not hasil_post == []:
            if exclude_tags == []:
                await ctx.send(f"Ditemukan post dengan query `{'^'.join(tagss)}::{pagee}`")
            else:
                await ctx.send(f"Ditemukan post dengan query `{'^'.join(tagss)}///{'^'.join(exclude_tags)}::{pagee}`")
            menu = MenuPages(source=PostListG(ctx, hasil_post),
                            clear_reactions_after=True,
                            timeout=60.0)# bisa ditambah clear_reaction_after=True
            await menu.start(ctx)
            
    @command(name = "gelbooru", aliases=['gb'])
    async def gelbooru_postList(self, ctx, *, tagss):
        """Pencarian gambar/video dengan tag yang diberikan (tidak random) oleh gelbooru
        Dapat dicari kombinasi tag dengan pemisah ^
        Spasi otomatis dikonversi ke underscore (untuk kemudahan)
        Dapat dicari dengan 3 argumen:
        tag : str
        exclude tag : dengan pemisah ///
        halaman : <int> dengan pemisah :: 
        Contoh:
        ```gelbooru nakano nino^large breasts///netorare^cum::2```
        """
        tagss = tagss.lower()
        pagee = 0
        if "///" in tagss:
            if "::" in tagss:
                quary = "_".join(tagss.split(" ")).split("///")[0].split("^")
                exclude = "_".join(tagss.split(" ")).split("///")[1].split("::")[0].split("^")
                try:
                    pagee = int("_".join(tagss.split(" ")).split("///")[1].split("::")[1])-1
                    hasil_post = await gclient.search_posts(tags= quary, exclude_tags= exclude, limit =50, page= pagee)
                    
                except ValueError:
                    await ctx.send("Halaman yang kakak masukkan harus berupa bilangan bulat")
            else:
                quary = "_".join(tagss.split(" ")).split("///")[0].split("^")
                exclude = "_".join(tagss.split(" ")).split("///")[1].split("^")
                hasil_post = await gclient.search_posts(tags= quary, exclude_tags= exclude, limit =50)
                
        else:
            if "::" in tagss:
                quary = "_".join(tagss.split(" ")).split("::")[0].split("^")
                try:
                    pagee = int("_".join(tagss.split(" ")).split("::")[1])-1
                    hasil_post = await gclient.search_posts(tags= quary, limit =50, page= pagee)
                    
                except ValueError:
                    await ctx.send("Halaman yang kakak masukkan harus berupa bilangan bulat")
            else:
                quary = "_".join(tagss.split(" ")).split("^")
                hasil_post = await gclient.search_posts(tags= quary, limit =50)
                
        if hasil_post == []:
            await ctx.send(f"Post dengan query {str(tagss)} tidak ditemukan")
            hasil_passSearch = {}
            for tagog in quary:
                hasil_passSearch[tagog] = await self.gelbooru_passiveSearch(ctx, tagog)
            passSearch_exclude = {}
            try:
                for tagog in exclude:
                    passSearch_exclude[tagog] = await self.gelbooru_passiveSearch(ctx, tagog)
            except Exception:
                pass
            tagsatu = True
            excludesatu = True
            
            for key in hasil_passSearch.keys():
                exact_tag = False
                if not len(hasil_passSearch[key]) == 1:
                    for char in hasil_passSearch[key]:
                        if char.name == key:
                            exact_tag = True
                            hasil_passSearch[key] = [char.name]
                            break
                    if exact_tag is False:
                        tagsatu = False
                        break
            if not passSearch_exclude == {}:
                for key in passSearch_exclude.keys():
                    exact_exclude = False
                    if not len(passSearch_exclude[key]) == 1:
                        for charaa in passSearch_exclude[key]:
                            if charaa.name == key:
                                exact_exclude = True
                                passSearch_exclude[key] = [charaa.name]
                                break
                        if exact_exclude is False:
                            excludesatu = False
                            break
            if tagsatu is True and excludesatu is True:
                lis_tag = []
                lis_ex = []
                for ab in hasil_passSearch.values():
                    lis_tag.append(ab[0])
                
                        
                if passSearch_exclude == {}:
                    await self.gelbooru_passivePost(ctx, tagss=lis_tag, pagee=pagee)
                else:
                    for bc in passSearch_exclude.values():
                        lis_ex.append(bc[0])
                    await self.gelbooru_passivePost(ctx, tagss= lis_tag, exclude_tags= lis_ex, pagee=pagee)
            else:
                for tagog in quary:
                    await self.gelbooru_tagSearch(ctx, term=tagog)
                try:
                    for tagog in exclude:
                        await self.gelbooru_tagSearch(ctx, term=tagog)
                except Exception:
                    pass
            
        if not hasil_post == []:
            menu = MenuPages(source=PostListG(ctx, hasil_post),
                            clear_reactions_after=True,
                            timeout=60.0)# bisa ditambah clear_reaction_after=True
            await menu.start(ctx)

    @slash_command(name="gelbooru", description="Mencari art di forum gelbooru")
    @option("tag", description="Tag yang ingin dicari (jika >1 disambungkan dengan ^)")
    @option("exclude", description="Tag yang tidak akan diikutkan di hasil (jika >1 disambungkan dengan ^)", default='none')
    @option("page", int, description="Halaman", min_value=1, default=1)
    async def gelbooru_slash(self, ctx: ApplicationContext, tag, exclude, page):
        if exclude == 'none':
            tagss = f"{tag}::{page}"
        else:
            tagss = f"{tag}///{exclude}::{page}"
        await self.gelbooru_postList(ctx, tagss=tagss)
    
    async def gelbooru_passiveSearch(self, ctx, term):
        term = term.lower()
        # charlist = []
        hasil_search = await gclient.tag_list(name_pattern= "%" + term + "%", limit= 30)
        try:
            if hasil_search == []:
                await ctx.send(f"Tag {term} tidak ditemukan")
                return hasil_search
            # else:
                # for i, char in enumerate(hasil_search):
                #     charlist.append(f"{i+1:3d}  {char}")
                # menu = MenuPages(source=IsiSearchTag(ctx, charlist, term),
                #                 clear_reactions_after=True,
                #                 timeout=60.0)# bisa ditambah clear_reaction_after=True
                # await menu.start(ctx)
            elif len(hasil_search) == 1:
                return [hasil_search[0].name]
            else:
                return hasil_search
        except TypeError:
            return [hasil_search.name]
            
    
    @command(name="tagsearch", aliases=["ts"])
    async def gelbooru_tagSearch(self, ctx, *, term):
        """Mencari tag pada situs danbooru dengan kata kunci eksak"""
        term = term.lower()
        charlist = []
        hasil_search = await gclient.tag_list(name_pattern= "%" + term + "%", limit= 10000)
        try:
            if hasil_search == []:
                await ctx.send(f"Tag {term} tidak ditemukan")
            else:
                for i, char in enumerate(hasil_search):
                    charlist.append(f"{i+1:3d}  {char}")
                menu = MenuPages(source=IsiSearchTag(ctx, charlist, term),
                                clear_reactions_after=True,
                                timeout=60.0)# bisa ditambah clear_reaction_after=True
                await menu.start(ctx)
        except TypeError:
            embed = Embed(
                title= f"Hasil Search {term}",
                description=f"```{hasil_search.name}```"
            )
            await ctx.send(embed=embed)

    @slash_command(name='ts', description="Tag Search di forum booru")
    @option("term", description="Term yang ingin dicari (autocomplete)")
    async def tagsearch_slash(self, ctx: ApplicationContext, term):
        await self.gelbooru_tagSearch(ctx, term=term)
            
    @command(name="sauce")
    async def sauceNao_link(self,ctx, link:Optional[str]="Takda"):
        """Mencari saos dari gambar yg dikirim

        Args:
            link (Optional[str], optional): Link gambar yang ingin dicari saosnya.

        Jika link tidak dikirim bersamaan dengan command, gambar juga dapat dikirim setelah command
        """
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
                try:
                    link = link.attachments[0].url
                except IndexError:
                    link = link.embeds[0].url
                await self.passive_sauce(ctx, link)
        else:
            await self.passive_sauce(ctx, link)

    @slash_command(name="sauce", description="Mencari sauce art di SauceNao")
    @option("link", description="URL gambar", default="Takda")
    async def sauce_slash(self, ctx: ApplicationContext, link):
        await self.sauceNao_link(ctx, link=link)

    @retry(wait=wait_fixed(1), stop=stop_after_attempt(5))
    async def passive_sauce(self, ctx, link):
        loop = self.bot.loop or asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: sauce.from_url(link))
        hasil_saos = result.results
        menu = MenuPages(source=IsiSauceNao(ctx, hasil_saos),
                            clear_reactions_after=True,
                            timeout=60.0)# bisa ditambah clear_reaction_after=True
        await menu.start(ctx)
        

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")



def setup(bot):
    bot.add_cog(Fun(bot))