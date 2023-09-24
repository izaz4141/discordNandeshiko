from mihomo import Language, MihomoAPI
from mihomo.models import StarrailInfoParsed

from discord import Embed, Colour
from datetime import datetime

client = MihomoAPI(language=Language.EN)

def relic_scorer(chara, uid):
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
