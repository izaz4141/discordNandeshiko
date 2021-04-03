from discord.ext.commands import Cog, command
from discord.ext.menus import MenuPages, ListPageSource
from discord.utils import get
from discord import Embed
from asyncio import TimeoutError
from jikanpy import Jikan
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
                      description=f"Score : {self.entries[menu.current_page]['score']:,.2f}\n\
Tipe : {self.entries[menu.current_page]['type']}\n\
Episodes : {self.entries[menu.current_page]['episodes']}\n\
Producer : {', '.join(str(self.entries[menu.current_page]['producers'][i]['name']) for i in range(len(self.entries[menu.current_page]['producers'])))}\n\
Licencors : {', '.join(str(i) for i in self.entries[menu.current_page]['licensors'])} \n\
Genre : {', '.join(str(genre['name']) for genre in self.entries[menu.current_page]['genres'])} \n\
Sinopsis :\n{self.entries[menu.current_page]['synopsis']}",
                      colour=self.ctx.author.colour)
        
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
                      description=f"Score : {self.entries[menu.current_page]['score']:,.2f}\nTipe : {self.entries[menu.current_page]['type']}\nEpisodes : {self.entries[menu.current_page]['episodes']:,}\nSinopsis :\n      {self.entries[menu.current_page]['synopsis']}",
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

class AnimeSearch(Cog):
    def __init__(self, bot):
        self.bot = bot


    @command(name="animesearch", aliases=["as"])
    async def anime_search(self, ctx, *, nama_anime: str):
        """Mencari Anime berdasar judul

        Args:
            ctx (str): command
            nama_anime (str): judul
        """
        
        result = jikan.search('anime', f'{nama_anime}', page=1)
        list_anime = result["results"]
        menu = MenuPages(source=IsiAnimeSearch(ctx, list_anime),
                         delete_message_after=True,
                         timeout=60.0)# bisa ditambah clear_reaction_after=True
        await menu.start(ctx)

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
    
    @command(name="seasonsearch", aliases=["ss"])
    async def season_search(self, ctx, *, musim_tahun: Optional[str]=None):
        """Harus berupa musim *spasi* tahun\nKategori musim : spring, summer, fall, winter.\nContoh: +ss fall 2020"""
        musim_tahun = str(musim_tahun).split(" ")
        musim = musim_tahun[0]
        try:
            tahun = musim_tahun[1]
            result = jikan.season(year= tahun, season= musim)
        except IndexError:
            result = jikan.season(season= musim)
        year = result["season_year"]
        season = result["season_name"]
        list_anime = result["anime"]
        menu = MenuPages(source=IsiSeasonSearch(season, year, ctx, list_anime),
                         delete_message_after=True,
                         timeout=60.0)# bisa ditambah clear_reaction_after=True
        await menu.start(ctx)
        
    # @command(name="jadwal")
    # async def jadwal_anime(self, ctx, *, hari:Optional[str]= date.today().strftime("%A")):
        
                
            
            
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
        self.bot.cogs_ready.ready_up("animesearch")

def setup(bot):
    bot.add_cog(AnimeSearch(bot))