from discord.ext.commands import Cog, command
from discord.ext.menus import MenuPages, ListPageSource
from discord.utils import get
from discord import Embed
from asyncio import TimeoutError
from jikanpy import Jikan
from jikanpy.exceptions import APIException
from typing import Optional
from datetime import datetime as date


jikan = Jikan()

# def syntax(command):
#     cmd_and_alias = " | ".join([str(command), *command.aliases])
#     params = []

#     for key, value in command.params.items():
#         if key not in ("self", "ctx"):
#             params.append(f"{key}" if "NoneType" in str(value) else f"<{key}>")

#     params = " ".join(params)

#     return f"```{cmd_and_alias} {params}```"
# OPTIONS = {
#     "1️⃣": 0,
#     "2⃣": 1,
#     "3⃣": 2,
#     "4⃣": 3,
#     "5⃣": 4,
# }

# MOVER = {
#     "◀️": -1,
#     "▶️": 1
# }

HEART = {
    "❤️": 0
}

class IsiPersonSearch(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx

        super().__init__(data, per_page=1)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*1) + 1
        len_data = len(self.entries)

        embed = Embed(title=self.entries[menu.current_page]["name"],
                      description=f"Aliases : {', '.join(str(alias) for alias in self.entries[menu.current_page]['alternative_names'])}\nId : {str(self.entries[menu.current_page]['mal_id'])}",
                      colour=self.ctx.author.colour)

        embed.set_image(url=self.entries[menu.current_page]["image_url"])
        embed.set_footer(text=f"{offset:,} of {len_data:,} hasil.")

        # for name, value in fields:
        #     embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        fields = []
        
        

        
        # fields.append((entries["title"], f"Score = {entries['score']:,.2f}\nTipe = {entries['type']}\nEpisodes = {entries['episodes']:,}\nSinopsis =\n{entries['synopsis']}"))

        return await self.write_page(menu, fields)

class IsiMangaSearch(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx

        super().__init__(data, per_page=1)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*1) + 1
        len_data = len(self.entries)

        embed = Embed(title=self.entries[menu.current_page]["title"],
                      description=f"Score : {str(self.entries[menu.current_page]['score'])}\n\
Volume : {str(self.entries[menu.current_page]['volumes'])} \n\
Chapters : {str(self.entries[menu.current_page]['chapters'])} \n\
Publishing : {str(self.entries[menu.current_page]['publishing'])} \n\
Members : {str(self.entries[menu.current_page]['members'])} \n\
Id : {str(self.entries[menu.current_page]['mal_id'])} \n",
                      colour=self.ctx.author.colour)
        
        fields = [
            ("Sinopsis", f"{str(self.entries[menu.current_page]['synopsis']):.1021s}..." )
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

class IsiCharaSearch(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx

        super().__init__(data, per_page=1)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*1) + 1
        len_data = len(self.entries)

        embed = Embed(title=self.entries[menu.current_page]["name"],
                      description=f"Aliases : {', '.join(str(alias) for alias in self.entries[menu.current_page]['alternative_names'])}\n\
Id : {str(self.entries[menu.current_page]['mal_id'])} ",
                      colour=self.ctx.author.colour)
        dr_anim = ', '.join(str(anime['name']) for anime in self.entries[menu.current_page]['anime'])
        if dr_anim == '':
            dr_anim = 'None'
        dr_mango = ', '.join(str(manga['name']) for manga in self.entries[menu.current_page]['manga'])
        if dr_mango == '':
            dr_mango = 'None'
        
        fields = [
            ("Dari Anime", dr_anim ),
            ("Dari Manga", dr_mango )
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
        
        # chara_id = str(self.entries[menu.current_page]['mal_id'])

        
        # fields.append((entries["title"], f"Score = {entries['score']:,.2f}\nTipe = {entries['type']}\nEpisodes = {entries['episodes']:,}\nSinopsis =\n{entries['synopsis']}"))

        return await self.write_page(menu, fields)

class IsiJadwalAnime(ListPageSource):
    def __init__(self, day, ctx, data):
        self.ctx = ctx
        self.day = day

        super().__init__(data, per_page=1)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*1) + 1
        len_data = len(self.entries)

        embed = Embed(title=f"{self.day}\n{self.entries[menu.current_page]['title']}",
                      description=f"Score : {str(self.entries[menu.current_page]['score'])}\n\
Tipe : {str(self.entries[menu.current_page]['type'])}\n\
Source : {str(self.entries[menu.current_page]['source'])}\n\
Episodes : {str(self.entries[menu.current_page]['episodes'])}\n\
Id : {str(self.entries[menu.current_page]['mal_id'])}\n",
                      colour=self.ctx.author.colour)
        try:
            produsa = '\n'.join(str(self.entries[menu.current_page]['producers'][i]['name']) for i in range(len(self.entries[menu.current_page]['producers'])))
        except IndexError:
            produsa = 'None'
        lisensa = '\n'.join(str(i) for i in self.entries[menu.current_page]['licensors'])
        if lisensa == '':
            lisensa = 'None'
        
        fields = [
            ("Producers", produsa ),
            ("Licensors", lisensa ),
            ("Genre", ', '.join(str(genre['name']) for genre in self.entries[menu.current_page]['genres']) ),
            ("Sinopsis", f"{str(self.entries[menu.current_page]['synopsis']):.1021s}...")
        ]
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)
        embed.set_image(url=self.entries[menu.current_page]["image_url"])
        embed.set_footer(text=f"{offset:,} of {len_data:,} hasil.")

        # for name, value in fields:
        #     embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        fields = []
        
        

        
        # fields.append((entries["title"], f"Score = {entries['score']:,.2f}\nTipe = {entries['type']}\nEpisodes = {entries['episodes']:,}\nSinopsis =\n{entries['synopsis']}"))

        return await self.write_page(menu, fields)

