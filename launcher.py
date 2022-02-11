from os import system
# from nltk import download

# download('punkt')
system("python -m spacy link en_core_web_md en")

from features.bot_main import bot

VERSION = "0.0.3"

bot.run(VERSION);
