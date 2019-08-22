#! /usr/bin/env python3

"""
A simple script to create an anonymous facebook message conversation of two people out of an actual one
"""

import json
import sys
import os

###########################################################################
# Parameters

# required
file = ''

my_name = ''

other_name = ''

# optional
anonymous_name = 'anonymous'

###########################################################################
# Constants

LOREM_IPSUM = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque et dolor libero. Nunc sit amet elit vestibulum lacus dapibus feugiat eu id sem. Etiam euismod volutpat risus at egestas. Nunc commodo sodales enim eu placerat. Aliquam luctus, ex sit amet bibendum tempus, nunc nibh auctor nulla, vitae laoreet lectus nulla in lacus. Nunc tempus tempor ipsum vitae porta. Donec posuere, ligula nec sodales porttitor, sem lacus fermentum ex, id condimentum lacus velit vitae neque. In hac habitasse platea dictumst. Phasellus tincidunt nibh odio, ac vehicula quam cursus eu. Duis condimentum dictum lorem eget dapibus. Donec imperdiet ullamcorper consequat.
Nunc fringilla mauris eget gravida scelerisque. Proin fringilla nulla in velit sollicitudin, ut varius purus tincidunt. Nullam id consequat nisi. Mauris non dui et augue ultrices aliquet molestie ut mauris. Phasellus eu nisl ultrices, maximus dolor at, ultricies ex. Maecenas nec nulla feugiat, mollis ex ac, dignissim augue. Nulla feugiat mi vel tristique laoreet. Proin scelerisque ligula ligula, vel ornare velit accumsan nec. Vivamus tristique nisi ac diam vehicula lobortis.
Aliquam imperdiet gravida enim mollis facilisis. Sed semper nisi in lorem rhoncus, nec placerat quam porttitor. In hac habitasse platea dictumst. Pellentesque tristique aliquet nunc non viverra. Aenean dictum nec justo sed cursus. Pellentesque vitae ornare justo, id efficitur leo. Cras lectus nunc, auctor condimentum dolor ut, viverra congue elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque eget tristique sapien.
Suspendisse quam tortor, mattis at tortor pulvinar, malesuada ultricies urna. Suspendisse id convallis ante. Phasellus faucibus, nisi vel malesuada auctor, enim libero convallis nisl, vel vehicula est elit id tortor. Vivamus mollis leo nec nulla malesuada iaculis. Vestibulum vitae rutrum libero. Nullam aliquet, lectus a porttitor fermentum, lectus turpis eleifend ante, sit amet dignissim arcu nibh sit amet ligula. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Proin ut condimentum tellus, in dapibus lectus. Etiam quis lobortis nibh. Cras sollicitudin odio eu ante ullamcorper, ac imperdiet diam vulputate. Aenean ut vulputate erat. Vestibulum ut enim volutpat, imperdiet urna ac, sollicitudin est.
Morbi eleifend non ligula et dapibus. Aenean magna turpis, convallis eu metus a, maximus ultrices elit. Nulla ullamcorper felis neque, nec congue diam semper a. Integer elementum magna sed euismod tincidunt. Nullam in mauris a tortor placerat condimentum eget nec risus. Nunc convallis ligula ligula, vel laoreet magna dictum a. Aliquam nunc purus, porta porttitor cursus in, aliquam vel nulla.
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut leo felis, posuere non rhoncus ut, congue a velit. Etiam et enim eget nisi semper ullamcorper. In suscipit elit ut turpis lacinia, vel porta augue efficitur. Phasellus vitae nibh dapibus, aliquam nunc at, tempus ipsum. Phasellus at orci gravida, scelerisque enim eu, dapibus purus. Vestibulum tincidunt lorem id ipsum tempus sagittis.
Cras scelerisque sapien a metus ullamcorper, at gravida magna tempor. Praesent eget urna eget mauris condimentum facilisis eu eu ligula. Pellentesque ac velit sed ante porttitor placerat. Proin sed risus non nulla auctor posuere id eu neque. In tempor mi at felis commodo, nec blandit felis ullamcorper. Vestibulum vel urna ex. Vivamus placerat, mi eget consequat porta, tortor enim tempor purus, id rhoncus nulla nibh vel odio. Morbi gravida a ante a vulputate. Duis tempor enim ex, id fermentum ligula luctus ac. Sed euismod sit amet purus sed condimentum. Sed hendrerit tellus quam, eget pulvinar nisi aliquet ac.
Cras maximus sapien aliquet, ullamcorper risus eget, ullamcorper est. Vestibulum vestibulum mauris ut enim lacinia, a egestas libero sodales. Praesent interdum lectus vehicula aliquet euismod. Integer ullamcorper sodales dui in ultricies. Maecenas non augue volutpat, placerat ante sed, lobortis nunc. Suspendisse eu egestas urna. Ut sodales nisi eget mi posuere, in consequat arcu euismod. Aenean quis justo facilisis, consectetur eros eget, aliquam leo. In hac habitasse platea dictumst. Nullam ut felis laoreet, blandit tellus sit amet, vehicula ligula. Duis metus lectus, auctor efficitur faucibus ut, aliquam nec enim. Phasellus quis viverra mauris. Curabitur consequat posuere nunc vel aliquet.
Curabitur accumsan pellentesque ipsum vitae tempus. Maecenas odio mi, facilisis ac commodo non, commodo quis augue. In venenatis pharetra lacus, at consectetur turpis volutpat non. Sed sapien purus, maximus faucibus felis a, consequat viverra risus. Sed auctor a ligula a ullamcorper. Pellentesque vitae leo imperdiet, molestie urna vitae, volutpat nisl. Integer vel purus aliquet, condimentum turpis et, consectetur nibh. Nullam congue ipsum eget tincidunt suscipit. Nunc congue malesuada mi in auctor. Donec placerat porttitor erat. Sed sem arcu, lobortis nec lectus non, malesuada cursus tortor. Aliquam fringilla consectetur fermentum. Suspendisse elementum, purus euismod consectetur ultricies, tellus libero varius enim, vel viverra nulla ex at dolor.
Ut at varius elit, ut scelerisque lectus. Aenean placerat sodales risus nec vehicula. Curabitur et luctus est, vel egestas tortor. Etiam quam lorem, viverra id semper et, laoreet sed nibh. Nunc laoreet tempor pretium. Quisque posuere purus vitae purus ultricies tristique. Curabitur nec euismod purus. Pellentesque velit lacus, pretium et condimentum at, tempus quis dui. Aliquam non pretium mauris. Morbi viverra erat ac mi ultricies pulvinar. Sed a vulputate mauris. Nam convallis placerat tortor, sed vulputate mi convallis ullamcorper. Curabitur vitae dolor id mi tincidunt tempus.
In gravida tellus leo. Quisque eget fermentum purus. Morbi posuere tincidunt volutpat. Etiam ac sodales dui. Pellentesque quis mauris a urna auctor viverra eget ac libero. Aenean eget ultrices odio. Sed id mauris eget ligula condimentum imperdiet id sed ante. Maecenas eu nunc leo. Nullam quam est, efficitur sit amet elementum a, ornare vitae enim. Donec nibh elit, bibendum quis risus ac, placerat egestas purus. Morbi commodo luctus lobortis. Pellentesque ornare justo nec aliquet imperdiet.
Pellentesque sollicitudin mollis feugiat. Aenean vitae ligula nec elit tincidunt convallis quis vel massa. Nunc congue erat quis odio dapibus, eget cursus mauris feugiat. Etiam in quam sapien. Curabitur dolor lacus, feugiat quis auctor vitae, viverra nec orci. Vivamus tellus nibh, consequat non commodo in, porta sit amet ligula. Vestibulum porttitor nunc sit amet mollis varius. Suspendisse dignissim nulla vel elit venenatis luctus. Ut vel nunc neque. Nullam varius ut purus eu scelerisque. Pellentesque arcu massa, luctus quis ligula in, fringilla malesuada mi. Praesent dictum, ligula eget vestibulum vehicula, diam orci viverra libero, et fringilla dolor nisi vel diam. In ac tempor nulla. Cras eu tortor ligula. Curabitur felis augue, blandit vel arcu non, egestas tristique erat.
Donec sit amet fringilla sapien. Curabitur risus nisl, euismod vitae luctus nec, varius at velit. Sed nec ligula vel urna pulvinar gravida. Praesent posuere tellus quis hendrerit vestibulum. Aliquam fermentum lacinia tellus a porta. Etiam sollicitudin neque ac lacus mollis mattis. Aenean feugiat molestie pulvinar. Sed finibus mi vel accumsan bibendum. Nulla lacinia eros augue, sed gravida eros varius sit amet. Duis vitae aliquam dui, sed consequat purus.
Sed nec purus turpis. Nam lacinia arcu id nisi pharetra, eget porttitor nunc fringilla. Nunc malesuada risus vitae commodo elementum. Quisque convallis felis at tellus tincidunt, eu ullamcorper ante consequat. Phasellus ornare posuere est, non rutrum libero fermentum sit amet. Donec tortor justo, imperdiet eu pretium id, sodales at nisi. Sed sapien ex, cursus nec purus et, maximus interdum urna. Etiam euismod finibus nunc nec dictum. Vivamus a cursus arcu. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Integer nec neque vitae leo eleifend sodales vel id orci. Cras ut fringilla odio, scelerisque sagittis purus. Morbi dictum finibus condimentum.
Curabitur mattis, ligula vitae fringilla convallis, ipsum ex sodales arcu, a viverra mauris enim eget magna. Etiam sit amet arcu risus. Curabitur vel dolor vitae arcu tincidunt consectetur in vitae tellus. Donec gravida tortor vel quam blandit, et tincidunt dui pellentesque. Cras sit amet luctus metus. Morbi egestas odio at nisi sodales, at mollis nisl commodo. Ut purus erat, egestas ac dictum ut, sagittis nec nunc. Nulla fermentum, lectus nec posuere suscipit, sem est iaculis nisi, sed consectetur tellus nibh et ex. Nullam a elit ac velit pretium tincidunt vel eget leo. Maecenas non risus eu purus bibendum mattis nec ut neque.
Maecenas faucibus nibh nec molestie volutpat. Cras porttitor gravida sollicitudin. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas nec eros sed elit tempus euismod vitae sodales diam. In elit ex, mattis ut metus vitae, auctor auctor massa. Donec congue ipsum magna, vitae pellentesque ante dictum non. Morbi in tempor metus. Maecenas et diam non velit volutpat sollicitudin. Nam erat dolor, vehicula ut condimentum vel, fringilla sed leo.
Fusce eget maximus augue, eu scelerisque arcu. Cras tincidunt metus in scelerisque sagittis. Fusce ligula diam, placerat sit amet consectetur ut, congue at enim. Maecenas fringilla lacus nec suscipit bibendum. Mauris pellentesque at urna ut congue. Quisque ac lobortis mi. Donec placerat sapien ut nunc mattis, non accumsan orci maximus. Nunc pharetra ex maximus consectetur mollis.
Nullam posuere ut nisl eget malesuada. Praesent sagittis nibh vitae neque ornare, non suscipit dolor rutrum. Cras venenatis arcu non mauris viverra consectetur. Nunc consectetur velit ac dignissim pretium. Suspendisse suscipit tellus consectetur mi condimentum, et maximus elit pretium. Praesent at purus nec erat dictum gravida sed at mi. Interdum et malesuada fames ac ante ipsum primis in faucibus.
Phasellus pulvinar tincidunt posuere. Sed et tincidunt nulla. Sed et sapien lorem. Nam at posuere mi, sed tincidunt lectus. Fusce eleifend nisi nisi, vitae ornare augue tincidunt vel. Maecenas vulputate turpis quis felis porta, sed facilisis ipsum volutpat. Praesent at finibus ipsum. Donec venenatis diam et neque rutrum bibendum. Maecenas eu pharetra mi, et consequat erat. Quisque sed tortor eros. Aliquam bibendum dapibus massa, ac sollicitudin tortor molestie quis. Suspendisse in feugiat odio, ut finibus felis. Etiam luctus sit amet justo vel cursus. Quisque posuere mauris varius mauris mattis accumsan. Maecenas lobortis, quam et volutpat aliquam, eros ante luctus tortor, vel tincidunt magna erat sit amet metus. Praesent in leo mi.
Nulla fermentum interdum scelerisque. Pellentesque gravida blandit dolor, eu porta urna pellentesque eu. Quisque ac mattis ante. Quisque quis neque massa. Nullam eget fermentum augue, vel viverra mauris. Nullam ipsum dui, venenatis ac convallis sit amet, semper vehicula purus. Cras iaculis vitae velit non auctor. Quisque enim leo, feugiat non commodo eget, finibus pellentesque odio. Aenean iaculis, tellus eget venenatis tincidunt, elit mauris consectetur nibh, nec egestas tellus ipsum vitae felis. Vestibulum sed quam in lorem posuere aliquam.
""".strip().split()

###########################################################################

def print_usage():
    print("""
    	./anonymize.py {file} {my_name} {other_name} [anonymous_name]\n
    	{file} - Relative or absolute path to file
    	{my_name} - Your name as it appears in the file
    	{other_name} - Other person's name as it appears in the file
    	[anonymous_name] - (Optional) Name for output of the file
    	""")

if len(sys.argv) not in [4, 5]:
	print_usage()
	exit(1)

file = sys.argv[1]
my_name = sys.argv[2]
other_name = sys.argv[3]
if len(sys.argv) == 5:
	anonymous_name = sys.argv[4]

with open(file) as f:
	data = json.load(f)
	assert len(data['participants']) == 2, 'Can only anonymize conversations of two people currently'
	participants = [participant['name'] for participant in data['participants']]
	assert my_name in participants and other_name in participants, 'my_name and other_name should be participants of conversation'

	for participant in data['participants']:
		participant['name'] = anonymous_name if participant['name'] == other_name else 'Me'

	for message in data['messages']:
		sender_name = message['sender_name']
		sender_name = anonymous_name if sender_name == other_name else 'Me'


	(path, file_name) = os.path.split(file)
	new_filename = '{}/{}-{}'.format(path, anonymous_name, file_name)
	with open(new_filename, 'w') as new_file:
		json.dump(data, new_file, indent=4)
