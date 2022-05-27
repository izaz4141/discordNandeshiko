from discord import Embed, Colour, PCMVolumeTransformer, FFmpegOpusAudio, FFmpegPCMAudio
from discord.ext.commands import command, Cog
from ..utils.menus import MenuPages, ListPageSource
from discord.utils import get

import asyncio
# from youtube_dl import YoutubeDL
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch
from time import time
import datetime as dt
import random
from urllib3 import PoolManager
import shutil
# Import Module
from PIL import Image
import os


OPTIONS = {
    "1️⃣": 0,
    "2⃣": 1,
    "3⃣": 2,
    "4⃣": 3,
    "5⃣": 4,
}

BUTTON = {
    # "⏬" : "vol_down",
    # "⏫" : "vol_up",
    "⏮️" : 'previous',
    # "🎶" : "queue",
    "🔀" : 'shuffle',
    "⏯️" : 'playpause',
    "🔁" : 'repeat',
    "🔂" : "repeat_one",
    "⏭️" : 'next'
}

BAR = {
    0 : "▮",
    1 : "▯"
}

BUTTON_QUEUE = [ "⏮️", "◀️", "▶️", "⏭️" ]

urlp = PoolManager()

def format_durasi(durasi:int):
    durasi = int(durasi)
    donat = durasi
    if durasi >= 3600:
        jam = durasi//3600
        donat = durasi%3600
    if donat >= 60:
        menit = donat//60
        detik = donat%60
    else:
        menit = 0
        detik = donat
    if durasi >= 3600:
        return f"{jam}:{menit}:{detik}"
    else:
        return f"{menit}:{detik}"

class IsiSearchTag(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx

        super().__init__(data, per_page=10)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*self.per_page) + 1
        len_data = len(self.entries)
        lagu = "\n".join([cr for cr in fields])
        embed = Embed(title=f"Antrian Musik:",
                      description = f"{lagu}",
                      colour=self.ctx.author.colour)
        
        # for name, value in fields:
        #     embed.add_field(name=name,value=value,inline=False)

        embed.set_footer(text=f"{offset:,} - {min(len_data, offset + self.per_page - 1):,} dari {len_data:,} lagu.")


        return embed

    async def format_page(self, menu, entries):
        fields = []
        
        for entry in entries:
            fields.append(entry)

        return await self.write_page(menu, fields)