class IsiSeasonSearch(ListPageSource):
    def __init__(self, season, year, ctx, data):
        self.ctx = ctx
        self.year = year
        self.season = season

        super().__init__(data, per_page=1)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*1) + 1
        len_data = len(self.entries)

        embed = Embed(title=f"{self.season} {self.year}\n{self.entries[menu.current_page]['title']}",
                      description=f"Score : {str(self.entries[menu.current_page]['score'])}\n\
Tipe : {str(self.entries[menu.current_page]['type'])}\n\
Source : {str(self.entries[menu.current_page]['source'])}\n\
Episodes : {str(self.entries[menu.current_page]['episodes'])}\n\
Id : {str(self.entries[menu.current_page]['mal_id'])}\n",
                      colour=self.ctx.author.colour)
        try:
            produsa = '\n'.join(str(self.entries[menu.current_page]['producers'][i]['name']) for i in range(len(self.entries[menu.current_page]['producers'])))
        except IndexError:
            produsa = 'None'
        lisensa = '\n'.join(str(i) for i in self.entries[menu.current_page]['licensors'])
        if lisensa == '':
            lisensa = 'None'
        
        fields = [
            ("Producers", produsa ),
            ("Licensors", lisensa ),
            ("Genre", ', '.join(str(genre['name']) for genre in self.entries[menu.current_page]['genres']) ),
            ("Sinopsis", f"{str(self.entries[menu.current_page]['synopsis']):.1021s}...")
        ]
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)
        # fields=[]
        # for genre in self.entries[menu.current_page]["genres"]:
        #     fields.append(genre["name"])
            
    
        # embed.add_field(name="Genre : ", value= ",".join(value for value in fields), inline=True)

        embed.set_image(url=self.entries[menu.current_page]["image_url"])
        embed.set_footer(text=f"{offset:,} of {len_data:,} hasil.")

        # for name, value in fields:
        #     embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        fields = []
        
        

        
        # fields.append((entries["title"], f"Score = {entries['score']:,.2f}\nTipe = {entries['type']}\nEpisodes = {entries['episodes']:,}\nSinopsis =\n{entries['synopsis']}"))

        return await self.write_page(menu, fields)

