# from os import system
# system('python -m pip uninstall discord.py&&y')
# system('python -m pip install saucenao-api==2.3.1')


from features.bot_main import bot
from features.cloud.keep_alive import keep_alive

VERSION = "0.0.3"
def main():
    # keep_alive()
    bot.run(VERSION);

if __name__ == '__main__':
    main();