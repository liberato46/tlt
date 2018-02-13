#username:tltexambot
from telegram.ext import CommandHandler
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
import os 
from os.path import join,dirname
from dotenv import load_dotenv
from welcome import welcome_message
import telegram 
from telegram import KeyboardButton,ReplyKeyboardMarkup
from contacts import contacts_list

dotenv_path=join(dirname(__file__), ".env")
load_dotenv(dotenv_path,verbose=True)
token=os.environ.get("TOKEN")

updater = Updater(token=token)

dispatcher = updater.dispatcher
try:
	def start(bot, update):
		print(update.message.chat_id)
		contact_keyboard=KeyboardButton(text="Send my phone number",request_contact=True)
		custom_keyboard=[[contact_keyboard]]
		reply_markup=ReplyKeyboardMarkup(custom_keyboard)
		bot.send_message(chat_id=update.message.chat_id, text=welcome_message,reply_markup=reply_markup)

	def echo(bot, update):
		text="What do you mean by \""+update.message.text+"\" ?"
		bot.send_message(chat_id=update.message.chat_id, text=text)

	def contact(bot, update):
		phone=update.message.contact.phone_number
		text="Welcome, "+contacts_list[phone]+"!"
		reply_markup=telegram.ReplyKeyboardRemove()
		bot.send_message(chat_id=update.message.chat_id, text=text, reply_markup=reply_markup)

	def voice(bot, update):
		voice_file=bot.get_file(update.message.voice.file_id)
		voice_file.download("voice.ogg")
		text="Voice received"
		bot.send_message(chat_id=update.message.chat_id, text=text)

	echo_handler = MessageHandler(Filters.text, echo)
	dispatcher.add_handler(echo_handler)

	contact_handler = MessageHandler(Filters.contact, contact)
	dispatcher.add_handler(contact_handler)

	start_handler = CommandHandler('start', start)
	dispatcher.add_handler(start_handler)

	voice_handler = MessageHandler(Filters.voice, voice)
	dispatcher.add_handler(voice_handler)

	updater.start_polling()
except Exception as e:
	print(e)
