#username:tltexambot
from telegram.ext import CommandHandler
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
import os 
import requests
import json
import bucket
import datetime
import airtable_wrapper

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
	def sound(bot, update):
		bot.send_voice(chat_id=update.message.chat_id, voice=open("tlt_audios/TLT_v5_1_question1_v1.ogg", "rb"))

	def start(bot, update):
		print(update.message.chat_id)
		contact_keyboard=KeyboardButton(text="Send my phone number",request_contact=True)
		custom_keyboard=[[contact_keyboard]]
		reply_markup=ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
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
		user_id=update.message.from_user.id
		text=airtable_wrapper.associate(phone, user_id)
		print(phone)
		reply_markup=telegram.ReplyKeyboardRemove()
		if text==True:
			bot.send_message(chat_id=update.message.chat_id, text="Phone found", reply_markup=reply_markup)
			bot.send_message(chat_id=update.message.chat_id, text="(1) Click on \"Play\" to listen to the test instructions")
			bot.send_audio(chat_id=update.message.chat_id, audio=open("tlt_audios/TLT_v5.1_intro_v1.mp3", "rb"))
			bot.send_message(chat_id=update.message.chat_id, text="(2) Now click on \"Play\" to listen to Question 1")
			bot.send_audio(chat_id=update.message.chat_id, audio=open("tlt_audios/TLT_v5.1_question1_v1.mp3", "rb"))
			bot.send_message(chat_id=update.message.chat_id, text="(3) Now click on \"Record\" to record your answer to Question 1")
		else:
			bot.send_message(chat_id=update.message.chat_id, text="Phone NOT found", reply_markup=reply_markup)

	def voice(bot, update):
		question=airtable_wrapper.get_question(update.message.from_user.id)
		if question >=6:
			bot.send_message(chat_id=update.message.chat_id, text="You have already finished your text.")
		else: 
			voice_id=update.message.voice.file_id
			voice_file=bot.get_file(voice_id)
			voice_path="/tmp/voice-"+voice_id+".ogg"
			print(voice_path)
			voice_file.download(voice_path)
			s3_url=bucket.upload_s3(voice_path, voice_id)
			question_answered=airtable_wrapper.save_response(update.message.from_user.id, s3_url)
			bot.send_message(chat_id=update.message.chat_id, text="question "+str(question_answered)+" answered")
			if question_answered+1>6:
				bot.send_message(chat_id=update.message.chat_id, text="This is the end of your TLT test.")
			else: 
				bot.send_audio(chat_id=update.message.chat_id, audio=open("tlt_audios/TLT_v5.1_question"+str(question_answered+1)+"_v1.mp3", "rb"))
				bot.send_message(chat_id=update.message.chat_id, text="(3) Now click on \"Record\" to record your answer to Question "+str(question_answered+1))


	echo_handler = MessageHandler(Filters.text, echo)
	dispatcher.add_handler(echo_handler)

	contact_handler = MessageHandler(Filters.contact, contact)
	dispatcher.add_handler(contact_handler)

	start_handler = CommandHandler('start', start)
	dispatcher.add_handler(start_handler)

	voice_handler = MessageHandler(Filters.voice, voice)
	dispatcher.add_handler(voice_handler)

	sound_handler = CommandHandler('sound', sound)
	dispatcher.add_handler(sound_handler)

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
