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
		'sort_func': lambda message: message.total_messages,
		'reverse': True,
	},
	IMGUR_LINKS_SORT_MODE: {
		'type': 'Imgur',
		'sort_func': lambda message: message.imgur_links,
		'reverse': True,
	},	
	OLDEST_SORT_MODE: {
		'type': 'Oldest',
		'sort_func': lambda message: message.oldest_message,
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
	def __init__(self, other_person, messages):
		self.other_person = other_person

		# Dict that holds each message by month
		self.messages_per_month = {}

		self.messages = []

		my_messages = 0
		other_messages = 0
		imgur_links = 0
		for message in messages:

			message_obj = Message(self, **message)
			self.messages.append(message_obj)

			month_year = message_obj.month_year()
			self.messages_per_month[month_year] = (self.messages_per_month.get(month_year) + 1) if self.messages_per_month.get(month_year) else 1

			
			if message_obj.sent_by_me():
				my_messages += 1
				imgur_links += message_obj.imgur_links_in_message()
			else:
				other_messages += 1


		self.message_time_tuples = [(k, self.messages_per_month[k]) for k in self.messages_per_month.keys()]
		self.message_time_tuples = sorted(self.message_time_tuples, key=lambda tuple: tuple[0])
		
		self.other_messages = other_messages
		self.my_total_messages = my_messages
		self.imgur_links = imgur_links
		self.my_actual_messages = my_messages - imgur_links
		self.total_messages = my_messages + other_messages
		

		newest_message = messages[0]['timestamp_ms']/1000
		oldest_message = messages[-1]['timestamp_ms']/1000
		self.newest_message = datetime.fromtimestamp(newest_message)
		self.oldest_message = datetime.fromtimestamp(oldest_message)
		# Should probably filter out some outliers
		self.days_spoken = (self.newest_message - self.oldest_message).days
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
			oldest=self.oldest_message, newest=self.newest_message, days=self.days_spoken, avg=self.average_msg_per_day).strip()

	def get_message_history_str(self):
		"""Function that returns the conversation's history broken down by month as a string"""
		history_str = '{bold}{blue}{name}{end}'.format(bold=BOLD, blue=BLUE, name=self.other_person, end=END)
		for message_tuple in self.message_time_tuples:
			history_str += """
    {k} -- {v}""".format(k=message_tuple[0], v=message_tuple[1])
		return history_str

###########################################################################

class Message(object):
	"""Class that holds data on a message as well as helper and logic functions"""
	def __init__(self, conversation, **kwargs):
		super(Message, self).__init__()
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

	def month_year(self):
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
	_print_messages(conversations, up_to, sort_mode, lambda message: message)


def print_messaging_history(conversations, up_to=7, sort_mode=TOTAL_MESSAGES_SORT_MODE):
	_print_messages(conversations, up_to, sort_mode, lambda message: message.get_message_history_str())
	


def _print_messages(people_messages, up_to, sort_mode, print_func):
	sort_obj = SORT_CONFIGS[sort_mode]

	print_header('Messages Sorted By ' + sort_obj['type'])
	sorted_msgs = sorted(people_messages, key=sort_obj['sort_func'], reverse=sort_obj['reverse'])
	for idx, message_summary in enumerate(sorted_msgs[0:up_to]):
		print(idx+1, print_func(message_summary))


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
					other_person = participants[0]['name'] if participants[0]['name'] != MY_FACEBOOK_NAME else participants[1]['name']
				
					if is_worth_including(data['messages']):
						conversations.append(Conversation(other_person, data['messages']))

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
# print_header('Message Dates')
# print_messaging_history(conversations)
