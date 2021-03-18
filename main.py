# libs
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Bot, ReplyKeyboardMarkup, KeyboardButton
from telegram.utils.request import Request

import time

import config

# creating bots

Sq = Bot(config.data.tokens["squirrel"])
Sq_upd = Updater(bot=Sq, use_context=True)
Sq_dp = Sq_upd.dispatcher

Fl = Bot(config.data.tokens["floppa"])
Fl_upd = Updater(bot=Fl, use_context=True)
Fl_dp = Fl_upd.dispatcher

# logging
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


# start message
def hello(update, context):
    Sq.send_message(chat_id=update.effective_chat.id,
                             text="Здарова я Белка Манагерка")
    time.sleep(0.4)
    Sq.send_message(chat_id=update.effective_chat.id,
                             text="А это наш новый коллега Флоппа")
    time.sleep(0.8)
    Fl.send_message(chat_id=update.effective_chat.id,
                             text="Хало это я Флоппа")

Sq_dp.add_handler(CommandHandler('start', hello))


def main():
    Sq_upd.start_polling()
    Fl_upd.start_polling()

if __name__ == '__main__':
    main()