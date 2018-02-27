#username:tltexambot
from telegram.ext import CommandHandler
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
import os 
import requests
import json
import bucket
from os.path import join,dirname
from dotenv import load_dotenv
from welcome import welcome_message
import telegram 
from telegram import KeyboardButton,ReplyKeyboardMarkup
from contacts import contacts_list
env=os.environ.get("ENV", "development")
if env=="development":
	dotenv_path=join(dirname(__file__), ".env")
	load_dotenv(dotenv_path,verbose=True)
TOKEN=os.environ.get("TOKEN")

updater=Updater(token=TOKEN)

dispatcher=updater.dispatcher
try:
	def start(bot, update):
		print(update.message.chat_id)
		contact_keyboard=KeyboardButton(text="Send my phone number",request_contact=True)
		custom_keyboard=[[contact_keyboard]]
		reply_markup=ReplyKeyboardMarkup(custom_keyboard)
		bot.send_message(chat_id=update.message.chat_id, text=welcome_message,reply_markup=reply_markup)

	def echo(bot, update):
		print(update.message.text)
		text="What do you mean by \""+update.message.text+"\" ?"
		payload={"message":{"username":update.message.from_user.username, "text":update.message.text}}
		url="https://hooks.zapier.com/hooks/catch/2980782/zgadqb"
		requests.post(url, data=json.dumps(payload))
		bot.send_message(chat_id=update.message.chat_id, text=text)

	def contact(bot, update):
		phone=update.message.contact.phone_number
		print(phone)
		text="Welcome, "+contacts_list[phone]+"!"
		reply_markup=telegram.ReplyKeyboardRemove()
		bot.send_message(chat_id=update.message.chat_id, text=text, reply_markup=reply_markup)

	def voice(bot, update):
		voice_id=update.message.voice.file_id
		voice_file=bot.get_file(voice_id)
		voice_path="/tmp/voice-"+voice_id+".ogg"
		print(voice_path)
		voice_file.download(voice_path)
		s3_url=bucket.upload_s3(voice_path, voice_id)
		text="Voice received"
		payload={"message":{"username":update.message.from_user.id, "text":s3_url}}
		url="https://hooks.zapier.com/hooks/catch/2980782/zgadqb"
		requests.post(url, data=json.dumps(payload))
		bot.send_message(chat_id=update.message.chat_id, text=text)

	echo_handler = MessageHandler(Filters.text, echo)
	dispatcher.add_handler(echo_handler)

	contact_handler = MessageHandler(Filters.contact, contact)
	dispatcher.add_handler(contact_handler)

	start_handler = CommandHandler('start', start)
	dispatcher.add_handler(start_handler)

	voice_handler = MessageHandler(Filters.voice, voice)
	dispatcher.add_handler(voice_handler)

	if env=="production":
		PORT=int(os.environ.get("PORT"))
		HEROKU_APP=os.environ.get("HEROKU_APP")
		updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
		updater.bot.set_webhook("https://"+HEROKU_APP+".herokuapp.com/"+TOKEN)
		updater.idle()
	else:
		updater.start_polling()
except Exception as e:
	print(e)