class IsiAnimeSearch(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx

        super().__init__(data, per_page=1)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*1) + 1
        len_data = len(self.entries)

        embed = Embed(title=self.entries[menu.current_page]["title"],
                      description=f"Score : {self.entries[menu.current_page]['score']:,.2f}\nTipe : {self.entries[menu.current_page]['type']}\nEpisodes : {self.entries[menu.current_page]['episodes']:,}\nId : {str(self.entries[menu.current_page]['mal_id'])}\nSinopsis :\n      {self.entries[menu.current_page]['synopsis']}",
                      colour=self.ctx.author.colour)

        embed.set_image(url=self.entries[menu.current_page]["image_url"])
        embed.set_footer(text=f"{offset:,} of {len_data:,} hasil.")
        
       

        # for name, value in fields:
        #     embed.add_field(name=name, value=value, inline=False)
        return embed

    async def format_page(self, menu, entries):
        fields = []
        
        

        
        # fields.append((entries["title"], f"Score = {entries['score']:,.2f}\nTipe = {entries['type']}\nEpisodes = {entries['episodes']:,}\nSinopsis =\n{entries['synopsis']}"))

        return await self.write_page(menu, fields)

class AnimeRelated(Cog):
    def __init__(self, bot):
        self.bot = bot


    @command(name="animesearch", aliases=["as"])
    async def anime_search(self, ctx, *, nama_anime):
        """Mencari Anime berdasar judul

        Args:
            ctx (str): command
            nama_anime (str): judul
        """
        nama_anime = str(nama_anime)
        try:
            result = jikan.search('anime', f'{nama_anime}', page=1)
            list_anime = result["results"]
            menu = MenuPages(source=IsiAnimeSearch(ctx, list_anime),
                            delete_message_after=False,
                            timeout=60.0)# bisa ditambah clear_reaction_after=True
            await menu.start(ctx)
        except APIException:
            await ctx.send(f"Tidak ditemukan anime dengan nama {nama_anime}\nMaaf >n<")

    # @command(name="animesearch", aliases=["as"])
    # async def ani_search(self, ctx, *, nama_anime: str):
    #     def _check(r, u):
    #         return (
    #             r.emoji in OPTIONS.keys()
    #             and u == ctx.author
    #             and r.message.id == msg.id
    #         )
            
            
    #     from json import dump
    #     from jikanpy import Jikan
    #     jikan = Jikan()
    #     result = jikan.search('anime', f'{nama_anime}', page=1)
    #     list_anime = result["results"]
    #     with open("./data/Jikan/Hasil_Carian.json", "w") as f:
    #         dump(list_anime, f, indent=4)
    #     embed = Embed(title=f"Hasil search: {nama_anime}",
    #                   description= (
    #             "\n".join(
    #                 f"**{i+1}.** {t['title']}"
    #                 for i, t in enumerate(list_anime[:5])
    #             )
    #         ),
    #                   colour= ctx.author.colour)
        
    #     embed.set_thumbnail(url=list_anime[0]["image_url"])
        
    #     msg = await ctx.send(embed=embed)
    #     for emoji in list(OPTIONS.keys())[:min(len(list_anime), len(OPTIONS))]:
    #         await msg.add_reaction(emoji)
        
    #     try:
    #         reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=_check)
    #     except TimeoutError:
    #         await msg.delete()
    #     else:
    #         anime_terpilih = list_anime[OPTIONS[reaction.emoji]]
    #         nilai = OPTIONS[reaction.emoji]
    #         with open("./data/Jikan/order.txt", "w") as f:
    #             f.write(str(nilai))
    #         embed = Embed(title= anime_terpilih["title"],
    #                   description=f"Score : {anime_terpilih['score']:,.2f}\nTipe : {anime_terpilih['type']}\nEpisodes : {anime_terpilih['episodes']:,}\nSinopsis :\n      {anime_terpilih['synopsis']}",
    #                   colour=ctx.author.colour)

    #         embed.set_image(url=anime_terpilih["image_url"])
    #         msg = await ctx.send(embed=embed)
    #         for emoji in list(MOVER.keys()):
    #             await msg.add_reaction(emoji)
                
    #         self.as_id = msg.id
    
    @command(name="season", aliases=["s"])
    async def season_search(self, ctx, *, musim_tahun: Optional[str]=None):
        """Harus berupa musim *spasi* tahun\nKategori musim : spring, summer, fall, winter.\nContoh: +s fall 2020"""
        musim_tahun = str(musim_tahun).split(" ")
        musim = musim_tahun[0].lower()
        if musim == "gugur":
            musim = "fall"
        elif musim == "semi":
            musim = "spring"
        elif musim == "dingin" or musim == "salju":
            musim = "winter"
        elif musim == "panas":
            musim = "summer"
        try:
            tahun = musim_tahun[1]
            result = jikan.season(year= tahun, season= musim)
        except IndexError:
            result = jikan.season(season= musim)
        year = result["season_year"]
        season = result["season_name"]
        list_anime = result["anime"]
        menu = MenuPages(source=IsiSeasonSearch(season, year, ctx, list_anime),
                         delete_message_after=False,
                         timeout=60.0)# bisa ditambah clear_reaction_after=True
        await menu.start(ctx)
        
    @command(name="jadwalanime", aliases=["ja"])
    async def jadwal_anime(self, ctx, *, hari:Optional[str]= date.today().strftime("%A")):
        """Mencari anime yang tayang pada hari yang dilampirkan (default= hari ini)"""
        hari_ = hari.lower()
        if hari_ == "senin":
            hari_ = "monday"
        elif hari_ == "selasa":
            hari_ = "tuesday"
        elif hari_ == "rabu":
            hari_ = "wednesday"
        elif hari_ == "kamis":
            hari_ = "thursday"
        elif hari_ == "jumat" or hari_ == "jum'at" or hari_ == "jum at":
            hari_ = "friday"
        elif hari_ == "sabtu":
            hari_ = "saturday"
        elif hari_ == "minggu" or hari_ == "ahad":
            hari_ = "sunday"
        
        try:
            result = jikan.schedule(day= hari_)
            list_anime = result[f"{hari_}"]
            menu = MenuPages(source=IsiJadwalAnime(hari, ctx, list_anime),
                            delete_message_after=False,
                            timeout=60.0)# bisa ditambah clear_reaction_after=True
            await menu.start(ctx)
        except APIException:
            await ctx.send(f"{hari} bukan merupakan nama hari!")
        
    @command(name="charasearch", aliases=["cs"])
    async def chara_search(self, ctx, *, chara):
        """Mencari character dengan kata kunci"""
    
        chara = str(chara)
        try:
            result = jikan.search("character", f"{chara}", page=1)
            list_chara = result["results"]
            menu = MenuPages(source=IsiCharaSearch(ctx, list_chara),
                            delete_message_after=False,
                            timeout=60.0 )# bisa ditambah clear_reaction_after=True
            
            await menu.start(ctx)
            
        except APIException:
            await ctx.send("Siapa itu?")
            
    @command(name="personsearch", aliases=["ps"])
    async def seiyuu_search(self, ctx, *, person_name):
        """Mencari orang (seiyuu dkk) dengan kata kunci"""
        person_name = str(person_name)
        try:
            result = jikan.search("person", person_name, page=1)
            list_person = result["results"]
            if list_person == []:
                await ctx.send("Maaf kak orang dengan nama itu tidak ditemukan\nPerintah ini memang agak rusak.")
            else:
                menu = MenuPages(source=IsiPersonSearch(ctx, list_person),
                                delete_message_after=False,
                                timeout=60.0 )# bisa ditambah clear_reaction_after=True
                
                await menu.start(ctx)
            
        except APIException:
            await ctx.send("Siapa itu ?")
        
            
        
        
    @command(name="mangasearch", aliases=["ms"])
    async def manga_search(self, ctx, *, manga):
        """Mencari manga dengan kata kunci"""
        
        result = jikan.search("manga", f"{manga}", page=1)
        list_manga = result["results"]
        menu = MenuPages(source=IsiMangaSearch(ctx, list_manga),
                         delete_message_after=False,
                         timeout=60.0)# bisa ditambah clear_reaction_after=True
        await menu.start(ctx)
        
    @command(name="character")
    async def character_detail(self, ctx, *, chara_id):
        """Mengambil info character dengan Character Id"""
        chara_id = int(chara_id)
        try:
            result = jikan.character(chara_id)
            embed = Embed(title= result['name'],
                        description= f"{str(result['name_kanji'])} \n\
Nicknames : {', '.join(str(nama) for nama in result['nicknames'])} ",
                        colour= ctx.author.colour)
            
            detil_chara = ''.join(str(result['about']).split('\\n'))
            
            dr_anim = '\n'.join(f"{str(result['animeography'][i]['name'])} : {str(result['animeography'][i]['role'])} " for i in range(len(result['animeography'])))
            if dr_anim == '':
                dr_anim = 'None'
            dr_mango = '\n'.join(f"{str(result['mangaography'][i]['name'])} : {str(result['mangaography'][i]['role'])} " for i in range(len(result['mangaography'])))
            if dr_mango == '':
                dr_mango = 'None'
            seyu = '\n'.join(f"{str(result['voice_actors'][i]['name'])} : {str(result['voice_actors'][i]['language'])} " for i in range(len(result['voice_actors'])))
            if seyu == '':
                seyu = 'None'

            fields = [("Menjadi Pujaan", f"{str(result['member_favorites'])} orang", False),
                    ("Dari Anime", dr_anim, False),
                    ("Dari Manga", dr_mango, False ),
                    ("Seiyuu", seyu, False ),
                    ("Detail Karakter", f"{detil_chara:.1021s}...", False )]
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
            embed.set_image(url=result['image_url'])
            
            await ctx.send(embed=embed)
        except APIException:
            await ctx.send(f"Tidak ditemukan karakter dengan id {chara_id}")
            
    @command(name="person")
    async def person_detail(self, ctx, *, chara_id):
        """Mengambil info orang dengan Id"""
        def Umur(tanggal):
            sekarang = date.now()
            if tanggal is None:
                umur = 'Tidak diketahui'
            elif sekarang.month > tanggal.month:
                umur = sekarang.year - tanggal.year
            elif sekarang.month == tanggal.month:
                if sekarang.day >= tanggal.day:
                    umur = sekarang.year - tanggal.year
                elif sekarang.day < tanggal.day:
                    umur = (sekarang.year - tanggal.year) - 1
            elif sekarang.month < tanggal.month:
                umur = (sekarang.year - tanggal.year) - 1
            return umur
        
        chara_id = int(chara_id)
        try:
            result = jikan.person(chara_id)
            embed = Embed(title= result['name'],
                        description= f"Given Name : {str(result['given_name'])} \n\
Family Name : {str(result['family_name'])} \n\
Aliases : {', '.join(str(nama) for nama in result['alternate_names'])} " ,
                        colour= ctx.author.colour)
            
            karir_s = '\n'.join(f"{str(result['voice_acting_roles'][i]['anime']['name'])} : {str(result['voice_acting_roles'][i]['character']['name'])} : {str(result['voice_acting_roles'][i]['role'])} " for i in range(min(9,len(result['voice_acting_roles']))))
            if karir_s == '':
                karir_s = 'None'
            
            mangas = '\n'.join(f"{result['published_manga'][i]['manga']['name']} : {result['published_manga'][i]['position']}" for i in range(len(result['published_manga'])))
            if mangas == '':
                mangas = 'None'
                
            posisi_staff = '\n'.join(f"{str(result['anime_staff_positions'][i]['anime']['name'])} : {str(result['anime_staff_positions'][i]['position'])} " for i in range(min(9, len(result['anime_staff_positions']))))
            if posisi_staff == '':
                posisi_staff = 'None'
                
            tgl = result['birthday']
            tgl_u = None
            if not tgl is None:
                tgl_u = date.fromisoformat(tgl)
                tgl = date.fromisoformat(tgl).strftime("%A, %d %B %Y")
                
                
                
            detil_chara = ''.join(str(result['about']).split('\\n'))
            
            fields = [("Menjadi Pujaan", f"{str(result['member_favorites'])} orang", False),
                    ("Tanggal lahir", str(tgl), False),
                    ("Umur", Umur(tgl_u), False ) ,
                    ("Karir Seiyuu", str(karir_s), False),
                    ("Posisi Staff Anime", str(posisi_staff), False ),
                    ("Published Manga", str(mangas), False ),
                    ("Detail Karakter", f"{detil_chara:.1021s}...", False )]
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
            embed.set_image(url=result['image_url'])
            
            await ctx.send(embed=embed)
        except APIException:
            await ctx.send(f"Tidak ditemukan manusia dengan id {chara_id}")
            
    @command(name="anime")
    async def anime_detail(self, ctx, *, anime_id):
        """Mengambil info anime dengan Anime Id"""
        anime_id = int(anime_id)
        try:
            result = jikan.anime(anime_id)
            embed = Embed(title= f"{result['title']}/{str(result['title_english'])} ({str(result['title_japanese'])})",
                          description= f"{'/'.join(str(alias) for alias in result['title_synonyms'])}\n\n\
Score : {str(result['score'])} dari {str(result['scored_by'])} orang \n\
Rank : {str(result['rank'])}\n\
Favorites : {str(result['favorites'])}\n\
Durasi Episode : {str(result['duration'])}",
                            colour= ctx.author.colour)
            try:
                adaptasi = '\n'.join(str(result['related']['Adaptation'][i]['name']) for i in range(len(result['related']['Adaptation'])))
                
            except KeyError:
                adaptasi = 'None'
            try:
                side_story = '\n'.join(str(result['related']['Side story'][i]['name']) for i in range(len(result['related']['Side story'])))
                
            except KeyError:
                side_story = 'None'
            try:
                sequel = '\n'.join(str(result['related']['Sequel'][i]['name']) for i in range(len(result['related']['Sequel'])))
                
            except KeyError:
                sequel = 'None'
            try:
                other = '\n'.join(str(result['related']['Other'][i]['name']) for i in range(len(result['related']['Other'])))
                
            except KeyError:
                other = 'None'
            producers = '\n'.join(str(result['producers'][i]['name']) for i in range(len(result['producers'])))
            if producers == '':
                producers = 'None'
            licensors = '\n'.join(str(result['licensors'][i]['name']) for i in range(len(result['licensors'])))
            if licensors == '':
                licensors = 'None'
            studios = ', '.join(str(result['studios'][i]['name']) for i in range(len(result['studios'])))
            if studios == '':
                studios = 'None'
            genres = ', '.join(str(result['genres'][i]['name']) for i in range(len(result['genres'])))
            if genres == '':
                genres = 'None'
            openings = '\n'.join(str(opening) for opening in result['opening_themes'])
            if openings == '':
                openings = 'None'
            endings = '\n'.join(str(ending) for ending in result['ending_themes'])
            if endings == '':
                endings = 'None'
            fields = ( ("Status", f"{str(result['status'])}\n{str(result['aired']['string'])}", False),
                       ("Premiere", f"{str(result['premiered'])}", False),
                       ("Producers", producers, False),
                       ("Licensors", licensors, False),
                       ("Studio", studios, False),
                       ("Genre", genres, False),
                       ("Diadaptasi dari", adaptasi, False),
                       ("Side Story", side_story, False),
                       ("Sequel", sequel, False),
                       ("Lain", other, False),
                       ("Opening", openings, False),
                       ("Ending", endings, False),
                       ("Sinopsis", "%.1021s..." % result['synopsis'], False)
                    )
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
            embed.set_image(url=result['image_url'])
            
            await ctx.send(embed=embed)
            
        except APIException:
            await ctx.send(f"Tidak ditemukan anime dengan id {anime_id}")
            
    @command(name="manga")
    async def manga_detail(self, ctx, *, manga_id):
        """Mengambil info manga dengan Manga Id"""
        manga_id = int(manga_id)
        try:
            result = jikan.manga(manga_id)
            embed = Embed(title= f"{result['title']}/{str(result['title_english'])} ({str(result['title_japanese'])})",
                          description= f"{'/'.join(str(alias) for alias in result['title_synonyms'])}\n\n\
Score : {str(result['score'])} dari {str(result['scored_by'])} orang \n\
Rank : {str(result['rank'])}\n\
Favorites : {str(result['favorites'])}\n\
Volume : {str(result['volumes'])}\n\
Chapter : {str(result['chapters'])} ",
                            colour= ctx.author.colour)
            try:
                adaptasi = '\n'.join(str(result['related']['Adaptation'][i]['name']) for i in range(len(result['related']['Adaptation'])))
                
            except KeyError:
                adaptasi = 'None'
            try:
                side_story = '\n'.join(str(result['related']['Side story'][i]['name']) for i in range(len(result['related']['Side story'])))
                
            except KeyError:
                side_story = 'None'
            try:
                sequel = '\n'.join(str(result['related']['Sequel'][i]['name']) for i in range(len(result['related']['Sequel'])))
                
            except KeyError:
                sequel = 'None'
            try:
                other = '\n'.join(str(result['related']['Other'][i]['name']) for i in range(len(result['related']['Other'])))
                
            except KeyError:
                other = 'None'
            authors = '\n'.join(str(result['authors'][i]['name']) for i in range(len(result['authors'])))
            if authors == '':
                authors = 'None'
            serializations = '\n'.join(f"{result['serializations'][i]['type']} : {result['serializations'][i]['name']}" for i in range(len(result['serializations'])))
            if serializations == '':
                serializations = 'None'
            genres = ', '.join(str(result['genres'][i]['name']) for i in range(len(result['genres'])))
            if genres == '':
                genres = 'None'
                
            fields = ( ("Status", f"{str(result['status'])}\n{str(result['published']['string'])}", False),
                       ("Authors", authors, False),
                       ("Serialisasi", serializations, False),
                       ("Genre", genres, False),
                       ("Diadaptasi dari", adaptasi, False),
                       ("Side Story", side_story, False),
                       ("Sequel", sequel, False),
                       ("Lain", other, False),
                       ("Sinopsis", "%.1021s..." % result['synopsis'], False)
                    )
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
            embed.set_image(url=result['image_url'])
            
            await ctx.send(embed=embed)
            
        except APIException:
            await ctx.send(f"Tidak ditemukan manga dengan id {manga_id}")
        
                
            
            
    # @Cog.listener()
    # async def on_reaction_add(self, reaction, user):
    #     if not user.bot:
            
    #         if reaction.emoji == "▶️":
    #             if reaction.message.id == self.as_id:
    #                 from json import load
    #                 with open("./data/Jikan/order.txt", "r") as f:
    #                     nilai = f.read()
    #                 nilai = int(nilai) + MOVER["▶️"]
    #                 with open("./data/Jikan/order.txt", "w") as f:
    #                     f.write(str(nilai))
    #                 with open("./data/Jikan/Hasil_Carian.json", "r") as f:
    #                     hasil_carian = load(f)
    #                 anime_terpilih = hasil_carian[nilai]
    #                 embed = Embed(title= anime_terpilih["title"],
    #                         description=f"Score : {anime_terpilih['score']:,.2f}\nTipe : {anime_terpilih['type']}\nEpisodes : {anime_terpilih['episodes']:,}\nSinopsis :\n      {anime_terpilih['synopsis']}",
    #                         colour=user.colour)

    #                 embed.set_image(url=anime_terpilih["image_url"])
    #                 msg = await reaction.message.channel.send(embed=embed)
    #                 for emoji in list(MOVER.keys()):
    #                     await msg.add_reaction(emoji)
    #                 self.as_id = msg.id
                
    #         elif reaction.emoji == "◀️":
    #             if reaction.message.id == self.as_id:
    #                 from json import load
    #                 with open("./data/Jikan/order.txt", "r") as f:
    #                     nilai = f.read()
    #                 nilai = int(nilai) + MOVER["◀️"]
    #                 with open("./data/Jikan/order.txt", "w") as f:
    #                     f.write(str(nilai))
    #                 with open("./data/Jikan/Hasil_Carian.json", "r") as f:
    #                     hasil_carian = load(f)
    #                 anime_terpilih = hasil_carian[nilai]
    #                 embed = Embed(title= anime_terpilih["title"],
    #                         description=f"Score : {anime_terpilih['score']:,.2f}\nTipe : {anime_terpilih['type']}\nEpisodes : {anime_terpilih['episodes']:,}\nSinopsis :\n      {anime_terpilih['synopsis']}",
    #                         colour=user.colour)

    #                 embed.set_image(url=anime_terpilih["image_url"])
    #                 msg = await reaction.message.channel.send(embed=embed)
    #                 for emoji in list(MOVER.keys()):
    #                     await msg.add_reaction(emoji)
    #                 self.as_id = msg.id
            
            
                
            
            

    @Cog.listener()
    async def on_ready(self):
        self.bot.cogs_ready.ready_up("animerelated")

def setup(bot):
    bot.add_cog(AnimeRelated(bot))