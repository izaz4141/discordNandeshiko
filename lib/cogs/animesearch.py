from discord.ext.commands import Cog, command
from discord.ext.menus import MenuPages, ListPageSource
from discord.utils import get
from discord import Embed

# def syntax(command):
#     cmd_and_alias = " | ".join([str(command), *command.aliases])
#     params = []

#     for key, value in command.params.items():
#         if key not in ("self", "ctx"):
#             params.append(f"{key}" if "NoneType" in str(value) else f"<{key}>")

#     params = " ".join(params)

#     return f"```{cmd_and_alias} {params}```"

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


    @command(name="animesearch", aliases=["aser"])
    async def anime_search(self, ctx, *, nama_anime: str):
        """Show This Message"""
        from jikanpy import Jikan
        jikan = Jikan()
        result = jikan.search('anime', f'{nama_anime}', page=1)
        list_anime = result["results"]
        menu = MenuPages(source=IsiAnimeSearch(ctx, list_anime),
                         delete_message_after=True,
                         timeout=60.0)# bisa ditambah clear_reaction_after=True
        await menu.start(ctx)


    @Cog.listener()
    async def on_ready(self):
        self.bot.cogs_ready.ready_up("animesearch")

def setup(bot):
    bot.add_cog(AnimeSearch(bot))