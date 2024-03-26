from discord import Embed, Colour
from datetime import datetime

from genshin.models.starrail import chronicle as models
from mihomo.models import StarrailInfoParsed


def relic_scorer(chara, uid) -> Embed :
    if chara.rarity == 5:
        color = Colour.gold()
    else:
        color = Colour.purple()
    relics = Embed(
        title= chara.name,
        colour= color
    )
    fields = []
    for relic in chara.relics:
        subfix = '\n'.join([f"{sub_affix.name} +{sub_affix.count}:  {sub_affix.displayed_value}" for sub_affix in relic.sub_affixes])
        fields += [(f"{relic.name} +{relic.level}", f"**{relic.main_affix.name}:  {relic.main_affix.displayed_value}**\n{subfix}", True)]
    for name, value, inline in fields:
        if value == '':
                value = "N/A"
        relics.add_field(name=name, value=value, inline=inline)
    relics.set_thumbnail(url= chara.icon)
    relics.set_footer(text= f"UID: {uid}")
    return relics

def profile_template(data, notes: models.StarRailNote, celeng: models.StarRailChallenge, pf: models.StarRailPureFiction, uid, ctx) -> Embed :
    embed = Embed(
        title= f"{data.player.name}         ({data.player.level})",
        description= f"*{data.player.signature}*",
        color=ctx.author.colour
    )
     
    sec = notes.stamina_recover_time.seconds
    jam = int(sec/3600)
    menit = int((sec % 3600)/60)
    detik = sec % 60
    finished = 0
    for expedition in notes.expeditions:
        if expedition.finished:
            finished += 1 
    waktu_MoC = celeng.end_time.datetime - datetime.utcnow()
    waktu_PF = pf.end_time.datetime - datetime.utcnow()
    waktu = [waktu_MoC, waktu_PF]
    for n, i in enumerate(waktu):
        if i.days == 0:
            sc = i.seconds
            j = int(sc/3600)
            m = int((sc % 3600)/60)
            d = sc % 60
            waktu[n] = f"{j} jam {m} menit {d} detik"
        else:
            waktu[n] = f"{i.days} hari" 
    fields = [
        ("Trailblaze Power", f"{notes.current_stamina}/{notes.max_stamina}\n{jam} jam {menit} menit {detik} detik"),
        ("Daily Commision", f"{notes.current_train_score}/{notes.max_train_score}"),
        ("Assignments", f"Finished: { finished }/{notes.total_expedition_num}"),
        ("Simulated Universe", f"{notes.current_rogue_score}/{notes.max_rogue_score}"),
        ("Echo of War", f"{notes.remaining_weekly_discounts}/{notes.max_weekly_discounts}"),
        ("Memory of Chaos", f"{celeng.total_stars}/36\n{waktu[0]} ❇"),
        ("Pure Fiction", f"{pf.total_stars}/12\n{waktu[1]} ❇"),
    ]
    for name, value in fields:
        if value == '':
                value = "N/A"
        embed.add_field(name=name, value=value, inline=True)
    embed.set_thumbnail(url= data.player.avatar.icon)
    embed.set_footer(text= f"UID: {uid}")

    return embed