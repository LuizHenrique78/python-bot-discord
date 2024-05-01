import discord
from aiohttp import web
from discord.ext import commands
import os
from commands.basic import Basic
from environment_custom import EnvConfigCustom

prefix = "!"
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
bot = commands.Bot(command_prefix=prefix, intents=intents)
github_webhook_instance = Basic(bot)


async def load_commands():
    for file in os.listdir("./commands"):
        if file.endswith(".py"):
            extension_name = file[:-3]
            await bot.load_extension(f"commands.{extension_name}")


@bot.event
async def on_ready():
    await load_commands()
    print(f'Bot está pronto: {bot.user.name}')


bot.run(EnvConfigCustom().discord_bot_token)
