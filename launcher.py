from features.bot_main import bot
from os import system

system('python -m pip install saucenao-api==2.3.1')

VERSION = "0.0.3"

bot.run(VERSION);
