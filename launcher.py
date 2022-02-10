from os import system
from nltk import download

download('punkt')
system("python -m pip install -U git+https://github.com/Rapptz/discord-ext-menus")
system("python -m pip install torch torchvision torchaudio")

from features.bot_main import bot

VERSION = "0.0.3"

bot.run(VERSION);
