from discord.ext.commands import Cog, CheckFailure, command, has_permissions, has_role, cooldown, BucketType

from discord import Embed

from datetime import datetime, timedelta
from random import randint, choices
from typing import Optional
from asyncio import TimeoutError
from json import loads, JSONDecodeError, dumps
from ..db import db

OPTIONS = {
    "⚔️" : "attack",
    "🛡️" : "defend"
}
inBattle = {}
dungeon = {
    "Trial Tower" : {
        "Event" :[
            "Monster", "Treasure"
        ],
        "Monster" : {
            "Slime" : {
                "id" : 1,
                "hp" : 50,
                "mp" : 0,
                "strength" : 3,
                "intelligence" : 0,
                "dexerity" : 1,
                "lvl" : 1,
                "luck" : 20,
                "items" : {},
                "yen" : 20,
                "nadeC" : 0,
                "lokasi" : "Trial Tower"
            },
            "Frogzard" : {
                "id" : 2,
                "hp" : 90,
                "mp" : 0,
                "strength" : 6,
                "intelligence" : 0,
                "dexerity" : 2,
                "lvl" : 2,
                "luck" : 30,
                "items" : {},
                "yen" : 30,
                "nadeC" : 0,
                "lokasi" : "Trial Tower"
            }
        },
        "Treasure" : {
            "yen" : [70, 100],
            "items" : {
                "hp_pot" : [2, 4]
            }
        },
        "Treasure_times" : [1,2]
    }
}

fightOneMonster = {}

class Monster:
    def __init__(self, name, dungeon_place:dict, p_id):
        self.name = name
        self.identity = dungeon_place["Monster"][name]["id"]
        self.hp = dungeon_place["Monster"][name]["hp"]
        self.mp = dungeon_place["Monster"][name]["mp"]
        self.lvl = dungeon_place["Monster"][name]["lvl"]
        self.strength = dungeon_place["Monster"][name]["strength"]
        self.intelligence = dungeon_place["Monster"][name]["intelligence"]
        self.dexerity = dungeon_place["Monster"][name]["dexerity"]
        self.luck = dungeon_place["Monster"][name]["luck"]
        self.items = dungeon_place["Monster"][name]["items"]
        self.yen = dungeon_place["Monster"][name]["yen"]
        self.nadeC = dungeon_place["Monster"][name]["nadeC"]
    
        self.p_id = p_id  
        
    def hp_change(self, delta_hp):
        self.hp = self.hp + delta_hp
        return self.hp
    def mp_change(self, delta_mp):
        self.mp = self.mp + delta_mp
        return self.mp
    
    def strength_change(self, delta_str):
        self.strength = self.strength + delta_str
        return self.strength
    def intelligence_change(self, delta_int):
        self.intelligence = self.intelligence + delta_int
        return self.intelligence
    def dexerity_change(self, delta_dex):
        self.dexerity = self.dexerity + delta_dex
        return self.dexerity
        