class Music(Cog):
    def __init__(self, bot):
        self.bot = bot 
        self.YDL_OPTIONS = {
            'audioquality': 5,
            'format': 'opus/bestaudio/best',
            'outtmpl': '{}',
            'restrictfilenames': True,
            'flatplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': True,
            # 'logtostderr': False,
            "extractaudio": True,
            # "audioformat": "opus",
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            # bind to ipv4 since ipv6 addresses cause issues sometimes
            'source_address': '0.0.0.0',
            'postprocessors': [{  # Extract audio using ffmpeg
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'opus',
            }]
        }
        # self.YDL_OPTIONS = {
        #     'format': 'opus/bestaudio/best',
        #     # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
        #     'postprocessors': [{  # Extract audio using ffmpeg
        #         'key': 'FFmpegExtractAudio',
        #         'preferredcodec': 'opus',
        #     }]
        # }
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        # self.FFMPEG_OPTIONS = {'options' : '-vn'}
        self.song_queue = {}
        self.shuffle = {}
        self.repeat = {}
        self.repeat_one = {}
        self.np = {}
        self.playing = {}
        self.timer = {}
        self.np_id = {}
        self.fu = {}
        self.volume = {}
        self.position = {}
        self.np_display = {}
        self.pause = {}
        self.np_queue = {}
    async def check_queue(self, ctx):
        try:
            if len(self.song_queue[ctx.guild.id]) > 0:
                try:
                    if self.repeat[ctx.guild.id] is True:
                        self.song_queue[ctx.guild.id].append(self.np[ctx.guild.id])
                    elif self.repeat_one[ctx.guild.id] is True:
                        self.song_queue[ctx.guild.id].insert(0, self.np[ctx.guild.id])
                        
                except KeyError:
                    self.repeat[ctx.guild.id] = False
                    self.repeat_one[ctx.guild.id] = False
                await self.play_song(ctx, self.song_queue[ctx.guild.id][0])
                self.song_queue[ctx.guild.id].pop(0)
                try:
                    if self.shuffle[ctx.guild.id] is True and len(self.song_queue[ctx.guild.id]) > 1:
                        random.shuffle(self.song_queue[ctx.guild.id])
                except KeyError:
                    self.shuffle[ctx.guild.id] = False
            else:
                self.fu[ctx.guild.id] = False
                self.timer[ctx.guild.id] = 0
                try:
                    if self.repeat[ctx.guild.id] is True or self.repeat_one[ctx.guild.id] is True:
                        self.playing[ctx.guild.id] = True
                        self.song_queue[ctx.guild.id] = [self.np[ctx.guild.id]]
                        await self.play_song(ctx, self.song_queue[ctx.guild.id][0])
                        self.song_queue[ctx.guild.id].pop(0)
                    else:
                        while True:
                            if self.fu[ctx.guild.id] is True:
                                break
                            await asyncio.sleep(10)
                            self.timer[ctx.guild.id] += 10
                            if self.timer[ctx.guild.id] >= 60:
                                if self.playing[ctx.guild.id] is True:
                                    return await self.passive_leave(ctx.guild.id, ctx.voice_client)
                    
                except KeyError:
                        while True:
                            if self.fu[ctx.guild.id] is True:
                                break
                            await asyncio.sleep(10)
                            self.timer[ctx.guild.id] += 10
                            if self.timer[ctx.guild.id] >= 60 and self.playing[ctx.guild.id] is True:
                                return await self.passive_leave(ctx.guild.id, ctx.voice_client)
        except KeyError:
            try:
                if self.repeat[ctx.guild.id] is True or self.repat_one[ctx.guild.id] is True:
                    self.song_queue[ctx.guild.id] = [self.np[ctx.guild.id]]
                    await self.play_song(ctx, self.song_queue[ctx.guild.id][0])
                    self.song_queue[ctx.guild.id].pop(0)
                else:
                    while True:
                        if self.fu[ctx.guild.id] is True:
                            break
                        await asyncio.sleep(10)
                        self.timer[ctx.guild.id] += 10
                        if self.timer[ctx.guild.id] >= 60 and self.playing[ctx.guild.id] is True:
                            return await self.passive_leave(ctx.guild.id, ctx.voice_client)
            except KeyError:
                while True:
                    if self.fu[ctx.guild.id] is True:
                        break
                    await asyncio.sleep(10)
                    self.timer[ctx.guild.id] += 10
                    if self.timer[ctx.guild.id] >= 60 and self.playing[ctx.guild.id]:
                        return await self.passive_leave(ctx.guild.id, ctx.voice_client)
                
    async def poll_song(self, user, channel):
        poll = Embed(title=f"Vote to Skip Song by - {user.name}#{user.discriminator}", description="**80% of the voice channel must vote to skip for it to pass.**", colour= Colour.blue())
        poll.add_field(name="Skip", value=":white_check_mark:")
        poll.add_field(name="Stay", value=":no_entry_sign:")
        poll.set_footer(text="Voting ends in 5 seconds.")

        poll_msg = await channel.send(embed=poll) # only returns temporary message, we need to get the cached message to get the reactions
        poll_id = poll_msg.id

        await poll_msg.add_reaction(u"\u2705") # yes
        await poll_msg.add_reaction(u"\U0001F6AB") # no
        
        await asyncio.sleep(5) # 5 seconds to vote

        poll_msg = await channel.fetch_message(poll_id)
        
        votes = {u"\u2705": 0, u"\U0001F6AB": 0}
        reacted = []

        for reaction in poll_msg.reactions:
            if reaction.emoji in [u"\u2705", u"\U0001F6AB"]:
                async for member in reaction.users():
                    if member.voice.channel.id == channel.guild.voice_client.channel.id and member.id not in reacted and not member.bot:
                        if member.id in self.bot.owner_ids:
                            votes[reaction.emoji] += 10
                        else:
                            votes[reaction.emoji] += 1
                        reacted.append(member.id)

        skip = False

        if votes[u"\u2705"] > 0:
            if votes[u"\U0001F6AB"] == 0 or votes[u"\u2705"] / (votes[u"\u2705"] + votes[u"\U0001F6AB"]) > 0.79: # 80% or higher
                skip = True
                embed = Embed(title="Skip Successful", description="***Voting to skip the current song was succesful, skipping now.***", colour= Colour.green())

        if not skip:
            embed = Embed(title="Skip Failed", description="*Voting to skip the current song has failed.*\n\n**Voting failed, the vote requires at least 80% of the members to skip.**", colour= Colour.red())

        embed.set_footer(text="Voting has ended.")

        await poll_msg.clear_reactions()
        await poll_msg.edit(embed= embed, delete_after= 5)
        return skip, poll_msg
    
    async def choose_track(self, ctx, query):
        def _check(r, u):
            return (
                r.emoji in OPTIONS.keys()
                and u == ctx.author
                and r.message.id == msg.id
            )
            
        info = YoutubeSearch(query, max_results=5).to_dict()
        embed = Embed(
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
        embed.set_footer(text=f"Invoked by {ctx.author.display_name}", icon_url=ctx.author.avatar.url)

        msg = await ctx.send(embed=embed)
        for emoji in list(OPTIONS.keys())[:min(len(info), len(OPTIONS))]:
            await msg.add_reaction(emoji)

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=15.0, check=_check)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.message.delete()
            return None
        else:
            await msg.delete()
            track = info[OPTIONS[reaction.emoji]]
            ydl_format = self.YDL_OPTIONS.copy()
            loop = self.bot.loop or asyncio.get_event_loop()
            with YoutubeDL(ydl_format) as ydl:
                try: 
                    lagu = await loop.run_in_executor(None, lambda: ydl.extract_info(f"{'https://www.youtube.com' + track['url_suffix']}", download=False))
                    lagu = await loop.run_in_executor(None, lambda: ydl.sanitize_info(lagu))
                except Exception: 
                    return None
            return {'source': lagu['url'], 'title': lagu['title'], 'duration' : lagu['duration'], 'thumbnail' : lagu['thumbnail']}

    async def link_handler(self, ctx, song):
        if "youtube.com/playlist?" in song:
            if not ctx.guild.id == 605057520955818010:
                return False
            msg = await ctx.send("Ditemukan suatu playlist, mohon tunggu sampai seluruh playlist dimasukkan dalam antrian")
        ydl_format = self.YDL_OPTIONS.copy()
        loop = self.bot.loop or asyncio.get_event_loop()
        with YoutubeDL(ydl_format) as ydl:
            try: 
                info = await loop.run_in_executor(None, lambda: ydl.extract_info(song, download=False))
                info = await loop.run_in_executor(None, lambda: ydl.sanitize_info(info))
            except Exception: 
                return None
        if not info['webpage_url_basename'] == "playlist":
            return {'source': info['url'], 'title': info['title'], 'duration' : info['duration'], 'thumbnail' : info['thumbnail']}
        else:
            
            entries = []
            for entry in info['entries']:
                entries.append([entry['title'], entry['url'], entry['duration'], entry['thumbnail']])

            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                try:
                    self.song_queue[ctx.guild.id] += entries
                except KeyError:
                    self.song_queue[ctx.guild.id] = entries
            else:
                await self.play_song(ctx, entries[0])
                entries.pop(0)
                try:
                    self.song_queue[ctx.guild.id] += entries
                except KeyError:
                    self.song_queue[ctx.guild.id] = entries
            await msg.delete()
            await ctx.send(f"{len(entries)} lagu dari {info['title']} berhasil ditambahkan")
            return "playlist"
            
    async def stopwatch_song(self, voice_client, guild_id, durasi):
        np_id = self.np_id[guild_id][0]
        posisi = self.position[guild_id]
        np = self.np[guild_id]
        while time() - posisi < int(durasi):
            await asyncio.sleep(2)
            if self.playing[guild_id] is False or voice_client.is_paused() or np_id != self.np_id[guild_id][0] or np != self.np[guild_id]:
                break
            embed = await self.passive_np(voice_client, guild_id, time() - self.position[guild_id], self.np_display[guild_id])
            np_msg = await self.bot.get_channel(self.np_id[guild_id][1]).fetch_message(self.np_id[guild_id][0])
            await np_msg.edit(embed=embed)

    async def download_image(self, url, file_path, file_name):
        full_path = file_path + file_name + '.jpg'
        loop = self.bot.loop or asyncio.get_event_loop()
        with open(full_path, 'wb') as out:
            r = await loop.run_in_executor(None, lambda: urlp.request('GET', url, preload_content=False))
            shutil.copyfileobj(r, out)
            r.release_conn()
    def most_common_used_color(self, img):
        # Get width and height of Image
        width, height = img.size

        # Initialize Variable
        r_total = 0
        g_total = 0
        b_total = 0

        count = 0

        # Iterate through each pixel
        for x in range(0, width):
            for y in range(0, height):
                # r,g,b value of pixel
                r, g, b = img.getpixel((x, y))

                r_total += r
                g_total += g
                b_total += b
                count += 1

        return (round(r_total/count), round(g_total/count), round(b_total/count))
    async def play_song(self, ctx, song, volume= 0.5):
        # try:
        #     ctx.voice_client.play(PCMVolumeTransformer(FFmpegOpusAudio.from_probe(song[1], **self.FFMPEG_OPTIONS)), after=lambda error: self.bot.loop.create_task(self.check_queue(ctx)))
        # except Exception:
        try:
            if isinstance(self.volume[ctx.guild.id], float):
                volume = self.volume[ctx.guild.id]
        except Exception:
            pass
        ctx.voice_client.play(PCMVolumeTransformer(FFmpegPCMAudio(song[1], **self.FFMPEG_OPTIONS), volume=volume), after=lambda error: self.bot.loop.create_task(self.check_queue(ctx)))
        self.position[ctx.guild.id] = time()
        try:
            self.volume[ctx.guild.id] = ctx.voice_client.source.volume
        except AttributeError:
            self.volume[ctx.guild.id] = volume
        self.np[ctx.guild.id] = song
        self.playing[ctx.guild.id] = True
        self.fu[ctx.guild.id] = True
        try:
            np_id = self.np_id[ctx.guild.id][0]
            if isinstance(np_id, int):
                embed = await self.passive_np(ctx.voice_client, ctx.guild.id)
                np_msg = await self.bot.get_channel(self.np_id[ctx.guild.id][1]).fetch_message(np_id)
                await np_msg.edit(embed=embed)
                await self.stopwatch_song(ctx.voice_client, ctx.guild.id, song[2])
        except Exception:
            return

    @command(name="join")
    async def join(self, ctx):
        if ctx.author.voice is None:
            return await ctx.send("Connect dulu ke voice channel ya kak")
        try:
            if ctx.voice_client.is_playing() and ctx.author.voice.channel.id != ctx.voice_client.channel.id:
                await ctx.send("Ihh nanti aja ya kak, Nadeshiko lagi nyanyi")
                return 69
        except Exception:
            pass
        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect()

        await ctx.author.voice.channel.connect()
        

    @command(name="leave", aliases=["disconnect"])
    async def leave(self, ctx):
        """Gunakan command ini untuk mereset cog musik apabila terjadi bug
        """
        await self.passive_leave(ctx.guild.id, ctx.voice_client, ctx.message.channel)

    async def passive_leave(self,guild_id, voice_client, channel = "Takda"):
        if not voice_client is None:
            self.song_queue[guild_id] = []
            self.shuffle[guild_id] = False
            self.repeat[guild_id] = False
            self.repeat_one[guild_id] = False
            self.np[guild_id] = []
            self.np_id[guild_id] = []
            self.playing[guild_id] = False
            self.fu[guild_id] = False
            self.timer[guild_id] = 0
            self.volume[guild_id] = 0.5
            self.position[guild_id] = False
            self.np_display[guild_id] = []
            self.pause[guild_id] = 0
            self.np_queue[guild_id] = []
            return await voice_client.disconnect()
        if not channel == "Takda":
            await channel.send("Nadeshiko tidak sedang berada dalam voice channel")
    
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
            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                try:
                    queue_len = len(self.song_queue[ctx.guild.id])
                    self.song_queue[ctx.guild.id].append([result['title'], result['source'], result['duration'], result['thumbnail']])
                    return await ctx.send(f"**{result['title']}** telah ditambahkan dalam antrian posisi: {queue_len+1}.")
                except KeyError:
                    self.song_queue[ctx.guild.id] = [[result['title'], result['source'], result['duration'], result['thumbnail']]]
                    return await ctx.send(f"**{result['title']}** telah ditambahkan dalam antrian posisi: 1.")
        
            else:
                await self.play_song(ctx, [result['title'], result['source'], result['duration'], result['thumbnail']])
                await ctx.send(f"Now playing: **{result['title']}**")
            #     return await ctx.send("Sorry, I can only queue up to 10 songs, please wait for the current song to finish.")
        except KeyError:
            await self.play_song(ctx, [result['title'], result['source'], result['duration'], result['thumbnail']])
            await ctx.send(f"Now playing: **{result['title']}**")

    @command(name="queue", aliases=["q"])
    async def queue(self, ctx): # display the current guilds queue
        """Menunjukkan Antrian Lagu
        """
        try:
            if len(self.song_queue[ctx.guild.id]) == 0:
                return await ctx.send("Tidak ada lagu dalam antrian")
        except KeyError:
            return await ctx.send("Tidak ada lagu dalam antrian")
        queue = []
        for i, title in enumerate(self.song_queue[ctx.guild.id]):
            
                
            queue.append(f"**{i+1:3d}**)  {title[0]} ({format_durasi(title[2])})")
        menu = MenuPages(source=IsiSearchTag(ctx, queue),
                         clear_reactions_after=True,
                         timeout=60.0)# bisa ditambah clear_reaction_after=True
        await menu.start(ctx)

    @command(name="skip")
    async def skip(self, ctx):
        if ctx.voice_client is None:
            return await ctx.send("Dih orang Nadeshiko ga lagi nyanyi juga")

        if ctx.author.voice is None:
            return await ctx.send("Masuk ke voice channel dulu ya kak")

        if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
            return await ctx.send("Nadeshiko ga lagi nyanyi buat kakak")

        skip, poll_msg = await self.poll_song(ctx.author, ctx.channel)
        if skip:
            ctx.voice_client.stop()
        await asyncio.sleep(4)
        await poll_msg.delete()
            
    @command(name="skipto")
    async def skipto(self,ctx, number):
        """Memutar lagu pada posisi antrian yang dipilih

        Args:
            number (int): Nomor antrian yang ingin diputar
        """
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
        
        skip, poll_msg = await self.poll_song(ctx.author, ctx.channel)
        if skip:
            self.song_queue[ctx.guild.id].insert(0, self.song_queue[ctx.guild.id][number-1])
            self.song_queue[ctx.guild.id].pop(number)
            ctx.voice_client.stop()
        await asyncio.sleep(4)
        await poll_msg.delete()

    @command(name="pause")
    async def pause(self, ctx):
        if ctx.voice_client.is_paused():
            return await ctx.send("Nadeshiko ga lagi nyanyi kok kak")

        ctx.voice_client.pause()
        self.pause[ctx.guild.id] = time()
        await ctx.send("Lagu telah dijeda", delete_after= 4)

    @command(name="resume")
    async def resume(self, ctx):
        if ctx.voice_client is None:
            return await ctx.send("Joinin aku dulu kak")

        if  ctx.voice_client.is_playing():
            return await ctx.send("Berisik ih, lagi nyanyi juga")
        try:
            if isinstance(self.np_id[ctx.guild.id][0], int):
                self.np[ctx.guild.id][2] += time() - self.pause[ctx.guild.id]
                await self.stopwatch_song(ctx.voice_client, ctx.guild.id, self.np[ctx.guild.id][2])
        except Exception:
            pass
        ctx.voice_client.resume()
        await ctx.send("Okee, ku lanjut nyanyi yaa", delete_after= 4)
    
    @command(name="np")
    async def np(self,ctx):
        if not self.np[ctx.guild.id] == []:
            embed = await self.passive_np(ctx.voice_client, ctx.guild.id)
            msg = await ctx.send(embed=embed)
            self.np_id[ctx.guild.id] = [msg.id, msg.channel.id]
            for emoji in list(BUTTON.keys()):
                await msg.add_reaction(emoji)
            await self.stopwatch_song(ctx.voice_client, ctx.guild.id,self.np[ctx.guild.id][2])
        else:
            await ctx.send("Nadeshiko sedang tidak menyanyi")
    
    async def passive_np(self, voice_client, guild_id, posisi=0, rgb:list = []):
        vol_lv = []
        try:
            vol = round(voice_client.source.volume * 10)
        except AttributeError:
            vol = round(self.volume[guild_id] * 10)
        for i in range(vol):
            vol_lv.append(BAR[0])
        for i in range(10-vol):
            vol_lv.append(BAR[1])
        
        if rgb == []:
            file_name = "Music-Cover" + str(random.randint(1, 101))
            loop = self.bot.loop or asyncio.get_event_loop()
            await self.download_image(self.np[guild_id][3], "./data/temp-image/", file_name)
        
            # Read Image
            img = Image.open(f"./data/temp-image/{file_name}.jpg")
            # Convert Image into RGB
            img = img.convert('RGB')
            # call function
            red, green, blue = await loop.run_in_executor(None, lambda: self.most_common_used_color(img))
            rgb = [red, green, blue]
            self.np_display[guild_id] = rgb
            os.remove(f"./data/temp-image/{file_name}.jpg")
            
        # ━ ⬤ ─
        # progress_bar = ["━━━━━━⬤─────────────"] #20 karakter
        bagian = self.np[guild_id][2] / 24
        terisi = round(posisi / bagian)
        sisa = 24 - (terisi + 1)
        bar_form = []
        if not terisi == 0:
            for n in range(terisi-1):
                bar_form.append("━")
        bar_form.append("⬤")
        if not sisa == 0:
            for n in range(sisa-1):
                bar_form.append("─")
        embed = Embed(
            title= f"Now playing: **{self.np[guild_id][0]}**",
            description= f"Volume : {''.join(vol_lv)} 『{round(self.volume[guild_id] * 100)}』\n{format_durasi(posisi)} {''.join(bar_form)} {format_durasi(self.np[guild_id][2])}",
            colour= Colour.from_rgb(rgb[0], rgb[1], rgb[2])
        )
        embed.set_image(url=self.np[guild_id][3])
        return embed
        
    
    @command(name="shuffle")
    async def shuffle(self, ctx):
        try:
            if self.shuffle[ctx.guild.id] is False:
                self.shuffle[ctx.guild.id] = True
                await ctx.send("Mode shuffle diaktifkan", delete_after= 4)
            else:
                self.shuffle[ctx.guild.id] = False
                await ctx.send("Mode shuffle dimatikan", delete_after= 4)
        except KeyError:
            self.shuffle[ctx.guild.id] = True
            await ctx.send("Mode shuffle diaktifkan", delete_after= 4)
            
    @command(name="repeat")
    async def repeat(self, ctx):
        await self.passive_repeat(ctx.guild.id, ctx.message.channel)
            
    async def passive_repeat(self, guild_id, channel):
        try:
            if self.repeat[guild_id] is False:
                self.repeat[guild_id] = True
                self.repeat_one[guild_id] = False
                await channel.send("Mode repeat diaktifkan", delete_after= 4)
            else:
                self.repeat[guild_id] = False
                await channel.send("Mode repeat dimatikan", delete_after= 4)
        except KeyError:
            self.repeat[guild_id] = True
            self.repeat_one[guild_id] = False
            await channel.send("Mode repeat diaktifkan", delete_after= 4)
    
    @command(name="repeatone")
    async def repeat_one(self,ctx):
        """Memutar ulang lagu yang sedang berputar terus menerus
        """
        await self.passive_repeat_one(ctx.guild.id, ctx.message.channel)
        
    async def passive_repeat_one(self, guild_id, channel):
        try:
            if self.repeat_one[guild_id] is False:
                self.repeat[guild_id] = False
                self.repeat_one[guild_id] = True
                await channel.send("Mode repeat one diaktifkan", delete_after= 4)
            else:
                self.repeat_one[guild_id] = False
                await channel.send("Mode repeat one dimatikan", delete_after= 4)
        except KeyError:
            self.repeat_one[guild_id] = True
            self.repeat[guild_id] = False
            await channel.send("Mode repeat one diaktifkan", delete_after= 4)
    
    @command(name="remove")
    async def remove(self, ctx, number):
        if not number.isnumeric():
            return await ctx.send("Tolong masukkan nilai angka bulat ya kak")
        number = int(number)
        if number <= len(self.song_queue[ctx.guild.id]):
            await ctx.send(f"**{self.song_queue[ctx.guild.id][number-1][0]}** telah dihapus dari antrian")
            self.song_queue[ctx.guild.id].pop(number-1)
    
    @command(name="volume", aliases=["vol"])
    async def vol_control(self,ctx, *, number):
        """Kontrol volume dengan settingan maksimal 100

        Args:
            number (int): Nilai volume
        """
        if not number.isnumeric():
            return await ctx.send("Tolong masukkan nilai angka bulat ya kak")
        number = int(number)
        if number >= 100:
            number = 100
        ctx.voice_client.source.volume = number/100
        self.volume[ctx.guild.id] = number/100
        await ctx.send("Oke, kusesuaiin ya volumenya~", delete_after= 4)
        
         
    @Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        
        
        
        # if event is triggered by the bot? return
        if member.bot and member.id != member.guild.me.id:
            return

        # when before.channel != None that means user isnt joining a channel
        if before.channel != None:
            voice = get(self.bot.voice_clients , channel__guild__id = before.channel.guild.id)

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
                        await self.passive_leave(member.guild.id, voice)
                        break
    # Button control on now playing embed
    @Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
        try:
            if user.voice.channel.id == reaction.message.guild.voice_client.channel.id:
                if reaction.message.id == self.np_id[reaction.message.guild.id][0]:
                    if not self.np == []:
                        return await self.button_control(reaction, user)
                        
            if reaction.message.id == self.np_queue[reaction.message.guild.id][1]:
                return await self.queue_control(reaction)
        except (AttributeError, KeyError, IndexError):
            return
                    
    @Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        if user.bot:
            return
        try:
            if user.voice.channel.id == reaction.message.guild.voice_client.channel.id:
                if reaction.message.id == self.np_id[reaction.message.guild.id][0]:
                    if not self.np == []:
                        await self.button_control(reaction, user)
                        
            if reaction.message.id == self.np_queue[reaction.message.guild.id][1]:
                return await self.queue_control(reaction)
        except (AttributeError, KeyError, IndexError):
            return
                    
    async def button_control(self, reaction, user):
        if reaction.emoji == "⏬":
            reaction.message.guild.voice_client.source.volume -= 0.05
            self.volume[reaction.message.guild.id] -= 0.05
            await reaction.message.channel.send("Oke, kukecilkan dulu ya volumenya~", delete_after= 4)
        elif reaction.emoji == "⏫":
            reaction.message.guild.voice_client.source.volume += 0.05
            self.volume[reaction.message.guild.id] += 0.05
            await reaction.message.channel.send("Oke, kubesarin dulu ya volumenya~", delete_after= 4)
        elif reaction.emoji == "⏮️":
            skip, poll_msg = await self.poll_song(user, reaction.message.channel)
            if skip:
                self.song_queue[reaction.message.guild.id].insert(0, self.song_queue[reaction.message.guild.id][len(self.song_queue[reaction.message.guild.id])-1])
                self.song_queue[reaction.message.guild.id].pop(len(self.song_queue[reaction.message.guild.id])-1)
                reaction.message.guild.voice_client.stop()
            await asyncio.sleep(4)
            await poll_msg.delete()
        elif reaction.emoji == "🎶":
            try:
                if len(self.song_queue[reaction.message.guild.id]) == 0:
                    return await reaction.message.channel.send("Tidak ada lagu dalam antrian")
            except KeyError:
                return await reaction.message.channel.send("Tidak ada lagu dalam antrian")
            self.np_queue[reaction.message.guild.id] = [1, 0]
            embed = self.passive_queue(reaction.message.guild.id, reaction.message.author)
            
            msg = await reaction.message.channel.send(embed=embed, delete_after=15)
            for emoji in BUTTON_QUEUE:
                await msg.add_reaction(emoji)
            self.np_queue[reaction.message.guild.id][1] = msg.id
        elif reaction.emoji == "🔀":
            try:
                if self.shuffle[reaction.message.guild.id] is False:
                    self.shuffle[reaction.message.guild.id] = True
                    msg = await reaction.message.channel.send("Mode shuffle diaktifkan")
                else:
                    self.shuffle[reaction.message.guild.id] = False
                    msg =await reaction.message.channel.send("Mode shuffle dimatikan")
            except KeyError:
                self.shuffle[reaction.message.guild.id] = True
                msg = await reaction.message.channel.send("Mode shuffle diaktifkan")
            await asyncio.sleep(4)
            await msg.delete()
        elif reaction.emoji == "⏯️":
            if reaction.message.guild.voice_client.is_paused():
                reaction.message.guild.voice_client.resume()
                try:
                    if isinstance(self.np_id[reaction.message.guild.id][0], int):
                        self.np[reaction.message.guild.id][2] += time() - self.pause[reaction.message.guild.id]
                        await self.stopwatch_song(reaction.message.guild.voice_client, reaction.message.guild.id, self.np[reaction.message.guild.id][2])
                except Exception:
                    pass
                msg = await reaction.message.channel.send("Lagu diteruskan")
            elif reaction.message.guild.voice_client.is_playing():
                self.pause[reaction.message.guild.id] = time()
                reaction.message.guild.voice_client.pause()
                msg = await reaction.message.channel.send("Lagu telah dijeda")
            await asyncio.sleep(5)
            await msg.delete()
        elif reaction.emoji == "🔁":
            await self.passive_repeat(reaction.message.guild.id, reaction.message.channel)
            # try:
            #     if self.repeat[reaction.message.guild.id] is False:
            #         self.repeat[reaction.message.guild.id] = True
            #         msg = await reaction.message.channel.send("Mode repeat diaktifkan")
            #     else:
            #         self.repeat[reaction.message.guild.id] = False
            #         msg = await reaction.message.channel.send("Mode repeat dimatikan")
            # except KeyError:
            #     self.repeat[reaction.message.guild.id] = True
            #     msg = await reaction.message.channel.send("Mode repeat diaktifkan")
            # await asyncio.sleep(4)
            # await msg.delete()
        elif reaction.emoji == "🔂":
            await self.passive_repeat_one(reaction.message.guild.id, reaction.message.channel)
        elif reaction.emoji == "⏭️":
            skip, poll_msg = await self.poll_song(user, reaction.message.channel)
            if skip:
                reaction.message.guild.voice_client.stop()
            await asyncio.sleep(4)
            await poll_msg.delete()
            
    async def queue_control(self, reaction):
        benar = False
        if reaction.emoji == "⏮️":
            self.np_queue[reaction.message.guild.id][0] = 1
            embed = self.passive_queue(reaction.message.guild.id, reaction.message.author)
            benar = True
        elif reaction.emoji == "◀️":
            self.np_queue[reaction.message.guild.id][0] -= 1
            embed = self.passive_queue(reaction.message.guild.id, reaction.message.author)
            benar = True
        elif reaction.emoji == "▶️":
            self.np_queue[reaction.message.guild.id][0] += 1
            embed = self.passive_queue(reaction.message.guild.id, reaction.message.author)
            benar = True
        elif reaction.emoji == "⏭️":
            self.np_queue[reaction.message.guild.id][0] = (len(self.song_queue) + 9) // 10
            embed = self.passive_queue(reaction.message.guild.id, reaction.message.author)
            benar = True
        if benar is True:
            msg = await reaction.message.channel.fetch_message(self.np_queue[reaction.message.guild.id][1])
            await msg.edit(embed= embed, delete_after= 15)
            
    def passive_queue(self, guild_id, user):
        queue = []
        for i, title in enumerate(self.song_queue[guild_id]):
            queue.append(f"**{i+1:3d}**)  {title[0]} ({format_durasi(title[2])})")
        if len(queue) <= self.np_queue[guild_id][0] * 10:
            self.np_queue[guild_id][0] = (len(queue) + 9) // 10
            queue = queue[(self.np_queue[guild_id][0] * 10) - 10:]
        else:
            queue = queue[(self.np_queue[guild_id][0] * 10) - 10 : self.np_queue[guild_id][0] * 10]
        lagu = "\n".join([cr for cr in queue])
        embed = Embed(title="Antrian Musik:",
                    description = f"{lagu}",
                    colour=user.colour)
        
        embed.set_footer(text=f"{(self.np_queue[guild_id][0] * 10) - 9:,} - {self.np_queue[guild_id][0] * 10:,} dari {len(self.song_queue[guild_id]):,} lagu.")
        return embed

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("music")
            
def setup(bot):
    bot.add_cog(Music(bot))