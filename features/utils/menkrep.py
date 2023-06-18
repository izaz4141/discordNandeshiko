from mcstatus import JavaServer
from discord import Embed
from os import getenv
from typing import Optional
from aiohttp import ClientSession as session

url = getenv("MINECRAFT_LINK")

def get_status(link: Optional[str]=None):
    """
    Mengecek Status Server Minecraft Menggunakan module python mcstatus
    """
    link = link or url
    server = JavaServer.lookup(link)
    status = server.status()
    query = server.query()
    embed = Embed(
        title= f"{link}",
        description= f"{status.description}"
    )
    fields = [
        ("Versi", f"Server {status.version.name} {query.software.brand} {query.software.version}"),
        ("Jumlah Player", f"{status.players.online}/{status.players.max}")
    ]
    if status.players.online > 0:
        fields.append(("List Player Online", ', '.join(query.players.names[:6])))
    for name, value in fields:
        if value == [] or value == "":
            value = "Tidak Diketahui"
        embed.add_field(name=name, value=value, inline=False)
    return embed, status.players.online

async def get_status_2(link: Optional[str]=None):
    """
    Mengecek Status Server Minecraft Menggunakan Request ke API Mcsrvstat
    """
    link = link or url
    async with session() as sess:
        async with sess.get(f'https://api.mcsrvstat.us/2/{link}') as resp:
            data = await resp.json()
    embed = Embed(
        title= f"{link}",
        description= f"{data['motd']['clean'][0]}"
    )
    fields = [
        ("Versi", f"Server {data['software'] or 'Minecraft'}: {data['version']} "),
        ("Jumlah Player", f"{data['players']['online']}/{data['players']['max']}")
    ]
    if data['players']['online'] > 0:
        fields.append(("List Player Online", ', '.join(data['players']['list'][:10])))
    for name, value in fields:
        if value == [] or value == "":
            value = "Tidak Diketahui"
        embed.add_field(name=name, value=value, inline=False)
    return embed, data['players']['online']


if __name__ == "__main__":
    get_status()