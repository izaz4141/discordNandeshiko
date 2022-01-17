import discord
from discord.ext.commands import command, Cog

import asyncio
from youtube_dl import YoutubeDL
from youtube_search import YoutubeSearch
import datetime as dt
import random


OPTIONS = {
    "1️⃣": 0,
    "2⃣": 1,
    "3⃣": 2,
    "4⃣": 3,
    "5⃣": 4,
}


class Music(Cog):
    def __init__(self, bot):
        self.bot = bot 
        self.YDL_OPTIONS = {
        'format': 'bestaudio[ext=webm]',
        'noplaylist': False
        }
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        # self.FFMPEG_OPTIONS = {'options' : '-vn'}
        self.song_queue = {}
        self.shuffle = {}
        self.repeat = {}
        self.np = {}
        self.playing = {}
        self.timer = {}


    async def check_queue(self, ctx):
        try:
            if len(self.song_queue[ctx.guild.id]) > 0:
                try:
                    if self.repeat[ctx.guild.id] is True:
                        self.song_queue[ctx.guild.id].append(self.np[ctx.guild.id])
                except KeyError:
                    self.repeat[ctx.guild.id] = False
                await self.play_song(ctx, self.song_queue[ctx.guild.id][0])
                self.song_queue[ctx.guild.id].pop(0)
                try:
                    if self.shuffle[ctx.guild.id] is True and len(self.song_queue[ctx.guild.id]) > 1:
                        random.shuffle(self.song_queue[ctx.guild.id])
                except KeyError:
                    self.shuffle[ctx.guild.id] = False
            else:
                try:
                    if self.repeat[ctx.guild.id] is True:
                        self.song_queue[ctx.guild.id] = [self.np[ctx.guild.id]]
                        await self.play_song(ctx, self.song_queue[ctx.guild.id][0])
                        self.song_queue[ctx.guild.id].pop(0)
                    else:
                        await self.leave(ctx)
                    
                except KeyError:
                    await self.leave(ctx)
        except KeyError:
            try:
                if self.repeat[ctx.guild.id] is True:
                    self.song_queue[ctx.guild.id] = [self.np[ctx.guild.id]]
                    await self.play_song(ctx, self.song_queue[ctx.guild.id][0])
                    self.song_queue[ctx.guild.id].pop(0)
                else:
                    await self.leave(ctx)
            except KeyError:
                await self.leave(ctx)
    
    async def choose_track(self, ctx, query):
        def _check(r, u):
            return (
                r.emoji in OPTIONS.keys()
                and u == ctx.author
                and r.message.id == msg.id
            )
            
        info = YoutubeSearch(query, max_results=5).to_dict()
        embed = discord.Embed(
            title="Pilih Lagu",
            description=(
                "\n".join(
                    f"**{i+1}.** {t['title']} ({':'.join(str(t['duration']).split('.'))})"
                    for i, t in enumerate(info[:5])
                )
            ),
            colour=ctx.author.colour,
            timestamp=dt.datetime.utcnow()
        )
        embed.set_author(name="Hasil Cari")
        embed.set_footer(text=f"Invoked by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)

        msg = await ctx.send(embed=embed)
        for emoji in list(OPTIONS.keys())[:min(len(info), len(OPTIONS))]:
            await msg.add_reaction(emoji)

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=_check)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.message.delete()
            return None
        else:
            await msg.delete()
            track = info[OPTIONS[reaction.emoji]]
            with YoutubeDL(self.YDL_OPTIONS) as ydl:
                try: 
                    lagu = ydl.extract_info(f"{'https://www.youtube.com' + track['url_suffix']}", download=False)['entries'][0]
                except Exception: 
                    return None
            return {'source': lagu['formats'][0]['url'], 'title': lagu['title']}

    async def link_handler(self, ctx, song):
        if "youtube.com/playlist?" in song:
            if not ctx.guild.id == 605057520955818010:
                return False
            msg = await ctx.send("Ditemukan suatu playlist, mohon tunggu sampai seluruh playlist dimasukkan dalam antrian")
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try: 
                info = ydl.extract_info(song, download=False)
            except Exception: 
                return None
        if not info['webpage_url_basename'] == "playlist":
            return {'source': info['formats'][0]['url'], 'title': info['title']}
        else:
            
            entries = []
            for entry in info['entries']:
                entries.append([entry['title'], entry['formats'][0]['url']])
            try:
                if self.playing[ctx.guild.id] is True:
                    for entry in entries:
                        self.song_queue[ctx.guild.id].append(entry)
                else:
                    await self.play_song(ctx, entries[0])
                    entries.pop(0)
                    for entry in entries:
                        self.song_queue[ctx.guild.id].append(entry)
                await msg.delete()
                await ctx.send(f"{len(entries)} lagu dari {info['title']} berhasil ditambahkan")
                return "playlist"
            except KeyError:
                await self.play_song(ctx, entries[0])
                entries.pop(0)
                self.song_queue[ctx.guild.id] = entries
                await msg.delete()
                await ctx.send(f"{len(entries)} lagu dari {info['title']} berhasil ditambahkan")
                return "playlist"
                            
    async def play_song(self, ctx, song):
        ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song[1], **self.FFMPEG_OPTIONS)), after=lambda error: self.bot.loop.create_task(self.check_queue(ctx)))
        ctx.voice_client.source.volume = 0.5
        self.np[ctx.guild.id] = song
        self.playing[ctx.guild.id] = True

    @command(name="join")
    async def join(self, ctx):
        if ctx.author.voice is None:
            return await ctx.send("Connect dulu ke voice channel ya kak")
        elif self.playing[ctx.guild.id] is True and ctx.author.voice.channel.id != ctx.voice_client.channel.id:
            await ctx.send("Ihh nanti aja ya kak, Nadeshiko lagi nyanyi")
            return 69
        elif ctx.voice_client is not None:
            await ctx.voice_client.disconnect()

        await ctx.author.voice.channel.connect()
        

    @command(name="leave", aliases=["disconnect"])
    async def leave(self, ctx):
        """Gunakan command ini untuk mereset cog musik apabila terjadi bug
        """
        if ctx.voice_client is not None:
            self.song_queue[ctx.guild.id] = []
            self.shuffle[ctx.guild.id] = False
            self.repeat[ctx.guild.id] = False
            self.np[ctx.guild.id] = []
            self.playing[ctx.guild.id] = False
            return await ctx.voice_client.disconnect()

        await ctx.send("Nadeshiko tidak sedang berada dalam voice channel")

    @command(name="play")
    async def play(self, ctx, *, song=None):
        if song is None:
            return await ctx.send("Pilih lagunya kak")
        if ctx.author.voice is None:
            return await ctx.send("Kakak harus masuk ke voice channel dulu!!")
        if ctx.voice_client is None:
            await self.join(ctx)
        elif ctx.author.voice.channel.id != ctx.voice_client.channel.id:
            a = await self.join(ctx)
            if a == 69:
                return
        link = ["youtube.com/playlist?", "youtube.com/watch?", "https://youtu.be/"]
        # handle song where song isn't url
        if not any(url in song for url in link):
            result = await self.choose_track(ctx, song)

            if result is None:
                return await ctx.send("Maaf kak, Nadeshiko tidak bisa menemukan lagu yang kakak maksud.")
        
        else:
            result = await self.link_handler(ctx, song)
            if result == 'playlist':
                return
            elif result is None:
                return await ctx.send("Maaf kak, Nadeshiko tidak bisa menemukan lagu yang kakak maksud")
            elif result is False:
                return await ctx.send("Maaf kak fitur menambahkan dari playlist dinonaktifkan di server kakak")

        try:
            if self.playing[ctx.guild.id] is True:
                try:
                    queue_len = len(self.song_queue[ctx.guild.id])
                except KeyError:
                    self.song_queue[ctx.guild.id] = [[result['title'], result['source']]]
                    return await ctx.send(f"**{result['title']}** telah ditambahkan dalam antrian posisi: 1.")
                if queue_len < 10:
                    self.song_queue[ctx.guild.id].append([result['title'], result['source']])
                    return await ctx.send(f"**{result['title']}** telah ditambahkan dalam antrian posisi: {queue_len+1}.")
        
            else:
                await self.play_song(ctx, [result['title'], result['source']])
                await ctx.send(f"Now playing: **{result['title']}**")
            #     return await ctx.send("Sorry, I can only queue up to 10 songs, please wait for the current song to finish.")
        except KeyError:
            await self.play_song(ctx, [result['title'], result['source']])
            await ctx.send(f"Now playing: **{result['title']}**")

    @command(name="queue", aliases=["q"])
    async def queue(self, ctx): # display the current guilds queue
        try:
            if len(self.song_queue[ctx.guild.id]) == 0:
                return await ctx.send("Tidak ada lagu dalam antrian")
        except KeyError:
            return await ctx.send("Tidak ada lagu dalam antrian")
        embed = discord.Embed(title="Song Queue", description="", colour=discord.Colour.dark_gold())
        i = 1
        for song in self.song_queue[ctx.guild.id]:
            embed.description += f"{i}) {song[0]}\n"

            i += 1

        await ctx.send(embed=embed)

    @command(name="skip")
    async def skip(self, ctx):
        if ctx.voice_client is None:
            return await ctx.send("Dih orang Nadeshiko ga lagi nyanyi juga")

        if ctx.author.voice is None:
            return await ctx.send("Masuk ke voice channel dulu ya kak")

        if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
            return await ctx.send("Nadeshiko ga lagi nyanyi buat kakak")

        poll = discord.Embed(title=f"Vote to Skip Song by - {ctx.author.name}#{ctx.author.discriminator}", description="**80% of the voice channel must vote to skip for it to pass.**", colour=discord.Colour.blue())
        poll.add_field(name="Skip", value=":white_check_mark:")
        poll.add_field(name="Stay", value=":no_entry_sign:")
        poll.set_footer(text="Voting ends in 15 seconds.")

        poll_msg = await ctx.send(embed=poll) # only returns temporary message, we need to get the cached message to get the reactions
        poll_id = poll_msg.id

        await poll_msg.add_reaction(u"\u2705") # yes
        await poll_msg.add_reaction(u"\U0001F6AB") # no
        
        await asyncio.sleep(15) # 15 seconds to vote

        poll_msg = await ctx.channel.fetch_message(poll_id)
        
        votes = {u"\u2705": 0, u"\U0001F6AB": 0}
        reacted = []

        for reaction in poll_msg.reactions:
            if reaction.emoji in [u"\u2705", u"\U0001F6AB"]:
                async for user in reaction.users():
                    if user.voice.channel.id == ctx.voice_client.channel.id and user.id not in reacted and not user.bot:
                        if user.id in self.bot.owner_ids:
                            votes[reaction.emoji] += 10
                        else:
                            votes[reaction.emoji] += 1
                        reacted.append(user.id)

        skip = False

        if votes[u"\u2705"] > 0:
            if votes[u"\U0001F6AB"] == 0 or votes[u"\u2705"] / (votes[u"\u2705"] + votes[u"\U0001F6AB"]) > 0.79: # 80% or higher
                skip = True
                embed = discord.Embed(title="Skip Successful", description="***Voting to skip the current song was succesful, skipping now.***", colour=discord.Colour.green())

        if not skip:
            embed = discord.Embed(title="Skip Failed", description="*Voting to skip the current song has failed.*\n\n**Voting failed, the vote requires at least 80% of the members to skip.**", colour=discord.Colour.red())

        embed.set_footer(text="Voting has ended.")

        await poll_msg.clear_reactions()
        await poll_msg.edit(embed=embed)

        if skip:
            self.song_queue[ctx.guild.id].append(self.np[ctx.guild.id])
            ctx.voice_client.stop()
            
    @command(name="skipto")
    async def skipto(self,ctx, *, number):
        if not number.isnumeric():
            return await ctx.send("Tolong masukkan nilai angka bulat ya kak")
        number = int(number)
        if not number <= len(self.song_queue[ctx.guild.id]):
            return await ctx.send(f"?? Nggak ada antrian nomer {number} tuh")
        if ctx.voice_client is None:
            return await ctx.send("Dih orang Nadeshiko ga lagi nyanyi juga")

        if ctx.author.voice is None:
            return await ctx.send("Masuk ke voice channel dulu ya kak")

        if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
            return await ctx.send("Nadeshiko ga lagi nyanyi buat kakak")
        poll = discord.Embed(title=f"Vote to Skip Song by - {ctx.author.name}#{ctx.author.discriminator}", description="**80% of the voice channel must vote to skip for it to pass.**", colour=discord.Colour.blue())
        poll.add_field(name="Skip", value=":white_check_mark:")
        poll.add_field(name="Stay", value=":no_entry_sign:")
        poll.set_footer(text="Voting ends in 15 seconds.")

        poll_msg = await ctx.send(embed=poll) # only returns temporary message, we need to get the cached message to get the reactions
        poll_id = poll_msg.id

        await poll_msg.add_reaction(u"\u2705") # yes
        await poll_msg.add_reaction(u"\U0001F6AB") # no
        
        await asyncio.sleep(15) # 15 seconds to vote

        poll_msg = await ctx.channel.fetch_message(poll_id)
        
        votes = {u"\u2705": 0, u"\U0001F6AB": 0}
        reacted = []

        for reaction in poll_msg.reactions:
            if reaction.emoji in [u"\u2705", u"\U0001F6AB"]:
                async for user in reaction.users():
                    if user.voice.channel.id == ctx.voice_client.channel.id and user.id not in reacted and not user.bot:
                        if user.id in self.bot.owner_ids:
                            votes[reaction.emoji] += 10
                        else:
                            votes[reaction.emoji] += 1
                        reacted.append(user.id)

        skip = False

        if votes[u"\u2705"] > 0:
            if votes[u"\U0001F6AB"] == 0 or votes[u"\u2705"] / (votes[u"\u2705"] + votes[u"\U0001F6AB"]) > 0.79: # 80% or higher
                skip = True
                embed = discord.Embed(title="Skip Successful", description="***Voting to skip the current song was succesful, skipping now.***", colour=discord.Colour.green())

        if not skip:
            embed = discord.Embed(title="Skip Failed", description="*Voting to skip the current song has failed.*\n\n**Voting failed, the vote requires at least 80% of the members to skip.**", colour=discord.Colour.red())

        embed.set_footer(text="Voting has ended.")

        await poll_msg.clear_reactions()
        await poll_msg.edit(embed=embed)

        if skip:
            self.song_queue[ctx.guild.id].insert(0, self.song_queue[ctx.guild.id][number-1])
            self.song_queue[ctx.guild.id].pop(number)
            self.song_queue[ctx.guild.id].append(self.np[ctx.guild.id])
            ctx.voice_client.stop()

    @command(name="pause")
    async def pause(self, ctx):
        if ctx.voice_client.is_paused():
            return await ctx.send("Nadeshiko ga lagi nyanyi kok kak")

        ctx.voice_client.pause()
        await ctx.send("Lagu telah dijeda")

    @command(name="resume")
    async def resume(self, ctx):
        if ctx.voice_client is None:
            return await ctx.send("Joinin aku dulu kak")

        if not ctx.voice_client.is_paused():
            return await ctx.send("Berisik ih, lagi nyanyi juga")
        
        ctx.voice_client.resume()
        await ctx.send("Okee, ku lanjut nyanyi yaa")
    
    @command(name="np")
    async def np(self,ctx):
        if not self.np[ctx.guild.id] == []:
            await ctx.send(f"Now playing: **{self.np[ctx.guild.id][0]}**")
        else:
            await ctx.send("Nadeshiko sedang tidak menyanyi")
    
    @command(name="shuffle")
    async def shuffle(self, ctx):
        try:
            if self.shuffle[ctx.guild.id] is False:
                self.shuffle[ctx.guild.id] = True
                await ctx.send("Mode shuffle diaktifkan")
            else:
                self.shuffle[ctx.guild.id] = False
                await ctx.send("Mode shuffle dimatikan")
        except KeyError:
            self.shuffle[ctx.guild.id] = True
            await ctx.send("Mode shuffle diaktifkan")
            
    @command(name="repeat")
    async def repeat(self, ctx):
        try:
            if self.repeat[ctx.guild.id] is False:
                self.repeat[ctx.guild.id] = True
                await ctx.send("Mode repeat diaktifkan")
            else:
                self.repeat[ctx.guild.id] = False
                await ctx.send("Mode repeat dimatikan")
        except KeyError:
            self.repeat[ctx.guild.id] = True
            await ctx.send("Mode repeat diaktifkan")
            
    @command(name="remove")
    async def remove(self, ctx, number):
        number = int(number)
        if number <= len(self.song_queue[ctx.guild.id]):
            await ctx.send(f"**{self.song_queue[ctx.guild.id][number-1][0]}** telah dihapus dari antrian")
            self.song_queue[ctx.guild.id].pop(number-1)
            
    @Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        
        # if event is triggered by the bot? return
        if member.bot:
            return

        # when before.channel != None that means user isnt joining a channel
        if before.channel != None:
            voice = discord.utils.get(self.bot.voice_clients , channel__guild__id = before.channel.guild.id)

            # voice is voiceClient and if it's none? that means the bot is not in an y VC of the Guild that triggerd this event 
            if voice == None:
                return

            # if VC left by the user is not equal to the VC that bot is in? then return
            if voice.channel.id != before.channel.id:
                return
            not_bot = []
            for member in voice.channel.members:
                if not member.bot:
                    not_bot.append(member)
                    break
            if len(not_bot) == 0:

                self.timer[before.channel.guild.id] = 0

                while True:
                    # print("Time" , str(GUILD_VC_TIMER[before.channel.guild.id]) , "Total Members" , str(len(voice.channel.members)))

                    await asyncio.sleep(1)

                    self.timer[before.channel.guild.id] += 1
                    not_bot = []
                    for member in voice.channel.members:
                        if not member.bot:
                            not_bot.append(member)
                            break
                    # if vc has more than 1 member or bot is already disconnectd ? break
                    if len(not_bot) >= 1 or not voice.is_connected():
                        break

                    # if bot has been alone in the VC for more than 60 seconds ? disconnect
                    if self.timer[before.channel.guild.id] >= 60:
                        self.song_queue[member.guild.id] = []
                        self.shuffle[member.guild.id] = False
                        self.repeat[member.guild.id] = False
                        self.np[member.guild.id] = []
                        self.playing[member.guild.id] = False
                        await voice.disconnect()
                        return

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("music")

def setup(bot):
    bot.add_cog(Music(bot))