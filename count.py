#! /usr/bin/env python3

import json
import os
from datetime import datetime


###########################################################################
# Constants

GREEN = '\033[92m'
BLUE = '\033[94m'
RED = '\033[91m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
END = '\033[0m'

TOTAL_MESSAGES_SORT_MODE = 0
IMGUR_LINKS_SORT_MODE = 1
OLDEST_SORT_MODE = 2

SORT_CONFIGS = {
	TOTAL_MESSAGES_SORT_MODE: {
		'type': 'Total',
		'sort_func': lambda conversation: conversation.summary.total_messages,
		'reverse': True,
	},
	IMGUR_LINKS_SORT_MODE: {
		'type': 'Imgur',
		'sort_func': lambda conversation: conversation.summary.imgur_links,
		'reverse': True,
	},	
	OLDEST_SORT_MODE: {
		'type': 'Oldest',
		'sort_func': lambda conversation: conversation.summary.oldest_message,
		'reverse': False,
	},	
}

###########################################################################
# Parameters

path = './inbox'

MY_FACEBOOK_NAME = 'Rienzi Gokea'

IS_WORTH_INCLUDING_THRESHOLD = 100

###########################################################################

class Conversation(object):
	"""
	High-level wrapper class that holds information about messages,
	convenience functions, and objects that hold logic for different parts of the script
	"""
	def __init__(self, messages):


		self.messages = [Message(self, **message) for message in messages]

		self.summary = ConversationSummary(self.messages)
		self.history = ConversationHistory(self.messages)

		# Just a convenience attribute so we don't have to reference the summary's other person
		self.other_person = self.summary.other_person


	def __str__(self):
		return str(self.summary)

	def message_history_str(self):
		return '{bold}{blue}{name}{end}'.format(bold=BOLD, blue=BLUE, name=self.other_person, end=END) + str(self.history)



###########################################################################

class ConversationSummary(object):
	"""
	Holds summary data around a conversation
	"""
	def __init__(self, messages):
		self.other_person = ''
		for message in messages:
			if not message.sent_by_me():
				self.other_person = message.sender_name
				break

		self.total_messages = len(messages)
		self.my_total_messages = 0
		self.my_actual_messages = 0
		self.other_messages = 0
		self.imgur_links = 0

		for message in messages:
			if message.sent_by_me():
				self.my_total_messages += 1
				num_links = message.imgur_links_in_message()
				self.imgur_links += num_links
				if num_links == 0:
					self.my_actual_messages += 1
			else:
				self.other_messages += 1


		self.newest_message_time = messages[0].time
		self.oldest_message_time = messages[-1].time
		# Should probably filter out some outliers
		self.days_spoken = (self.newest_message_time - self.oldest_message_time).days
		self.average_msg_per_day = self.total_messages / (float(self.days_spoken) if self.days_spoken else 1)

	def __str__(self):
		return """
	{bold}{blue}{name}{end}
	{green}{underline}Total Messages:{end}       {bold}{total}{end}
	{green}{underline}My Total Messages:{end}    {bold}{mine}{end}
	{green}{underline}My Imgur Links:{end}       {bold}{imgur}{end}
	{green}{underline}My Actual Messages:{end}   {bold}{mine_actual}{end}
	{green}{underline}Other Messages:{end}       {bold}{other}{end}
	{green}{underline}Oldest Message:{end}       {bold}{oldest}{end}
	{green}{underline}Newest Message:{end}       {bold}{newest}{end}
	{green}{underline}Days Spoken:{end}          {bold}{days}{end}
	{green}{underline}Avg Messages Per Day:{end} {bold}{avg}{end}
		""".format(bold=BOLD, green=GREEN, blue=BLUE, underline=UNDERLINE, end=END, 
			name=self.other_person,
			total=self.total_messages, mine=self.my_total_messages, imgur=self.imgur_links, mine_actual=self.my_actual_messages, other=self.other_messages, 
			oldest=self.oldest_message_time, newest=self.newest_message_time, days=self.days_spoken, avg=self.average_msg_per_day).strip()


