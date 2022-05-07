from os import system
# system('python -m pip uninstall discord.py&&y')
system('python -m pip install saucenao-api==2.3.1 && Y')


from features.bot_main import bot

VERSION = "0.0.3"

bot.run(VERSION);
