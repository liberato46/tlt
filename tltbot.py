#username:tltexambot
from telegram.ext import CommandHandler
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
import os 
from os.path import join,dirname
from dotenv import load_dotenv

dotenv_path=join(dirname(__file__), ".env")
load_dotenv(dotenv_path,verbose=True)
token=os.environ.get("TOKEN")

updater = Updater(token=token)

dispatcher = updater.dispatcher

def start(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="Hey, man, I'm a chat bot. What do you want?")

def echo(bot, update):
	text="What do you mean by \""+update.message.text+"\" ?"
	bot.send_message(chat_id=update.message.chat_id, text=text)

echo_handler = MessageHandler(Filters.text, echo)
dispatcher.add_handler(echo_handler)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

updater.start_polling()
