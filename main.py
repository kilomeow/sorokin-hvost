# libs
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Bot, ReplyKeyboardMarkup, KeyboardButton
from telegram.utils.request import Request

import config

# creating bot

bot = Bot(config.data.token)
upd = Updater(bot=bot, use_context=True)
dp = upd.dispatcher

# logging
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

# start message
def hello(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Hello world!")

dp.add_handler(CommandHandler('start', hello))

def main():
    upd.start_polling()
    upd.idle()

if __name__ == '__main__':
    main()