class Player:
    def __init__(self, identity, ctx: Optional=None, m_name: Optional=None, d_name: Optional=None, battle_id: Optional=None):
        self.identity = identity
        self.hp = db.record("SELECT HP FROM exp WHERE UserID = ?", self.identity)[0]
        self.mp = db.record("SELECT MP FROM exp WHERE UserID = ?", self.identity)[0]
        self.lvl = db.record("SELECT Level FROM exp WHERE UserID = ?", self.identity)[0]
        self.strength = db.record("SELECT Strength FROM exp WHERE UserID = ?", self.identity)[0]
        self.intelligence = db.record("SELECT Intelligence FROM exp WHERE UserID = ?", self.identity)[0]
        self.dexerity = db.record("SELECT Dexerity FROM exp WHERE UserID = ?", self.identity)[0]
        self.luck = db.record("SELECT Luck FROM exp WHERE UserID = ?", self.identity)[0]
        self.statP = db.record("SELECT StatusPoint FROM exp WHERE UserID = ?", self.identity)[0]
        self.yen = db.record("SELECT Yen FROM exp WHERE UserID = ?", self.identity)[0]
        self.nadeC = db.record("SELECT Nadecoin FROM exp WHERE UserID = ?", self.identity)[0]
        self.items = db.record("SELECT Items FROM exp WHERE UserID = ?", self.identity)[0]
        self.charas = db.record("SELECT Charas FROM exp WHERE UserID = ?", self.identity)[0]
        try:
            self.charas = loads(self.charas)
        except JSONDecodeError:
            self.charas = self.charas.split('"')
        try:
            self.items = loads(self.items)
        except JSONDecodeError:
            self.items = self.items
        if not m_name is None:
            self.m_name = m_name
        if not d_name is None:
            self.d_name = d_name
        if not battle_id is None:
            self.battle_id = battle_id

        
    def hp_change(self, delta_hp):
        self.hp = self.hp + delta_hp
        return self.hp
    def mp_change(self, delta_mp):
        self.mp = self.mp + delta_mp
        return self.mp
    
    def strength_change(self, delta_str):
        self.strength = self.strength + delta_str
        return self.strength
    def intelligence_change(self, delta_int):
        self.intelligence = self.intelligence + delta_int
        return self.intelligence
    def dexerity_change(self, delta_dex):
        self.dexerity = self.dexerity + delta_dex
        return self.dexerity
    
    def items_change(self, delta_items:dict):
        for key in delta_items.keys():
            try:
                self.items[key] += delta_items[key]
            except KeyError:
                self.items[key] = delta_items[key]
        db.execute("UPDATE SET Items = ? FROM exp WHERE UserID = ?", dumps(self.items), self.identity)
        
    def dungeon_treasures(self, ctx, dungeon_place:dict):
        kali = randint(dungeon_place["Treasure_times"][0], dungeon_place["Treasure_times"][1])
        delta_yen_akhir = 0
        delta_nadeC_akhir = 0
        delta_items = {}
        for i in range (1, kali+1):
            treasure_baru = choices([*dungeon_place["Treasure"]])[0]
            if treasure_baru == "yen":
                delta_yen = randint(dungeon_place["Treasure"]["yen"][0], dungeon_place["Treasure"]["yen"][1])
                delta_yen_akhir += delta_yen
                
            elif treasure_baru == "nadeC":
                
                delta_nadeC = randint(dungeon_place["Treasure"]["nadeC"][0], dungeon_place["Treasure"]["nadeC"][1])
                delta_nadeC_akhir += delta_nadeC
                
            
            elif treasure_baru == "items":
                item = choices([*dungeon_place["Treasure"]["items"]])[0]
                try:
                    delta_items[item] += randint(dungeon_place["Treasure"]["items"][item][0], dungeon_place["Treasure"]["items"][item][1])
                except KeyError:
                    delta_items[item] = randint(dungeon_place["Treasure"]["items"][item][0], dungeon_place["Treasure"]["items"][item][1])
                
        yen_lama = db.record("SELECT Yen FROM exp WHERE UserID = ?", ctx.message.author.id)[0]
        yen_baru = yen_lama + delta_yen_akhir
        
        nadeC_lama = db.record("SELECT Nadecoin FROM exp WHERE UserID = ?", ctx.message.author.id)[0]
        nadeC_baru = nadeC_lama + delta_nadeC_akhir
        
        for item in delta_items.keys():
            try:
                self.items[item] += delta_items[item]
            except KeyError:
                self.items[item] = delta_items[item]
        self.yen = yen_baru
        self.nadeC = nadeC_baru
        items_lama = dumps(self.items)
        db.execute("UPDATE exp SET Yen = ?, Nadecoin = ?, Items = ? WHERE UserID = ?", yen_baru, nadeC_baru, items_lama, ctx.message.author.id)
        return self.yen, delta_yen_akhir, self.nadeC, delta_nadeC_akhir, self.items, delta_items
        

# class Fight:
#     def __init__(self, player, monster, ctx: Optional=None):
#         self.player = player
#         self.monster = monster
        
    # def PlayerVOneMonster(self, ctx):
#         embed = Embed(
#             title= ctx.author.name,
#             colour=ctx.author.colour
#         )
#         fields = [
#             (f"{ctx.author.name}", 
#              f"HP = {self.player.hp}\n\
# MP = {self.player.mp}\n\
# ATK = {}")
#         ]
        
    
        
        