###########################################################################
class ConversationHistory(object):
	"""
	Class that holds history information around a conversation
	"""

	def __init__(self, messages):
		# A dict that holds references to message object based on the month was sent in
		# Key is string 'YYYY-MM'
		self.monthly_messages = {}

		for message in messages:
			year_month = message.year_month()
			if self.monthly_messages.get(year_month):
				self.monthly_messages[year_month].append(message)
			else:
				self.monthly_messages[year_month] = [message]


		# Get all the year-month keys in a sorted order
		self.message_dates = sorted(self.monthly_messages.keys(), key=lambda year_month: year_month)

	def num_messages_for_month(self, yyyy_mm):
		return len(self.monthly_messages.get(yyyy_mm, []))

	def num_words_for_month(self, yyyy_mm):
		messages = self.monthly_messages.get(yyyy_mm, [])
		num_words = 0
		for message in messages:
			num_words += message.words_in_message()
		return num_words

	def words_per_month_breakdown(self):
		"""Maps monthly_messages into number of words per month"""
		words_per_month = {}
		for month in self.message_dates:
			words_per_month[month] = self.num_words_for_month(month)
		return words_per_month

	def words_per_month_str(self):
		words_str = ''
		words_per_month = self.words_per_month_breakdown()
		for month in self.message_dates:
			history_str += """
    {k} -- {v}""".format(k=message_date, v=words_per_month[month])
		return history_str


	def __str__(self):
		"""Function that returns the conversation's history broken down by month as a string"""
		history_str = ''
		for message_date in self.message_dates:
			history_str += """
    {k} -- {v}""".format(k=message_date, v=self.num_messages_for_month(message_date))
		return history_str
	

###########################################################################

class Message(object):
	"""
	Class that holds data on a message as well as helper and logic functions
	"""
	def __init__(self, conversation, **kwargs):
		# A self-reference to the overall conversation for convenience
		self.conversation = conversation

		# We want the message to die if it doesn't have these kwargs
		self.time = datetime.fromtimestamp(kwargs['timestamp_ms']/1000)
		self.sender = kwargs['sender_name']
		self.type = kwargs['type']

		# Somehow, a message can not have the content key
		self.content = kwargs.get('content', '')

		for k in kwargs:
			setattr(self, k, kwargs[k])

	
	def sent_by_me(self):
		return self.sender_name == MY_FACEBOOK_NAME

	def year_month(self):
		return self.time.strftime('%Y-%m')

	# Types of messages:  Generic, Share, Call
	# Generic messages can have links in them or can be gifs/photos/stickers
	# Shares can have content assocaited with them
	# Calls have a duration	

	def is_call(self):
		return self.type == "Call"

	def words_in_message(self):
		return 0 if self.is_call() else len(self.content.split())

	def imgur_links_in_message(self):
		return 1 if (self.type == 'Share' and 'imgur' in getattr(self, 'share', {'link':''})['link']) or ('imgur.com' in self.content) else 0


	def __str__(self):
		return """
		Conversation: {conv}
		Sender: {sender}
		Type: {type}
		Time: {time}
		Content: {content}
		""".format(conv=self.conversation.other_person, sender=self.sender, type=self.type, time=self.time, content=self.content).strip()



###########################################################################

def is_worth_including(message_list):
	return len(message_list) >= IS_WORTH_INCLUDING_THRESHOLD

def print_header(header_str):
	print('{bold}{red}========  {header}  ========{end}'.format(bold=BOLD, red=RED, header=header_str, end=END))

def print_summary_data(conversations, up_to=15, sort_mode=TOTAL_MESSAGES_SORT_MODE):
	_print_messages(conversations, up_to, sort_mode, lambda conversation: conversation)


def print_messaging_history(conversations, up_to=7, sort_mode=TOTAL_MESSAGES_SORT_MODE):
	_print_messages(conversations, up_to, sort_mode, lambda conversation: conversation.message_history_str())

# TODO
def print_messaging_history_words_per_month(conversations, up_to=7, sort_mode=TOTAL_MESSAGES_SORT_MODE):
	_print_messages(conversations, up_to, sort_mode, lambda conversation: conversation.message_history_str())	
	


def _print_messages(conversations, up_to, sort_mode, print_func):
	sort_obj = SORT_CONFIGS[sort_mode]

	print_header('Conversations Sorted By ' + sort_obj['type'])
	sorted_conversations = sorted(conversations, key=sort_obj['sort_func'], reverse=sort_obj['reverse'])
	for idx, conversation_summary in enumerate(sorted_conversations[0:up_to]):
		print(idx+1, print_func(conversation_summary))


def get_conversations():
	conversations = []
	num_conversations = 0
	num_conversations_with_two_people = 0

	folders = os.listdir(path)
	for name in folders:
		files = os.listdir(path + '/' + name)
		if files[0] == 'message.json':
			num_conversations += 1
			with open('{}/{}/message.json'.format(path, name)) as f:
				data = json.load(f)
				participants = data['participants']
				if len(participants) == 2:
					num_conversations_with_two_people += 1
				
					if is_worth_including(data['messages']):
						conversations.append(Conversation(data['messages']))

	print_header('Number of Conversations Found')
	print(num_conversations)
	print_header('Number of Conversation Between Two People')
	print(num_conversations_with_two_people)

	return conversations



###########################################################################



conversations = get_conversations()

print_header('Messages Worth Including')
print(len(conversations))

print_summary_data(conversations)
print_header('Message Dates')
print_messaging_history(conversations)
