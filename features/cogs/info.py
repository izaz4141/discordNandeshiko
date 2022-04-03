from discord.ext.commands import Cog, command
from discord import Member, Embed
from typing import Optional
from datetime import datetime

class Info(Cog):
    def __init__(self,bot):
        self.bot = bot

    @command(name="userinfo", aliases=["ui"])
    async def user_info(self, ctx, *, target: Optional[Member]):
        """Memberi Info User yang dimention/diri sendiri"""
        target = target or ctx.author

        embed = Embed(title="User Information",
                      colour=target.colour,
                      timestamp = datetime.utcnow())

        if target.activity is None:
            fields = [("Nama", target.display_name, True),
                      ("ID", target.id, False),
                      ("Role", target.top_role.mention, False),
                      ("Status", str(target.status).title(), True),
                      ("Aktivitas", f"{bool(target.activity)}", True),
                      ("Tanggal Akun Dibuat", target.created_at.strftime("%d/%m/%Y %H:%M:%S"), False),
                      ("Tanggal Join Server", target.joined_at.strftime("%d/%m/%Y %H:%M:%S"), False),
                      ("Boosted", bool(target.premium_since), True),
                      ("Hp Status", f"{str(target.mobile_status)}", True),
                      ("Web Status", f"{str(target.web_status)}", True),
                      ("Desktop Status", f"{str(target.desktop_status)}", True),
                      ("Client Status", f"{''.join(''.join(str(target._client_status).split('{')).split('}'))}", False)
                     ]
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
        else:
            fields = [("Nama", target.display_name, True),
                      ("ID", target.id, False),
                      ("Role", target.top_role.mention, False),
                      ("Status", str(target.status).title(), True),
                      ("Aktivitas", f"{str(target.activity.type).split('.')[-1].title()}type: {target.activity.name} ", True),
                      ("Tanggal Akun Dibuat", target.created_at.strftime("%d/%m/%Y %H:%M:%S"), False),
                      ("Tanggal Join Server", target.joined_at.strftime("%d/%m/%Y %H:%M:%S"), False),
                      ("Boosted", bool(target.premium_since), True),
                      ("Hp Status", f"{str(target.mobile_status)}", True),
                      ("Web Status", f"{str(target.web_status)}", True),
                      ("Desktop Status", f"{str(target.desktop_status)}", True),
                      ("Client Status", f"{''.join(''.join(str(target._client_status).split('{')).split('}'))}", False)
                    ]
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
        embed.set_thumbnail(url=target.avatar.url)
        await ctx.send(embed=embed)
        
    @command(name="avatar")
    async def avatar_show(self, ctx, *, target: Optional[Member]):
        """Menampilkan Display Picture

        Args:
            ctx (str): command
            target (Member): mention member
        """
        target = target or ctx.author
        embed = Embed(colour= target.colour)
        embed.set_image(url= target.avatar.url)
        await ctx.send(embed= embed)

    @command(name="serverinfo", aliases=["guildinfo", "si", "gi"])
    async def server_info(self, ctx):
        """Menampilkan info server"""
        embed = Embed(title="Server information",
                      colour=ctx.guild.owner.colour,
                      timestamp=datetime.utcnow())

        embed.set_thumbnail(url=ctx.guild.icon_url)

        statuses = [len(list(filter(lambda m: str(m.status) == "online", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "idle", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "dnd", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "offline", ctx.guild.members)))]

        fields = [("ID", ctx.guild.id, True),
                ("Owner", ctx.guild.owner, False),
                ("Region", ctx.guild.region, True),
                ("Created at", ctx.guild.created_at.strftime("%d/%m/%Y %H:%M:%S"), False),
                ("Members", len(ctx.guild.members), True),
                ("Humans", len(list(filter(lambda m: not m.bot, ctx.guild.members))), True),
                ("Bots", len(list(filter(lambda m: m.bot, ctx.guild.members))), True),
                ("Banned members", len(await ctx.guild.bans()), True),
                ("Invites", len(await ctx.guild.invites()), True),
                ("Text channels", len(ctx.guild.text_channels), True),
                ("Voice channels", len(ctx.guild.voice_channels), True),
                ("Categories", len(ctx.guild.categories), True),
                ("Roles", len(ctx.guild.roles), True),
                ("Statuses", f"🟢 {statuses[0]} 🟠 {statuses[1]} 🔴 {statuses[2]} ⚪ {statuses[3]}", True),
                ("\u200b", "\u200b", True)]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await ctx.send(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("info")

def setup(bot):
    bot.add_cog(Info(bot))