class Game(Cog):
    def __init__(self,bot):
        self.bot = bot
        
    

    async def process_xp(self, message):
        xp, lvl, xplock = db.record("SELECT XP, Level, XPLock FROM exp WHERE UserID = ?", message.author.id)

        if datetime.fromisoformat(xplock) < datetime.utcnow():
            await self.add_xp(message, xp, lvl)

    async def add_xp(self, message, xp, lvl):
        xp_to_add = randint(10,20)
        new_level = int(((xp+xp_to_add)//42) ** 0.55)

        db.execute("UPDATE exp SET XP = XP + ? , Level = ?, XPLock = ? WHERE UserID = ?",
                    xp_to_add, new_level, (datetime.utcnow()+timedelta(seconds=45)).isoformat(), message.author.id)

        if new_level > lvl:
            wic = []
            for guild in self.bot.guilds:
                if guild.get_member(message.author.id):
                    wic.append(guild.id)
            for gid in wic:
                log_channel = db.field("SELECT LogChannel FROM guilds WHERE GuildID = ?", gid)
                if db.field("SELECT Leg FROM guilds WHERE GuildID = ?", gid) == 'ON':
                    await self.bot.get_channel(log_channel).send(f"**{message.author.display_name}** telah mencapai level {new_level:,}, GJ")
            
    @command(name="dungeonlist", aliases=["dl"])
    async def dungeon_list(self, ctx):
        d_list = dungeon.keys()
        await ctx.send('\n'.join(d_list))
        
    @command(name="dungeon")
    @cooldown(3, 60.0, BucketType.user)
    @has_role("BLANKET")
    async def dungeon_enter(self, ctx, *, nomor):
        def _check(r, u):
            return (
                r.emoji in OPTIONS.keys()
                and u == ctx.author
                and r.message.id == msg.id
            )
        nomor = int(nomor)
        nomor -= 1
        dungeon_place_name = [*dungeon][nomor]
        dungeon_place = dungeon[dungeon_place_name]
        dungeon_event = choices([*dungeon_place["Event"]])[0]
        if dungeon_event == "Treasure":
            p_yen, de_yen, p_nadeC, de_nadeC, p_items, de_items = Player(ctx.message.author.id, ctx).dungeon_treasures(ctx, dungeon_place)
            
            embed = Embed(
                title= f"Setelah berpetualang di  dalam {dungeon_place_name}",
                description= f"Kakak Mendapat :",
                colour= ctx.message.author.colour,
                timestamp= datetime.utcnow()
            )
            fields = [
                ("Yen", f"{p_yen}   ```+{de_yen}```"),
                ("NadeCoin", f"{p_nadeC}   ```+{de_nadeC}```")
            ]
            for item in de_items:
                fields.append((item, f"{p_items[item]}   ```+{de_items[item]}```"))
            
            for name, value in fields:
                embed.add_field(name=name, value=value, inline=False)
                
            embed.set_thumbnail(url= ctx.author.avatar_url)
            
            await ctx.send(embed=embed)
            
        elif dungeon_event == "Monster":
            dungeon_monster = choices([*dungeon_place["Monster"]])[0]
            await ctx.send(f"Seekor {dungeon_monster} lewat")
            # fightOneMonster[ctx.author.id] = Fight(Player(ctx.author.id), Monster(dungeon_monster, dungeon_place, ctx.author.id))
            # embed, message_id = fightOneMonster[ctx.author.id].PlayerVOneMonster(ctx)
            # await ctx.send(embed=embed)
                

    



    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("game")

    @Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            if self.bot.ready:
                await self.process_xp(message)
            
    # @Cog.listener()
    # async def on_reaction_add(self,reaction,user):
    #     if user.id in [*inBattle]:
    #         if reaction.message.id == Fight.players[user.id].battle_id:
    #             def _check(r, u):
    #                 return (
    #                     r.emoji in OPTIONS.keys()
    #                     and u == user
    #                     and r.message.id == msg.id
    #                 )
    #             if reaction.emoji == "⚔️":
    #                 p_dmg = Fight(Player(user.id), Monster(Player(user.id).m_name, Player(user.id).d_name),user.id).User_Attack(user.id)
    #                 p_act = "Menyerang"
                
                    
    #             if reaction.emoji == "🛡️":
    #                 fight = Fight(Player(user.id), Monster(Player(user.id).m_name, Player(user.id).d_name, user.id))
    #                 fight.players[user.id].strength = fight.players[user.id].strength * (1.6*(randint(fight.players[user.id].luck, 100)/100))
    #                 fight.players[ctx.message.author.id].dexerity = fight.players[user.id].dexerity * (1.4*(randint(fight.players[user.id].luck, 100)/100))
    #                 p_act = "Bertahan"
                    
    #             e_action = choices(["attack", "defend"])[0]
                
    #             if e_action == "attack":
    #                 fight = Fight(Player(user.id), Monster(Player(user.id).m_name, Player(user.id).d_name, user.id))
    #                 m_dmg = fight.Monster_Attack(user.id)
    #                 m_act = "Menyerang"
                    
    #             if e_action == "defend":
    #                 fight = Fight(Player(user.id), Monster(Player(user.id).m_name, Player(user.id).d_name, user.id))
    #                 fight.monsters[user.id].strength = fight.monsters[user.id].strength * (1.6*(randint(fight.monsters[user.id].luck, 100)/100))
    #                 fight.monsters[user.id].dexerity = fight.monsters[user.id].dexerity * (1.4*(randint(fight.monsters[user.id].luck, 100)/100))
    #                 m_act = "Bertahan"
                
    #             embed = Fight(Player(user.id), Monster(Player(user.id).m_name, Player(user.id).d_name)).Battle_Response(user, p_dmg, m_dmg, p_act, m_act)
                
    #             msg = await reaction.message.edit(embed=embed)
    #             for emoji in list(OPTIONS.keys()):
    #                 await msg.add_reaction(emoji)
    #             try:
    #                 await self.bot.wait_for("reaction_add", timeout=300.0, check=_check)
    #             except TimeoutError:
    #                 await reaction.message.channel.send("Dikarenakan melebihi 5 menit, Pertandingan berakhir")
    #                 await msg.delete()
    #                 inBattle[user.id] = False
                
                

def setup(bot):
    bot.add_cog(Game(bot))