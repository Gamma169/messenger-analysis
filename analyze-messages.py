#! /usr/bin/env python3

import argparse
from datetime import datetime
import json
import os


import plotly.graph_objects as go

###########################################################################
# Parameters

# Required
my_facebook_name = ''

# Optional
path = './inbox'

# Ignore convos with less than 100 messages-- can be configured
is_worth_including_threshold = 100

# Whether should include call duration in words-spoken
include_call_words = False

# How many words per second should be included if the above `include_call_words` is True
# Taken from https://virtualspeech.com/blog/average-speaking-rate-words-per-minute
call_speak_rate = 120 / 60

# Ignore calls shorter than 10 seconds
min_call_duration_length = 10

sort_mode = 'total'

filtered_list = []


###########################################################################
# Constants

GREEN = '\033[92m'
BLUE = '\033[94m'
RED = '\033[91m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
END = '\033[0m'

TOTAL_MESSAGES_SORT_MODE = 'total'
WORDS_SORT_MODE = 'num_words'
IMGUR_LINKS_SORT_MODE = 'imgur'
OLDEST_SORT_MODE = 'oldest'

SORT_CONFIGS = {
	TOTAL_MESSAGES_SORT_MODE: {
		'type': 'Total',
		'sort_func': lambda conversation: conversation.summary.total_messages,
		'reverse': True,
	},
	WORDS_SORT_MODE: {
		'type': 'Num Words',
		'sort_func': lambda conversation: conversation.summary.num_words,
		'reverse': True,
	},
	OLDEST_SORT_MODE: {
		'type': 'Oldest',
		'sort_func': lambda conversation: conversation.summary.oldest_message_time,
		'reverse': False,
	},
	IMGUR_LINKS_SORT_MODE: {
		'type': 'Imgur',
		'sort_func': lambda conversation: conversation.summary.imgur_links,
		'reverse': True,
	},	
}

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

		self.header_str = '{bold}{blue}{name}{end}'.format(bold=BOLD, blue=BLUE, name=self.other_person, end=END)

	def __str__(self):
		return str(self.summary)

	def message_history_str(self):
		return self.header_str + str(self.history)

	def words_history_str(self):
		return self.header_str + str(self.history.words_month_str())

	def messages_history_bar_obj(self):
		return self._create_bar_on_history_map(self.history.messages_month_map())

	def words_history_bar_obj(self):
		return self._create_bar_on_history_map(self.history.words_month_map())

	def call_history_bar_obj(self):
		return self._create_bar_on_history_map(self.history.calls_month_map())

	def call_duration_history_bar_obj(self):
		return self._create_bar_on_history_map(self.history.call_duration_month_map())

	def _create_bar_on_history_map(self, history_map):
		return go.Bar(name=self.other_person, x=self.history.message_dates, y=[history_map[month] for month in self.history.message_dates])

	def messages_history_relative_line_obj(self):
		return self._create_relative_line_on_history_map(self.history.messages_month_map())

	def words_history_relative_line_obj(self):
		return self._create_relative_line_on_history_map(self.history.words_month_map())

	def _create_relative_line_on_history_map(self, history_map):
		return go.Scatter(name=self.other_person, x=self.history.message_dates, y=[history_map[month] for month in self.history.message_dates],
			mode='lines', stackgroup='one', groupnorm='percent')

	def number_conversation_starts(self, hour_threshold=72, count_links=True):
		"""
		Get the number of times someone started a conversation after an elapsed period of time
		param hour_threshold: threshold for number of hours before a conversation is considered a "new" conversation 
		param count_links: whether the
		returns dict with name of person as key and number of times as value. 
		If count_links is True, will also have '<Name> Links' as keys and links that started a convo as values
		return dict also has 'hour_threshold' as convenience
		"""
		convo_starts = {
			my_facebook_name: 0,
			self.other_person: 0,
			'hour_threshold': hour_threshold
		}
		if count_links:
			my_links = my_facebook_name + ' Links'
			other_links = self.other_person + ' Links'
			convo_starts[my_links] = 0
			convo_starts[other_links] = 0

		for i in range(1, len(self.messages)):
			time_diff = (self.messages[i-1].time - self.messages[i].time).total_seconds() / 3600
			if time_diff >= hour_threshold:
				if self.messages[i].sent_by_me():
					convo_starts[my_facebook_name] += 1
					if count_links and self.messages[i].imgur_links_in_message() > 0:
						convo_starts[my_links] += 1
				else:
					convo_starts[self.other_person] += 1
					if count_links and self.messages[i].imgur_links_in_message() > 0:
						convo_starts[other_links] += 1

		return convo_starts



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
		self.num_words = 0
		self.num_calls = 0

		for message in messages:
			if message.sent_by_me():
				self.my_total_messages += 1
				num_links = message.imgur_links_in_message()
				self.imgur_links += num_links
				if num_links == 0:
					self.my_actual_messages += 1
			else:
				self.other_messages += 1

			self.num_words += message.words_in_message(include_call_words)

			if message.is_call() and message.call_duration > min_call_duration_length:
				self.num_calls += 1

		self.newest_message_time = messages[0].time
		self.oldest_message_time = messages[-1].time
		# Should probably filter out some outliers
		self.days_spoken = (self.newest_message_time - self.oldest_message_time).days
		self.average_msg_per_day = self.total_messages / (float(self.days_spoken) if self.days_spoken else 1)
		self.avg_calls_per_month = self.num_calls / (float(self.days_spoken / 30) if self.days_spoken else 1)



	def __str__(self):
		return """
	{bold}{blue}{name}{end}
	{green}{underline}Total Messages:{end}       {bold}{total}{end}
	{green}{underline}Total Words Written:{end}  {bold}{words}{end}
	{green}{underline}My Total Messages:{end}    {bold}{mine}{end}
	{green}{underline}Number of Calls:{end}      {bold}{calls}{end}
	{green}{underline}My Imgur Links:{end}       {bold}{imgur}{end}
	{green}{underline}My Actual Messages:{end}   {bold}{mine_actual}{end}
	{green}{underline}Other Messages:{end}       {bold}{other}{end}
	{green}{underline}Oldest Message:{end}       {bold}{oldest}{end}
	{green}{underline}Newest Message:{end}       {bold}{newest}{end}
	{green}{underline}Days Spoken:{end}          {bold}{days}{end}
	{green}{underline}Avg Messages Per Day:{end} {bold}{avg}{end}
	{green}{underline}Avg Calls Per Month: {end} {bold}{avg_calls}{end}
		""".format(bold=BOLD, green=GREEN, blue=BLUE, underline=UNDERLINE, end=END, 
			name=self.other_person,
			total=self.total_messages, words=self.num_words, mine=self.my_total_messages, calls=self.num_calls, imgur=self.imgur_links, mine_actual=self.my_actual_messages, other=self.other_messages,
			oldest=self.oldest_message_time, newest=self.newest_message_time, days=self.days_spoken, avg=self.average_msg_per_day, avg_calls=self.avg_calls_per_month).strip()


