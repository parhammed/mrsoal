from os.path import abspath
import locale

from classes.bot import Bot

locale.setlocale(locale.LC_ALL, "fa_IR")
bot = Bot(abspath("settings.json"))


if __name__ == '__main__':
    bot.run(bot.settings["token"])
