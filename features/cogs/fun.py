from discord.ext.commands import Cog, command, BadArgument, cooldown, BucketType
from random import choice, randint
from discord import Member, Embed, Client
from discord.errors import HTTPException, Forbidden
from discord.ext.menus import MenuPages, ListPageSource
from typing import Optional
from aiohttp import request
from jikanpy import Jikan
from datetime import datetime
from pybooru import Danbooru, Moebooru
from difflib import get_close_matches

from ..db import db

dclient = Danbooru("danbooru")
sclient = Danbooru("safebooru")
kclient = Moebooru("konachan")
yclient = Moebooru("yandere")
lclient = Moebooru("lolibooru")

class IsiTagsList(ListPageSource):
    def __init__(self, ctx, data, animek):
        self.ctx = ctx
        self.animek = animek

        super().__init__(data, per_page=20)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*self.per_page) + 1
        len_data = len(self.entries)
        chara = "\n".join(cr[0] for cr in fields)
        embed = Embed(title=self.animek,
                      description = f"```{chara}```",
                      colour=self.ctx.author.colour)
        
        # for name, value in fields:
        #     embed.add_field(name=name,value=value,inline=False)

        embed.set_footer(text=f"{offset:,} - {min(len_data, offset + self.per_page - 1):,} dari {len_data:,} hasil.")


        return embed

    async def format_page(self, menu, entries):
        fields = []
        
        

        for entry in entries:
            fields.append((entry, " "))

        return await self.write_page(menu, fields)

class PostListD(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx

        super().__init__(data, per_page=1)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*1) + 1
        len_data = len(self.entries)
        post_detail = self.entries[menu.current_page]
        embed = Embed(title= post_detail["tag_string_character"],
                    description= post_detail["id"],
                    colour=self.ctx.author.colour)
        if not post_detail["pixiv_id"] is None:
            sauce =  "https://pixiv.net/artworks/" + str(post_detail["pixiv_id"])
        else:
            sauce = post_detail["source"]
            if sauce == "":
                sauce = "Unknown"
        try:
            artis = post_detail["tag_string_artist"]
        except KeyError:
            artis = "Unknown"
        fields = [
            ("Artist", artis),
            ("Source", sauce),
            ("Tags", " ".join(f'[{tag}]' for tag in post_detail["tag_string_general"].split(" ")[:25]))
        ]
        
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)
        img_format = ["jpg", "png", "gif", "jpeg"]
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
            if not sauce == "Unknown":
                for forma in img_format:
                    if forma in post_detail["source"][-5:]:
                        embed.set_image(url=post_detail["source"])
        embed.set_footer(text=f"{offset:,} of {len_data:,} hasil.")

        # for name, value in fields:
        #     embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        fields = []
        
        
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
            ("Tags", " ".join(f'[{tag}]' for tag in post_detail["tags"].split(" ")[:25]))
        ]
        
        for name, value in fields:
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
            ("Tags", " ".join(f'[{tag}]' for tag in post_detail["tags"].split(" ")[:25]))
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

