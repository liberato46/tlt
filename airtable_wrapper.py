from airtable import airtable
at=airtable.Airtable('appyKxEV736kAtWMk', 'key7dKLOWhsE8Lwtg')

def associate(phone, user_id):
	output_text=False 
	lines=at.get('Table 1').get('records')
	
	for line in lines:
		user_phone=line.get('fields').get('Cell phone #')
		user_phone=user_phone.replace(' ', '')
		user_phone=user_phone.replace('(', '')
		user_phone=user_phone.replace(')', '')
		user_phone=user_phone.replace('-', '')
		user_phone=user_phone.replace('+', '')
		user_phone=user_phone.replace('.', '')

		if user_phone in phone:
			line_id=line.get('id')
			try:
				at.update('Table 1', line_id, {'telegram_id':str(user_id), 'question':0})
			except:
				print("ERROR!!")
			output_text=True
			break
	return output_text

def save_response(user_id, s3_url):
	lines=at.get('Table 1').get('records')
	for line in lines:
		telegram_id=line.get('fields').get("telegram_id")
		if telegram_id==str(user_id):
			line_id=line.get('id')
			question_number=line.get('fields').get("question")
			try:
				at.update('Table 1', line_id, {"question"+str(question_number+1)+"url":s3_url, "question":question_number+1})
			except:
				print("ERROR!!")
			break
	return question_number+1

def get_question(user_id):
	lines=at.get('Table 1').get('records')
	for line in lines:
		telegram_id=line.get('fields').get("telegram_id")
		if telegram_id==str(user_id):
			line_id=line.get('id')
			question_number=line.get('fields').get("question")
			return question_number


