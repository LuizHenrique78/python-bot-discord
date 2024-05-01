import subprocess
import time

import discord
import youtube_dl
from discord.ext import commands


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_channel = None

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice and ctx.author.voice.channel:
            self.voice_channel = ctx.author.voice.channel
            await self.voice_channel.connect()
        else:
            await ctx.send("Você precisa estar em um canal de voz para que eu possa entrar!")

    # Comando para sair de um canal de voz
    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        else:
            await ctx.send("Eu não estou em um canal de voz!")

    # Comando para reproduzir uma música
    @commands.command()
    async def play(self, ctx, url):
        # Verifica se o autor da mensagem está em um canal de voz
        if ctx.author.voice and ctx.author.voice.channel:

            ydl_opts = {
                'format': 'bestaudio/best',
                'extractaudio': True,
                'audioformat': 'mp3',
                'noplaylist': True,
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                url2 = info['formats'][0]['url']

            # Chama youtube-dl com a flag --verbose
            command = f"youtube-dl --verbose -o - {url}"
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            output, error = process.communicate()

            # Reproduz o áudio do YouTube
            if not error:
                self.voice_channel.play(discord.FFmpegPCMAudio(output.strip(), executable='./ffmpeg/bin/ffmpeg'))
            else:
                await ctx.send("Ocorreu um erro ao tentar reproduzir o áudio do YouTube.")


def setup(bot):
    return bot.add_cog(Music(bot))