###########################################################################

class ConversationHistory(object):
	"""
	Class that holds history information around a conversation
	"""

	def __init__(self, messages):
		# A dict that holds references to message object based on the month was sent in
		# Key is string 'YYYY-MM'
		self.monthly_messages = {}
		# dict that holds specifically call-messages same as above messages
		self.monthly_calls = {}

		for message in messages:
			year_month = message.year_month()
			if self.monthly_messages.get(year_month):
				self.monthly_messages[year_month].append(message)
			else:
				self.monthly_messages[year_month] = [message]

			if message.is_call() and message.call_duration >= min_call_duration_length:
				if self.monthly_calls.get(year_month):
					self.monthly_calls[year_month].append(message)
				else:
					self.monthly_calls[year_month] = [message]


		# Get all the year-month keys in a sorted order
		self.message_dates = sorted(self.monthly_messages.keys(), key=lambda year_month: year_month)

	def num_messages_for_month(self, yyyy_mm):
		return len(self.monthly_messages.get(yyyy_mm, []))

	def num_calls_for_month(self, yyyy_mm):
		return len(self.monthly_calls.get(yyyy_mm, []))

	def num_words_for_month(self, yyyy_mm):
		messages = self.monthly_messages.get(yyyy_mm, [])
		num_words = 0
		for message in messages:
			num_words += message.words_in_message(include_call_words)
		return num_words

	def call_duration_for_month(self, yyyy_mm):
		messages = self.monthly_calls.get(yyyy_mm, [])
		call_duration = 0
		for message in messages:
			call_duration += message.call_duration
		return call_duration


	def messages_month_map(self):
		"""Maps monthly_messages into number of messages sent each month"""
		return self._map(lambda month: self.num_messages_for_month(month))

	def words_month_map(self):
		"""Maps monthly_messages into number of words sent each month"""
		return self._map(lambda month: self.num_words_for_month(month))

	def calls_month_map(self):
		"""Maps monthly_calls into number of calls sent each month"""
		return self._map(lambda month: self.num_calls_for_month(month))

	def call_duration_month_map(self):
		"""Maps monthly_calls into duration of calls each month"""
		return self._map(lambda month: self.call_duration_for_month(month))

	def words_per_message_month_map(self):
		"""Maps monthly_messages into number of words per message sent each month"""
		return self._map(lambda month: self.num_words_for_month(month) / self.num_messages_for_month(month))

	def _map(self, map_func):
		"""Maps monthly-messages according to the map-function"""
		mapped_msgs = {}
		for month in self.message_dates:
			mapped_msgs[month] = map_func(month)
		return mapped_msgs

	def words_month_str(self):
		return self._stringify(self.words_month_map())

	def _stringify(self, monthly_messages_map):
		"""
		Returns a printable string version of the monthly messages map passed in
		Note that the monthly_messages_map can be a mapped version, or the base one
		"""
		ret_str = ''
		for month in self.message_dates:
			ret_str += """
    {k} -- {v}""".format(k=month, v=str(monthly_messages_map[month]))
		return ret_str

	def __str__(self):
		return self._stringify(self.messages_month_map())
	

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

		self.call_duration = kwargs.get('call_duration', -1)

		for k in kwargs:
			setattr(self, k, kwargs[k])

	
	def sent_by_me(self):
		return self.sender_name == my_facebook_name

	def year_month(self):
		return self.time.strftime('%Y-%m')

	# Types of messages:  Generic, Share, Call
	# Generic messages can have links in them or can be gifs/photos/stickers
	# Shares can have content assocaited with them
	# Calls have a duration	

	def is_call(self):
		return self.type == "Call"


	def words_in_message(self, include_call=False):
		call_words = 0
		if include_call and self.is_call:
			call_words = call_speak_rate * self.call_duration
		
		return call_words if self.is_call() else len(self.content.split())

	def imgur_links_in_message(self):
		return 1 if (self.type == 'Share' and 'imgur' in getattr(self, 'share', {'link':''}).get('link', '')) or ('imgur.com' in self.content) else 0


	def __str__(self):
		msg =  """
		Conversation: {conv}
		Sender: {sender}
		Type: {type}
		Time: {time}
		""".format(conv=self.conversation.other_person, sender=self.sender, type=self.type, time=self.time).strip()

		if self.is_call():
			msg += 'Call Duration: {dur}'.format(dur=self.call_duration)
		else:
			msg += 'Content: {content}'.format(content=self.content)

		return msg



