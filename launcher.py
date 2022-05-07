from features.bot_main import bot
from os import system

system('python -m pip install hentai==3.2.10 --install-option="--no-deps"')

VERSION = "0.0.3"

bot.run(VERSION);
