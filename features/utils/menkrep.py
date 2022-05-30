from mcstatus import JavaServer, BedrockServer
from discord import Embed
from os import getenv
from typing import Optional

url = getenv("MINECRAFT_LINK")

def get_status(link: Optional[str]):
    link = link or url
    server = JavaServer.lookup(link)
    ser = BedrockServer.lookup(link)
    status = server.status()
    query = server.query()
    bs =ser.status()
    embed = Embed(
        title= f"{bs.map}",
        description= f"{status.description}"
    )
    fields = [
        ("Versi", f"Server {status.version.name} {query.software.brand} {query.software.version}"),
        ("Gamemode", bs.gamemode),
        ("Jumlah Player", f"{status.players.online}/{status.players.max}")
    ]
    if status.players.online > 0:
        fields.append(("List Player Online", '\n'.join(query.players.names)))
    for name, value in fields:
        if value == [] or value == "":
            value = "Tidak Diketahui"
        embed.add_field(name=name, value=value, inline=False)
    return embed

if __name__ == "__main__":
    get_status()