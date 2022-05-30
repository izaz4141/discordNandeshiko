from mcstatus import JavaServer, BedrockServer
from discord import Embed
from os import getenv
from typing import Optional

url = getenv("MINECRAFT_LINK")
jv_serv = JavaServer(url)
br_serv = BedrockServer(url)

def get_status(link: Optional[str]):
    if not isinstance(link, type(None)):
        jv_serv = JavaServer.lookup(link)
        br_serv = BedrockServer.lookup(link)
    status = jv_serv.status()
    query = jv_serv.query()
    bs =br_serv.status()
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