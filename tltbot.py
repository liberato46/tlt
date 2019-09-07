#username:tltexambot
from telegram.ext import CommandHandler
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters,CallbackQueryHandler
import os 
import requests
import json
import bucket
import datetime
import airtable_wrapper
import time

from os.path import join,dirname
from dotenv import load_dotenv
from welcome import welcome_message
import telegram 
from telegram import KeyboardButton,ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from contacts import contacts_list
env=os.environ.get("ENV", "development")
if env=="development":
	dotenv_path=join(dirname(__file__), ".env")
	load_dotenv(dotenv_path,verbose=True)
TOKEN=os.environ.get("TOKEN")

updater=Updater(token=TOKEN)

dispatcher=updater.dispatcher
try:
	def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
	    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
	    if header_buttons:
	        menu.insert(0, header_buttons)
	    if footer_buttons:
	        menu.append(footer_buttons)
	    return menu

	def sound(bot, update):
		bot.send_voice(chat_id=update.message.chat_id, voice=open("tlt_audios/TLT_v5_1_question1_v1.ogg", "rb"))

	def start(bot, update):
		print(update.message.chat_id)
		contact_keyboard=KeyboardButton(text="Send my phone number",request_contact=True)
		custom_keyboard=[[contact_keyboard]]
		reply_markup=ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
		bot.send_audio(chat_id=update.message.chat_id, audio=open("tlt_audios/TLT_v5_1_welcome_v1.mp3", "rb"))
		bot.send_message(chat_id=update.message.chat_id, text=welcome_message,reply_markup=reply_markup, parse_mode=telegram.ParseMode.HTML)

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
			bot.send_message(chat_id=update.message.chat_id, text="📞 Phone found", reply_markup=reply_markup, parse_mode=telegram.ParseMode.HTML)
			
			button_list=[
				InlineKeyboardButton("Next", callback_data="next_button")
			]
			reply_markup=InlineKeyboardMarkup(build_menu(button_list, n_cols=1))

			bot.send_message(chat_id=update.message.chat_id, text=""" 🖐<b>BEFORE YOU START YOUR TEST:</b>

				1️⃣  Before you begin, make sure you have enough time to complete the test

				2️⃣  Take the test in a quiet location away from distractions and outside noise

				3️⃣  Make sure that you will not receive any calls or notifications during the test 

				4️⃣  Answer all questions naturally in a clear voice. 

				5️⃣  If you wish, bring your own headset and use it to block outside noise

				6️⃣  If you don’t know what to say in response to a question, press the audio record button and say "I don’t know”

				7️⃣  You cannot take notes during the test

				8️⃣  You may not pause the test once you have started it

				9️⃣  If you exit the app before you complete your test, you will not receive a score
""", reply_markup=reply_markup, parse_mode=telegram.ParseMode.HTML)

			time.sleep(10)

		else: 
			bot.send_message(chat_id=update.message.chat_id, text="⛔ Phone NOT found ⛔", reply_markup=reply_markup, parse_mode=telegram.ParseMode.HTML)

	def voice(bot, update):
		question=airtable_wrapper.get_question(update.message.from_user.id)
		if question >=6:
			bot.send_message(chat_id=update.message.chat_id, text="You have already finished your test. Thank you!", parse_mode=telegram.ParseMode.HTML)
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
				bot.send_message(chat_id=update.message.chat_id, text="🏆 This is the end of your TLT test 🏆. You may exit the TLT app now. Thank you!  🤗", parse_mode=telegram.ParseMode.HTML)
			else: 
				bot.send_audio(chat_id=update.message.chat_id, audio=open("tlt_audios/TLT_v5.1_question"+str(question_answered+1)+"_v1.mp3", "rb"))
				bot.send_message(chat_id=update.message.chat_id, text="Now click on \"Record\" to record your answer to Question "+str(question_answered+1))

	def next_button(bot, update):
		message_id=update.callback_query.message.message_id
		chat_id=update.callback_query.message.chat.id


		bot.send_message(chat_id=chat_id, text="""✈️🇺🇸 <b>Tourism English Language Test – TLT Test</b>

1️⃣	 In this test, you will be presented with several scenarios where a hotel front desk staff member responds to a guest.

2️⃣	 Read and listen to the scenarios. Then listen to what the guest says. Take on the role of a front desk staff member and answer the guest in English.

3️⃣	 You should answer the guest in a manner that is appropriate for a hotel front desk work situation.

4️⃣	 Use the voice recording feature in Telegram to record your answer. Then upload your recorded answer to each question""", parse_mode=telegram.ParseMode.HTML)

		bot.send_audio(chat_id=chat_id, audio=open("tlt_audios/TLT_v5.1_intro_v1.mp3", "rb"))
		
		time.sleep(20)

		#sending example question
		
		bot.send_message(chat_id=chat_id, text="""<b>Example Question</b>

Scenario: A guest calls the front desk and wants to have access to the hotel’s cable TV.

(Guest on the phone): Hi. I am trying to get access to the hotel’s cable TV, but I don’t know how. Can you help me?

You say: Sure. You will see two remote controls on the bedside table. Use the black remote control to turn on the TV, and then use the gray remote control to activate our cable service.
""", parse_mode=telegram.ParseMode.HTML)

		bot.send_photo(chat_id=chat_id, photo=open("images/hotel_receptionist.jpg","rb"))
		
		bot.send_audio(chat_id=chat_id, audio=open("tlt_audios/TLT_v5_1_example_question_and_answer_v1.mp3", "rb"))

		bot.send_message(chat_id=chat_id, text="Click on \"Play\" to listen to an example question and answer")

		#sending test questions
		time.sleep(30)
		bot.send_message(chat_id=chat_id, text="Now click on \"Play\" to listen to Question 1")
		time.sleep(10)
		bot.send_audio(chat_id=chat_id, audio=open("tlt_audios/TLT_v5.1_question1_v1.mp3", "rb"))
		time.sleep(10)
		bot.send_message(chat_id=chat_id, text="(3) Now click on \"Record\" to record your answer to Question 1")

	def error(bot, update, error):
		print("ERROR"+str(update)+" by "+str(error))


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

	next_handler = CallbackQueryHandler(next_button)
	dispatcher.add_handler(next_handler)

	dispatcher.add_error_handler(error)

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

#Buttons to navigate test questions

