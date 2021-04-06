from NHentai import NHentai
from discord.ext.menus import MenuPages, ListPageSource
from discord.ext.commands import Cog, CheckFailure, command
from discord import Embed

nhen = NHentai()

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

class Nhen(Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @command(name="berandasurga", aliases=["bs"])
    async def Nhen_Home(self, ctx):
        kamus_hen = {}
        home = nhen.get_pages(page=1)
        for i in range(len(home.doujins)):
            dojin = home.doujins[i]
            dojin_id = dojin.id
            dojin_lang = dojin.lang
            dojin_cover = dojin.cover
            dojin_title = dojin.title
            dojin_tags = dojin.data_tags #list
            kamus_hen[i] = {
                "name" : dojin_title,
                "id" : dojin_id,
                "language" : dojin_lang,
                "tags" : dojin_tags,
                "image_url" : dojin_cover
            }
        menu = MenuPages(source=IsiNHenHome(ctx, kamus_hen),
                        delete_message_after=False,
                        timeout=60.0)# bisa ditambah clear_reaction_after=True
        await menu.start(ctx)
        
    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("nhen")



def setup(bot):
    bot.add_cog(Nhen(bot))