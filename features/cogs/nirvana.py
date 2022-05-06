from hentai import Hentai, Utils, Sort
import asyncio

from discord.ext.menus import MenuPages, ListPageSource
from discord.ext.commands import Cog, CheckFailure, command, is_nsfw
from discord import Embed

class IsiNHenHome(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx

        super().__init__(data, per_page=1)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*1) + 1
        len_data = len(self.entries)

        embed = Embed(title=self.entries[menu.current_page]["name"],
                      description= self.entries[menu.current_page]["id"],
                      colour=self.ctx.author.colour)
        
        fields = [
            ("Bahasa", self.entries[menu.current_page]['language']),
            ("Jumlah Halaman", self.entries[menu.current_page]["pages"]),
            ("Jumlah Favorit", self.entries[menu.current_page]["favorites"]),
            ("Artists", ', '.join(str(artis) for artis in self.entries[menu.current_page]["artists"])),
            ("Tags", ', '.join(str(tag) for tag in self.entries[menu.current_page]['tags']))
        ]
        
        for name, value in fields:
            embed.add_field(name=name,value=value,inline=False)

        embed.set_image(url=self.entries[menu.current_page]["image_url"])
        embed.set_footer(text=f"{offset:,} of {len_data:,} hasil.")

        # for name, value in fields:
        #     embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        fields = []
        
        

        
        # fields.append((entries["title"], f"Score = {entries['score']:,.2f}\nTipe = {entries['type']}\nEpisodes = {entries['episodes']:,}\nSinopsis =\n{entries['synopsis']}"))

        return await self.write_page(menu, fields)
    
class IsiSurga(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx

        super().__init__(data, per_page=1)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*1) + 1
        len_data = len(self.entries)

        embed = Embed(colour=self.ctx.author.colour)
        
        
        

        embed.set_image(url=self.entries[menu.current_page])
        embed.set_footer(text=f"{offset:,} of {len_data:,} hasil.")

        # for name, value in fields:
        #     embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        fields = []
        
        

        
        # fields.append((entries["title"], f"Score = {entries['score']:,.2f}\nTipe = {entries['type']}\nEpisodes = {entries['episodes']:,}\nSinopsis =\n{entries['synopsis']}"))

        return await self.write_page(menu, fields)