###########################################################################
# Utils

def is_worth_including(message_list):
	return len(message_list) >= is_worth_including_threshold

def print_header(header_str):
	print('{bold}{red}========  {header}  ========{end}'.format(bold=BOLD, red=RED, header=header_str, end=END))

def print_summary_data(conversations, up_to=15, sort_mode=TOTAL_MESSAGES_SORT_MODE):
	_print_messages(conversations, up_to, sort_mode, lambda conversation: conversation)


def print_messaging_history(conversations, up_to=7, sort_mode=TOTAL_MESSAGES_SORT_MODE):
	_print_messages(conversations, up_to, sort_mode, lambda conversation: conversation.message_history_str())

def print_messaging_history_words_per_month(conversations, up_to=7, sort_mode=TOTAL_MESSAGES_SORT_MODE):
	_print_messages(conversations, up_to, sort_mode, lambda conversation: conversation.words_history_str())	

def print_conversation_starts(conversations, up_to=7, sort_mode=TOTAL_MESSAGES_SORT_MODE, hour_threshold=72):
	_print_messages(conversations, up_to, sort_mode, lambda conversation: conversation.number_conversation_starts(hour_threshold=hour_threshold))

def sort_conversations(conversations, sort_mode):
	sort_obj = SORT_CONFIGS[sort_mode]
	return sorted(conversations, key=sort_obj['sort_func'], reverse=sort_obj['reverse'])


