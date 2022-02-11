from os import system
# from nltk import download

# download('punkt')
system("sudo python -m spacy download en")

from features.bot_main import bot

VERSION = "0.0.3"

bot.run(VERSION);
