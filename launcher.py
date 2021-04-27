from os import system

system("python -m pip install -U git+https://github.com/Rapptz/discord-ext-menus")

from features.bot_main import bot

VERSION = "0.0.2"

bot.run(VERSION);