def _print_messages(conversations, up_to, sort_mode, print_func):
	print_header('Top ' + str(up_to) + ' Conversations Sorted By ' + SORT_CONFIGS[sort_mode]['type'])
	sorted_conversations = sort_conversations(conversations, sort_mode)
	for idx, conversation in enumerate(sorted_conversations[0:up_to]):
		print(idx+1, print_func(conversation))

def display_conversations_as_bars(conversations, up_to=5, sort_mode=TOTAL_MESSAGES_SORT_MODE, use_words=False, bar_mode='group', calls_graphs=False):
	conversations_sorted = sort_conversations(conversations, sort_mode)

	history_total_msgs_figure = go.Figure(
		data=[conv.messages_history_bar_obj() for conv in conversations_sorted[0:up_to]]
	)
	_style_bar_chart(history_total_msgs_figure, 'Total Messages Sent In Conversation Over Time', y_axis_title='Total Number of Messages Sent', bar_mode=bar_mode)
	history_total_msgs_figure.show()
	
	if calls_graphs:
		history_calls_figure = go.Figure(
			data=[conv.call_history_bar_obj() for conv in conversations_sorted[0:up_to]]
		)
		_style_bar_chart(history_calls_figure, 'Total Calls In Conversation Over Time', y_axis_title='Number of Calls', bar_mode=bar_mode)
		history_calls_figure.show()

	if use_words:
		history_words_figure = go.Figure(
			data=[conv.words_history_bar_obj() for conv in conversations_sorted[0:up_to]]
		)
		_style_bar_chart(history_words_figure, 'Total Words Written In Conversation Over Time', y_axis_title='Total Amount of Words Written', bar_mode=bar_mode)
		history_words_figure.show()

		if calls_graphs:
			history_calls_duration_figure = go.Figure(
				data=[conv.call_duration_history_bar_obj() for conv in conversations_sorted[0:up_to]]
			)
			_style_bar_chart(history_calls_duration_figure, 'Total Seconds Spent on Call in Conversation Over Time', y_axis_title='Seconds Spent On Call', bar_mode=bar_mode)
			history_calls_duration_figure.show()


def _style_bar_chart(figure, name, y_axis_title, bar_mode='group'):
	figure.update_layout(
		barmode=bar_mode,
		title=go.layout.Title(
			text=name,
			xref='paper',
			x=0
		),
		xaxis=go.layout.XAxis(
			nticks=50,
			tickangle=-45
		),
		yaxis=go.layout.YAxis(
		title=go.layout.yaxis.Title(text=y_axis_title)
		)
	)

def display_conversations_relative_percents(conversations, up_to=5, sort_mode=TOTAL_MESSAGES_SORT_MODE, use_words=False):
	"""
	Honestly, these graphs are kinda ugly.  Thought they'd be cool, but with more than 3 people, they're just messy
	"""
	conversations_sorted = sort_conversations(conversations, sort_mode)

	total_messages_figure = go.Figure()
	for conv in conversations_sorted[0:up_to]:
		total_messages_figure.add_trace(conv.messages_history_relative_line_obj())

	_style_relative_percent_chart(total_messages_figure, 'Relative Percents of Total Messages Over Time')
	total_messages_figure.show()

	if use_words:
		total_words_figure = go.Figure()
		for conv in conversations_sorted[0:up_to]:
			total_words_figure.add_trace(conv.words_history_relative_line_obj())

		_style_relative_percent_chart(total_words_figure, 'Relative Percents of Words Sent Over Time')
		total_words_figure.show()

def _style_relative_percent_chart(figure, name):
	figure.update_layout(
		showlegend=True,
		title=go.layout.Title(
			text=name,
			xref='paper',
			x=0
		),
		yaxis=dict(
			type='linear',
			range=[1, 100],
			ticksuffix='%'
		)
	)

