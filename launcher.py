from os import getenv
# system('python -m pip uninstall discord.py&&y')
# system('python -m pip install saucenao-api==2.3.1')

from features.bot_main import bot


VERSION = "0.0.3"
DESKTOP_KEY = getenv("DESKTOP_KEY")
def main():
    if not DESKTOP_KEY == 'benar':
        from features.cloud.keep_alive import keep_alive
        keep_alive()
    bot.run(VERSION);

if __name__ == '__main__':
    main();