class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot


    @command(name="luck")
    @cooldown(3, 60*60*24, BucketType.user)  #Parameternya(jumlah dipakai sebelum cd, waktu cd, type cd : member, user, guild, default)
    async def luck(self, ctx):
        luck = randint(1,100)
        if luck <= 30:
            await ctx.send('Haha ampas')
        elif luck <= 50:
            await ctx.send('Mayan lucknya, 50% berhasil. Sisa 50%nya lagi diisi dengan semangat aja!')
        elif luck <= 80:
            await ctx.send('Kalau dihitung dari pergerakan bintang dan snezhnaya keberuntungan kaka hari ini BAIK!! :thumbsup:')
        elif luck <= 99:
            await ctx.send('Enaknyaa~ aku juga pengen laksek... bagi dong ka lucknya!')
        elif luck == 100:
            await ctx.send("(0 o 0 ) Gila beuhh")
        db.execute("UPDATE exp SET Luck = ? WHERE UserID = ?", luck, ctx.author.id)
            
        

    @command(name="dice")
    async def roll_n_dice(self, ctx, die_string: str):
        dice, value = (int(msg) for msg in die_string.split("d"))
        rolls = [randint(1, value) for i in range(dice)]
        await ctx.send(" + ".join([str(r) for r in rolls]) + f" = {sum(rolls)}")
    
    
    @command(name="bilang")
    async def say(self, ctx, *, message):
        await ctx.message.delete()
        await ctx.send(f"{message} <:nandeshikyot:752500122415267850>")

    @command(name="slap")
    async def slap_member(self, ctx, member: Member, *, reason: Optional[str] = "ngeselin"):
        if member.id == self.bot.owner_ids[0]:
            await ctx.send("Gamau")
        else: 
            await ctx.send(f"Nandeshiko menampar {member.mention} karena {reason}")
        # print(member)
    @slap_member.error
    async def slap_member_error(self, ctx, exc):
        if isinstance(exc, BadArgument):
            await ctx.send("Siapa itu?")

    @command(name="danbooru")
    async def danbooru_postList(self, ctx, *, tagss):
        tagss = " ".join("_".join(tagss.split(" ")).split("+"))
        hasil_post = dclient.post_list(tags=tagss, random=True, limit= 50)
        if hasil_post == []:
            await ctx.send(f"Tidak ditemukan post dengan tag {tagss}")
            tagl = tagss.split(" ")
            tagli = []
            tag_lists = []
            for tag in tagl:
                tagli.append("".join("".join(tag.split("(")[-1]).split(")")))
            for tag in tagli:
                tag_lists.append(dclient.tag_related(query=tag))
            
            wikitag = []
            char_list = False
            for en, lis in enumerate(tag_lists):
                wiki_tag = []
                for key in lis["other_wikis"].keys():
                    if "list_of_" in key and "characters" in key:
                        for no in range(len(lis["other_wikis"][key])):
                            wiki_tag.append(lis["other_wikis"][key][no][0])
                        wikitag.append(wiki_tag)
                        char_list = True
                        break
                
                if not char_list is True:
                    for key in lis["wiki_page_tags"]:
                        wiki_tag.append(key[0])
                    wikitag.append(wiki_tag)
            if wikitag == []:
                    await ctx.send(f"Tidak ditemukan tag {tagss}")
            if not wiki_tag == []:
                for la, ntag in enumerate(tagl):
                    wtag = get_close_matches(ntag, wikitag[la], 20)
                    tagsss = []
                    for i, tag in enumerate(wtag):
                        tagsss.append(f"{i+1}.  {tag}")
                
                    if tagsss == []:
                        await ctx.send(f"Tidak ditemukan character dalam tag {''.join(''.join(ntag.split('(')[-1]).split(')'))}")
                    else:
                        desc = "\n".join(tagsss)
                        embed = Embed(title="Apakah maksud anda :",
                                    description= f"```{desc:.1024s}```",
                                    colour= ctx.author.colour)
                        await ctx.send(embed=embed)
        else:
            menu = MenuPages(source=PostListD(ctx, hasil_post),
                             clear_reactions_after=True,
                            timeout=60.0)# bisa ditambah clear_reaction_after=True
            await menu.start(ctx)
            
    @command(name= "safebooru")
    async def safebooru_postList(self, ctx, *, tagss):
        tagss = " ".join("_".join(tagss.split(" ")).split("+"))
        hasil_post = sclient.post_list(tags=tagss, random=True, limit= 50)
        if hasil_post == []:
            await ctx.send(f"Tidak ditemukan post dengan tag {tagss}")
            tagl = tagss.split(" ")
            tagli = []
            tag_lists = []
            for tag in tagl:
                tagli.append("".join("".join(tag.split("(")[-1]).split(")")))
            for tag in tagli:
                tag_lists.append(dclient.tag_related(query=tag))
            
            wikitag = []
            char_list = False
            for en, lis in enumerate(tag_lists):
                wiki_tag = []
                for key in lis["other_wikis"].keys():
                    if "list_of_" in key and "characters" in key:
                        for no in range(len(lis["other_wikis"][key])):
                            wiki_tag.append(lis["other_wikis"][key][no][0])
                        wikitag.append(wiki_tag)
                        char_list = True
                        break
                
                if not char_list is True:
                    for key in lis["wiki_page_tags"]:
                        wiki_tag.append(key[0])
                    wikitag.append(wiki_tag)
            if wikitag == []:
                    await ctx.send(f"Tidak ditemukan tag {tagss}")
            if not wiki_tag == []:
                for la, ntag in enumerate(tagl):
                    wtag = get_close_matches(ntag, wikitag[la], 20)
                    tagsss = []
                    for i, tag in enumerate(wtag):
                        tagsss.append(f"{i+1}.  {tag}")
                
                    if tagsss == []:
                        await ctx.send(f"Tidak ditemukan character dalam tag {''.join(''.join(ntag.split('(')[-1]).split(')'))}")
                    else:
                        desc = "\n".join(tagsss)
                        embed = Embed(title="Apakah maksud anda :",
                                    description= f"```{desc:.1024s}```",
                                    colour= ctx.author.colour)
                        await ctx.send(embed=embed)
        else:
            menu = MenuPages(source=PostListD(ctx, hasil_post),
                             clear_reactions_after=True,
                            timeout=60.0)# bisa ditambah clear_reaction_after=True
            await menu.start(ctx)
    @command(name= "danboorutaglist", aliases=["dtl"])
    async def danbooru_tagList(self, ctx, *, animek):
        animek = "_".join(animek.split(" "))
        tags_list = dclient.tag_related(query= animek)
        char_list = False
        for key in tags_list["other_wikis"].keys():
            if "list_of_" in key and "characters" in key:
                wiki_tag = tags_list["other_wikis"][key]
                char_list = True
        if not char_list is True:
            wiki_tag = tags_list["wiki_page_tags"]
        if wiki_tag == []:
            await ctx.send(f"Tidak ditemukan tag {animek}")
        if not wiki_tag == []:
            tagss = []
            for i, tag in enumerate(wiki_tag):
                tagss.append(f"{i+1}.  {tag[0]}")
            # desc = "\n".join(tagss)
            # embed = Embed(title=animek,
            #               description= f"{desc:.1024s}",
            #               colour= ctx.author.colour)
            # await ctx.send(embed=embed)
            menu = MenuPages(source=IsiTagsList(ctx, tagss, animek),
                             clear_reactions_after=True,
                            timeout=60.0)# bisa ditambah clear_reaction_after=True
            await menu.start(ctx)

    @command(name="konachan")
    async def konachan_postList(self, ctx, *, tagss):
        tagss = " ".join("_".join(tagss.split(" ")).split("+"))
        hasil_post = kclient.post_list(tags=tagss, limit= 50)
        if hasil_post == []:
            await ctx.send(f"Tidak ditemukan post dengan tag {tagss}")
        else:
            menu = MenuPages(source=PostListK(ctx, hasil_post),
                             clear_reactions_after=True,
                            timeout=60.0)# bisa ditambah clear_reaction_after=True
            await menu.start(ctx)
            
    @command(name="yanbooru")
    async def yandere_postList(self, ctx, *, tagss):
        tagss = " ".join("_".join(tagss.split(" ")).split("+"))
        hasil_post = yclient.post_list(tags=tagss, limit= 50)
        if hasil_post == []:
            await ctx.send(f"Tidak ditemukan post dengan tag {tagss}")
        else:
            menu = MenuPages(source=PostListK(ctx, hasil_post),
                             clear_reactions_after=True,
                            timeout=60.0)# bisa ditambah clear_reaction_after=True
            await menu.start(ctx)
            
    @command(name= "lolibooru")
    async def lolibooru_postList(self, ctx, *, tagss):
        tagss = " ".join("_".join(tagss.split(" ")).split("+"))
        hasil_post = lclient.post_list(tags=tagss, limit= 50)
        if hasil_post == []:
            await ctx.send(f"Tidak ditemukan post dengan tag {tagss}")
        else:
            menu = MenuPages(source=PostListL(ctx, hasil_post),
                             clear_reactions_after=True,
                            timeout=60.0)# bisa ditambah clear_reaction_after=True
            await menu.start(ctx)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")



def setup(bot):
    bot.add_cog(Fun(bot))