def get_conversations():
	conversations = []
	num_conversations = 0
	num_conversations_with_two_people = 0

	folders = os.listdir(path)
	for name in folders:
		files = os.listdir(path + '/' + name)
		has_json_files = any('.json' in file_name for file_name in files)
		if has_json_files:
			num_conversations += 1
			json_files = [file_name for file_name in files if '.json' in file_name]
			json_files.sort()
			# Large conversations get split up in multiple files, so we have to consolidate the conversation
			# Note that current facebook implementation has `message_1.json` the newest files, and `message_3.json` the oldest, so we can just concat them together
			all_messages = []
			for idx, file_name in enumerate(json_files):
				with open('{}/{}/{}'.format(path, name, file_name)) as f:
					data = json.load(f)
					participants = data['participants']
					if len(participants) == 2:
						if idx == 0:
							num_conversations_with_two_people += 1
						all_messages.extend(data['messages'])
					
			if is_worth_including(all_messages):
				conversations.append(Conversation(all_messages))

	print_header('Number of Conversations Found')
	print(num_conversations)
	print_header('Number of Conversation Between Two People')
	print(num_conversations_with_two_people)
	print_header('Messages Worth Including')
	print(len(conversations))

	return conversations



###########################################################################

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='A program to analyze facebook messenger data.')
	
	parser.add_argument('my_name', type=str, 
		help='The name you use for facebook.  The name that shows up for you in the messages')
	
	parser.add_argument('-p', '--path', type=str, default=path,
		help='Relative or absolute path to the location of the conversation folders. Default "./inbox"')
	parser.add_argument('-i', '--include-threshold', type=int, default=is_worth_including_threshold,
		help='The smallest number of total messages in a conversation for a conversation to be counted. Default 100')
	parser.add_argument('-s', '--sort-mode', type=str, default=sort_mode, choices=[TOTAL_MESSAGES_SORT_MODE, WORDS_SORT_MODE, OLDEST_SORT_MODE, IMGUR_LINKS_SORT_MODE], 
		help='How to sort the messages by.  Default "total"')
	parser.add_argument('-t', '--top-people', type=int, default=5,
		help='The top number of people people to display.  Default 5')
	parser.add_argument('-f', '--filter', type=str, default='',
		help='List of names, separated by comma (no whitespace between), for the program to filter to. If not provided, will do no filtering.  If a given name does not exist, will still filter, but will do nothing for that name.')

	# Summary-only
	parser.add_argument('-so', '--summary-only', action='store_true',
		help='Print only summary information in command-line.  Do not display graphs')
	# Pring History
	parser.add_argument('-ph', '--print-history', action='store_true',
		help='Print the messaging history per month')
	# Include Words-Count
	parser.add_argument('-w', '--word-count', action='store_true',
		help='Display analysis with word-count in addition to total messages-- if paired with -c, will display call duration graphs')
	parser.add_argument('-b', '--bar-mode', type=str, default='group', choices=['group', 'stack'], 
		help='How to display the bars in the history graph. Default "group"')
	parser.add_argument('-rg', '--relative-graphs', action='store_true',
		help='Display the relative-percent graphs as well')
	parser.add_argument('-c', '--calls', action='store_true',
		help='Generate analysis on call graphs')
	parser.add_argument('-wc', '--words-calls', action='store_true',
		help='Include call duration in word-count calculations')

	args = parser.parse_args()
	
	my_facebook_name = args.my_name
	path = args.path
	is_worth_including_threshold = args.include_threshold
	sort_mode = args.sort_mode
	num_to_display = args.top_people
	filtered_list = args.filter.split(',') if len(args.filter) > 0 else []
	summary_only = args.summary_only
	use_words = args.word_count
	bar_mode = args.bar_mode
	print_history = args.print_history
	display_relative = args.relative_graphs
	calls_graphs = args.calls

	# Note this is global var
	include_call_words = args.words_calls

	
	conversations = get_conversations()
	if len(filtered_list) > 0:
		print_header('Filtering Conversations Down To Top {} of {} Given Names'.format(num_to_display, len(filtered_list)))
		conversations = [conv for conv in conversations if conv.other_person in filtered_list]


	print_summary_data(conversations, up_to=num_to_display, sort_mode=sort_mode)
	
	if not summary_only:
		
		if print_history:
			print_header('Messaging History in Total Messages Per Month')
			print_messaging_history(conversations, up_to=num_to_display, sort_mode=sort_mode)

			if use_words:
				print_header('Messaging History in Total Words Per Month')
				print_messaging_history_words_per_month(conversations, up_to=num_to_display, sort_mode=sort_mode)

		display_conversations_as_bars(conversations, up_to=num_to_display, sort_mode=sort_mode, use_words=use_words, bar_mode=bar_mode, calls_graphs=calls_graphs)

		if display_relative:
			display_conversations_relative_percents(conversations, up_to=num_to_display, sort_mode=sort_mode, use_words=use_words)
