from features.bot_main import bot

VERSION = "0.0.3"
def main():
    bot.run(VERSION)

def test_main():
    bot.run(VERSION)

if __name__ == '__main__':
    main()