class Nirvana(Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @command(name="berandasurga", aliases=["bs"])
    @is_nsfw()
    async def Nhen_Home(self, ctx):
        """Mengintip pintu surga"""
        kamus_hen = {}
        loop = self.bot.loop or asyncio.get_event_loop()
        homepage = await loop.run_in_executor(None, lambda: Utils.get_homepage())
        home = [dojon for dojon in list(homepage.popular_now)] + [doujan for doujan in list(homepage.new_uploads)]
        for i in range(len(home)):
            dojin = home[i]
            dojin_id = dojin.id
            dojin_lang = dojin.language[0].name
            dojin_cover = dojin.cover
            dojin_title = dojin.json['title']['pretty']
            dojin_pages = dojin.json['num_pages']
            dojin_fav = dojin.json['num_favorites']
            dojin_artists = []
            for artis in dojin.artists:
                dojin_artists.append(artis.name)
            dojin_tags = []
            for tag in dojin.tag:
                dojin_tags.append(tag.name) #list
            kamus_hen[i] = {
                "name" : dojin_title,
                "id" : dojin_id,
                "language" : dojin_lang,
                "tags" : dojin_tags,
                "pages" : dojin_pages,
                "image_url" : dojin_cover,
                "favorites" : dojin_fav,
                "artists" : dojin_artists
            }
        menu = MenuPages(source=IsiNHenHome(ctx, kamus_hen),
                        # delete_message_after=True,
                        timeout=60.0)# bisa ditambah clear_reaction_after=True
        await menu.start(ctx)
        
    @command(name="mencarisurgap", aliases=["msp"])
    @is_nsfw()
    async def Nhen_searchP(self, ctx, *, kata_kunci):
        """Mencari surga yang paling atas"""
        kamus_hen = {}
        loop = self.bot.loop or asyncio.get_event_loop()
        results = []
        for n in range(1,3):
            results.append(await loop.run_in_executor(None, lambda: Utils.search_by_query(query= kata_kunci, page= n, sort= Sort.Popular)))
        
        for i in range(len(results.doujins)):
            dojin = results[i]
            dojin_id = dojin.id
            dojin_lang = dojin.language[0].name
            dojin_cover = dojin.cover
            dojin_title = dojin.json['title']['pretty']
            dojin_pages = dojin.json['num_pages']
            dojin_fav = dojin.json['num_favorites']
            dojin_artists = []
            for artis in dojin.artists:
                dojin_artists.append(artis.name)
            dojin_tags = []
            for tag in dojin.tag:
                dojin_tags.append(tag.name) #list
            kamus_hen[i] = {
                "name" : dojin_title,
                "id" : dojin_id,
                "language" : dojin_lang,
                "tags" : dojin_tags,
                "pages" : dojin_pages,
                "image_url" : dojin_cover,
                "favorites" : dojin_fav,
                "artists" : dojin_artists
            }
        menu = MenuPages(source=IsiNHenHome(ctx, kamus_hen),
                        # delete_message_after=True,
                        timeout=60.0)# bisa ditambah clear_reaction_after=True
        await menu.start(ctx)
        
    @command(name="mencarisurgam", aliases=["msm"])
    @is_nsfw()
    async def Nhen_searchPM(self, ctx, *, kata_kunci):
        """Mencari surga yang ramai bulan ini"""
        kamus_hen = {}
        loop = self.bot.loop or asyncio.get_event_loop()
        results = []
        for n in range(1,3):
            results.append(await loop.run_in_executor(None, lambda: Utils.search_by_query(query= kata_kunci, page= n, sort= Sort.PopularMonth)))
        
        for i in range(len(results.doujins)):
            dojin = results[i]
            dojin_id = dojin.id
            dojin_lang = dojin.language[0].name
            dojin_cover = dojin.cover
            dojin_title = dojin.json['title']['pretty']
            dojin_pages = dojin.json['num_pages']
            dojin_fav = dojin.json['num_favorites']
            dojin_artists = []
            for artis in dojin.artists:
                dojin_artists.append(artis.name)
            dojin_tags = []
            for tag in dojin.tag:
                dojin_tags.append(tag.name) #list
            kamus_hen[i] = {
                "name" : dojin_title,
                "id" : dojin_id,
                "language" : dojin_lang,
                "tags" : dojin_tags,
                "pages" : dojin_pages,
                "image_url" : dojin_cover,
                "favorites" : dojin_fav,
                "artists" : dojin_artists
            }
        menu = MenuPages(source=IsiNHenHome(ctx, kamus_hen),
                        # delete_message_after=True,
                        timeout=60.0)# bisa ditambah clear_reaction_after=True
        await menu.start(ctx)
        
    @command(name="mencarisurgaw", aliases=["msw"])
    @is_nsfw()
    async def Nhen_searchPW(self, ctx, *, kata_kunci):
        """Mencari surga yang ramai minggu ini"""
        kamus_hen = {}
        loop = self.bot.loop or asyncio.get_event_loop()
        results = []
        for n in range(1,3):
            results.append(await loop.run_in_executor(None, lambda: Utils.search_by_query(query= kata_kunci, page= n, sort= Sort.PopularWeek)))
        
        for i in range(len(results.doujins)):
            dojin = results[i]
            dojin_id = dojin.id
            dojin_lang = dojin.language[0].name
            dojin_cover = dojin.cover
            dojin_title = dojin.json['title']['pretty']
            dojin_pages = dojin.json['num_pages']
            dojin_fav = dojin.json['num_favorites']
            dojin_artists = []
            for artis in dojin.artists:
                dojin_artists.append(artis.name)
            dojin_tags = []
            for tag in dojin.tag:
                dojin_tags.append(tag.name) #list
            kamus_hen[i] = {
                "name" : dojin_title,
                "id" : dojin_id,
                "language" : dojin_lang,
                "tags" : dojin_tags,
                "pages" : dojin_pages,
                "image_url" : dojin_cover,
                "favorites" : dojin_fav,
                "artists" : dojin_artists
            }
        menu = MenuPages(source=IsiNHenHome(ctx, kamus_hen),
                        # delete_message_after=True,
                        timeout=60.0)# bisa ditambah clear_reaction_after=True
        await menu.start(ctx)
        
    @command(name="mencarisurgat", aliases=["mst"])
    @is_nsfw()
    async def Nhen_searchPT(self, ctx, *, kata_kunci):
        """Mencari surga yang ramai hari ini"""
        kamus_hen = {}
        loop = self.bot.loop or asyncio.get_event_loop()
        results = []
        for n in range(1,3):
            results.append(await loop.run_in_executor(None, lambda: Utils.search_by_query(query= kata_kunci, page= n, sort= Sort.PopularToday)))
        
        for i in range(len(results.doujins)):
            dojin = results[i]
            dojin_id = dojin.id
            dojin_lang = dojin.language[0].name
            dojin_cover = dojin.cover
            dojin_title = dojin.json['title']['pretty']
            dojin_pages = dojin.json['num_pages']
            dojin_fav = dojin.json['num_favorites']
            dojin_artists = []
            for artis in dojin.artists:
                dojin_artists.append(artis.name)
            dojin_tags = []
            for tag in dojin.tag:
                dojin_tags.append(tag.name) #list
            kamus_hen[i] = {
                "name" : dojin_title,
                "id" : dojin_id,
                "language" : dojin_lang,
                "tags" : dojin_tags,
                "pages" : dojin_pages,
                "image_url" : dojin_cover,
                "favorites" : dojin_fav,
                "artists" : dojin_artists
            }
        menu = MenuPages(source=IsiNHenHome(ctx, kamus_hen),
                        # delete_message_after=True,
                        timeout=60.0)# bisa ditambah clear_reaction_after=True
        await menu.start(ctx)
        
    @command(name="mencarisurga", aliases=["msl"])
    @is_nsfw()
    async def Nhen_searchPL(self, ctx, *, kata_kunci):
        """Mencari surga yang baru saja dibentuk"""
        kamus_hen = {}
        loop = self.bot.loop or asyncio.get_event_loop()
        results = []
        for n in range(1,3):
            results.append(await loop.run_in_executor(None, lambda: Utils.search_by_query(query= kata_kunci, page= n, sort= Sort.Date)))
        
        for i in range(len(results.doujins)):
            dojin = results[i]
            dojin_id = dojin.id
            dojin_lang = dojin.language[0].name
            dojin_cover = dojin.cover
            dojin_title = dojin.json['title']['pretty']
            dojin_pages = dojin.json['num_pages']
            dojin_fav = dojin.json['num_favorites']
            dojin_artists = []
            for artis in dojin.artists:
                dojin_artists.append(artis.name)
            dojin_tags = []
            for tag in dojin.tag:
                dojin_tags.append(tag.name) #list
            kamus_hen[i] = {
                "name" : dojin_title,
                "id" : dojin_id,
                "language" : dojin_lang,
                "tags" : dojin_tags,
                "pages" : dojin_pages,
                "image_url" : dojin_cover,
                "favorites" : dojin_fav,
                "artists" : dojin_artists
            }
        menu = MenuPages(source=IsiNHenHome(ctx, kamus_hen),
                        # delete_message_after=True,
                        timeout=60.0)# bisa ditambah clear_reaction_after=True
        await menu.start(ctx)
        
    @command(name="infosurga", aliases=["is"])
    @is_nsfw()
    async def Doujin_Info(self, ctx, *, doujin_id):
        """Melihat ingfo surga dengan kode tertentu"""
        loop = self.bot.loop or asyncio.get_event_loop()
        dojin = await loop.run_in_executor(None, lambda: Hentai(int(doujin_id)))
        if not Hentai.exists(dojin.id):
            return await ctx.send("Maaf kak surga yang kakak cari tidak ada..")
        dojin_id = dojin.id
        dojin_langs = []
        for lang in dojin.language:
            dojin_langs.append(lang.name)
        dojin_img = dojin.cover
        dojin_title = dojin.json['title']['pretty']
        dojin_pages = dojin.json['num_pages']
        dojin_fav = dojin.json['num_favorites']
        dojin_artists = []
        for artis in dojin.artists:
            dojin_artists.append(artis.name)
        dojin_tags = []
        for tag in dojin.tag:
            dojin_tags.append(tag.name) #list
        dojin_ctg = []
        for ctg in dojin.category:
            dojin_ctg.append(ctg.name)
        dojin_charas = []
        for chara in dojin.character:
            dojin_charas.append(chara.name)
        dojin_pard = []
        for pard in dojin.parody:
            dojin_pard.append(pard.name)
        dojin_grups = []
        for grup in dojin.group:
            dojin_grups.append(grup.name)
        
        embed = Embed(
            title= dojin_title,
            description= "Favorite : " + dojin_fav + "\nTotal Halaman : " + dojin_pages,
            colour= ctx.author.colour
        )
        fields = [
            ("Artists", ', '.join(artist for artist in dojin_artists), True),
            ("Groups", ', '.join(grup for grup in dojin_grups), True),
            ("Parodies", '\n'.join(parodi for parodi in dojin_pard), True),
            ("Characters", ', '.join(karakter for karakter in dojin_charas), True),
            ("Categories", ', '.join(kategori for kategori in dojin_ctg),True),
            ("Languages", '\n'.join(lang for lang in dojin_langs), True),
            ("Tags", ', '.join(tag for tag in dojin_tags), False)
            
        ]
        for name, value, inline in fields:
            if value == '':
                value = 'Tak ada'
            embed.add_field(name=name, value=value, inline=inline)
            
        embed.set_image(url=dojin_img)
        embed.set_footer(text=dojin_id, icon_url=ctx.author.avatar.url)
        
        await ctx.send(embed=embed)
        
    @command(name="infosurgarandom", aliases=["isr"])
    @is_nsfw()
    async def Doujin_Info_Random(self, ctx):
        """Melihat ingfo surga yang belum dijelajahi sebelumnya"""
        loop = self.bot.loop or asyncio.get_event_loop()
        dojin = await loop.run_in_executor(None, lambda: Utils.get_random_hentai())
        dojin_id = dojin.id
        dojin_langs = []
        for lang in dojin.language:
            dojin_langs.append(lang.name)
        dojin_img = dojin.cover
        dojin_title = dojin.json['title']['pretty']
        dojin_pages = dojin.json['num_pages']
        dojin_fav = dojin.json['num_favorites']
        dojin_artists = []
        for artis in dojin.artists:
            dojin_artists.append(artis.name)
        dojin_tags = []
        for tag in dojin.tag:
            dojin_tags.append(tag.name) #list
        dojin_ctg = []
        for ctg in dojin.category:
            dojin_ctg.append(ctg.name)
        dojin_charas = []
        for chara in dojin.character:
            dojin_charas.append(chara.name)
        dojin_pard = []
        for pard in dojin.parody:
            dojin_pard.append(pard.name)
        dojin_grups = []
        for grup in dojin.group:
            dojin_grups.append(grup.name)
        
        embed = Embed(
            title= dojin_title,
            description= "Favorite : " + dojin_fav + "\nTotal Halaman : " + dojin_pages,
            colour= ctx.author.colour
        )
        fields = [
            ("Artists", ', '.join(artist for artist in dojin_artists), True),
            ("Groups", ', '.join(grup for grup in dojin_grups), True),
            ("Parodies", '\n'.join(parodi for parodi in dojin_pard), True),
            ("Characters", ', '.join(karakter for karakter in dojin_charas), True),
            ("Categories", ', '.join(kategori for kategori in dojin_ctg),True),
            ("Languages", '\n'.join(lang for lang in dojin_langs), True),
            ("Tags", ', '.join(tag for tag in dojin_tags), False)
            
        ]
        for name, value, inline in fields:
            if value == '':
                value = 'Tak ada'
            embed.add_field(name=name, value=value, inline=inline)
            
        embed.set_image(url=dojin_img)
        embed.set_footer(text=dojin_id, icon_url=ctx.author.avatar.url)
        
        await ctx.send(embed=embed)
        
    @command(name="bacakitab", aliases=["bk"])
    @is_nsfw()
    async def Baca_Doujin(self, ctx, *, rahasia_dunia):
        """Mengintip Pintu Surga Menuju Kenikmatan Tak Terbatas (ada passwordnya)"""
        loop = self.bot.loop or asyncio.get_event_loop()
        dojin = await loop.run_in_executor(None, lambda: Hentai(int(rahasia_dunia)))
        dojin_imgs = []
        for img in dojin.pages:
            dojin_imgs.append(img.url)
        menu = MenuPages(source=IsiSurga(ctx, dojin_imgs),
                        # delete_message_after=True,
                        timeout=120.0)# bisa ditambah clear_reaction_after=True
        await menu.start(ctx)
        
    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("nirvana")
            
def setup(bot):
    bot.add_cog(Nirvana(bot))