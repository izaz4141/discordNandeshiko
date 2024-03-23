from discord import Embed, Colour
from datetime import datetime

def profile_template(data, notes, ctx, uid) -> Embed :
    embed = Embed(
        title= f"{data.player.nickname}         ({data.player.level})",
        description= f"*{data.player.signature}*",
        color=ctx.author.colour
    )
    exped = 0
    for expedition in notes.expeditions:
        if expedition.finished:
            exped += 1
    fields = [
        ("Resin", f"{notes.current_resin}/{notes.max_resin}"),
        ("Daily Commision", f"{notes.completed_commissions}/{notes.max_commissions}\nClaimed: {notes.claimed_commission_reward}"),
        ("Expedition", f"Finished: { exped }/{notes.max_expeditions}"),
        ("Abyss Floor", f"{data.player.abyss_floor} - {data.player.abyss_room}"),
        ("Teapot Coin", f"{notes.current_realm_currency}/{notes.max_realm_currency}")
    ]
    for name, value in fields:
        if value == '':
                value = "N/A"
        embed.add_field(name=name, value=value, inline=True)
    embed.set_thumbnail(url= data.player.avatar.icon.url)
    embed.set_footer(text= f"UID: {uid}")
    return embed

def artifact_eval(chara, uid) -> Embed :
    if chara.rarity == 5:
        color = Colour.gold()
    else:
        color = Colour.purple()
    relics = Embed(
        title= chara.name,
        colour= color
    )
    fields = []
    for eq in chara.equipments:
        if eq.props == []:
            continue
        enhance = {}
        for prop in eq.props:
            try:
                enhance[prop.prop_id] += 1
            except KeyError:
                enhance[prop.prop_id] = 1
        subfix = '\n'.join([f"{substat.name} +{enhance[substat.prop_id]}:  {substat.value}{'%' if substat.type == 1 else ''}" for substat in eq.detail.substats])
        fields += [(f"{eq.detail.name} +{eq.level}", f"**{eq.detail.mainstats.name}:  {eq.detail.mainstats.value}{'%' if eq.detail.mainstats.type == 1 else ''}**\n{subfix}", True)]
    for name, value, inline in fields:
        if value == '':
                value = "N/A"
        relics.add_field(name=name, value=value, inline=inline)
    relics.set_thumbnail(url= chara.image.card.url)
    relics.set_footer(text= f"UID: {uid}")
    return relics