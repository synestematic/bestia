import os, sys, unidecode
from time import sleep

from pprint import pprint
from unicodedata import normalize
from termcolor import cprint, colored

CHAR_SIZE = sys.getsizeof('A')
ENCODING = 'utf-8'
DEBUG = True

def expand_seconds(seconds, string=False):
	minutes, seconds = divmod(seconds, 60)
	hours, minutes = divmod(minutes, 60)
	days, hours = divmod(hours, 24)
	if string:
		seconds_msg = ' {} seconds'.format(round(seconds, 2))
		minutes_msg = ' {} minutes'.format(int(minutes)) if minutes else ''
		hours_msg = ' {} hours'.format(int(hours)) if hours else ''
		days_msg = ' {} days'.format(int(days)) if days else ''
		string = '{}{}{}{}'.format(days_msg, hours_msg, minutes_msg, seconds_msg)
		string = string.strip()
		return string
	else:
		return days, hours, minutes, seconds

def debug(message):
	if DEBUG:
		print(message)

def clear_screen():
	echo('\033[H\033[J')

def abort(message, pause=2):
	echo(message, pause, 'red')
	sys.exit()

def remove_path(input_path, deepness=-1):
	try:
		if deepness > 0:
			deepness = 0 - deepness
		elif deepness == 0:
			deepness = -1
		levels = []
		while deepness <= -1:
			levels.append(input_path.split(os.sep)[deepness])
			deepness += 1
		return os.path.join(*levels)
	except IndexError:
		return remove_path(input_path, deepness=deepness+1)

def flatten_path(b, d=1):
	rest, last = os.path.split(b)
	while last:
	# if d <= 1:
		cprint(rest, 'green')
		cprint(last, 'red')
		input()
		flatten_path(rest, d=d-1)


def slow_print(string='', speed='slow', color=None):
	if color:
		string = colored(string, color)
	print(string)
	factor = 0.7
	if speed is 'slow':
		s = 0.02
	elif speed is 'slower':
		s = 0.07
	elif speed is 'slowest':
		s = 0.12
	elif speed is 'pause':
		s = 0.9
	sleep(factor * s)


class echo():

	time_factor = 0.7

	def __init__(s, input='', *args):
		s.output = input
		s.input_args = args

		s.set_pause()
		s.set_colors()
		s()
		
	def __call__(s):
		if type(s.output) == dict:
			input('im a dict')
			pprint(colored(s.output, 'red'))
		else:
			print(s.output)
		sleep(s.time_factor * s.pause)

	def set_colors(s):
		s.fg_color = None
		s.bg_color = None

		available_colors = ( 'red', 'green', 'yellow', 'blue', 'grey', 'white', 'cyan', 'magenta' )
		s.input_colors = [arg for arg in s.input_args if arg in available_colors]

		if len(s.input_colors) < 1:
			return
		elif len(s.input_colors) == 1:
			s.fg_color = s.input_colors[0]
			s.output = colored(s.output, s.fg_color)
		elif len(s.input_colors) > 1:
			s.fg_color = s.input_colors[0]
			s.bg_color = s.input_colors[1]
			s.output = colored(s.output, s.fg_color, 'on_' + s.bg_color)

	def set_pause(s):
		s.pause = 0.0
		for arg in s.input_args:
			if type(arg) is int or type(arg) is float:
				s.pause = arg

class FString():
	def __init__(self, s, space=False, align='l', pad=' ', colors=[], xtras=[]):
		self.pad = pad
		self.input_string = str(s)
		self.set_input_size() # original len of input_string without considering color bytes
		self.output_size = int(space) if space else self.input_size	# desired len of output_string
		self.align = align										# l, r, cl, cr
		self.set_colors(colors) 								# grey, red, green, yellow, blue, magenta, cyan, white
		self.xtras = xtras										# bold, dark, underline, blink, reverse, concealed

	def set_input_size(self):
		# calculates input string length without color bytes
		ignore_these = [
			b'\xe2\x80\x8e', # left-to-right-mark
			b'\xe2\x80\x8b', # zero-width-space
		]
		color_start_byte = b'\x1b'
		color_end_byte = b'm'
		self.input_size = 0
		add = True
		for char in self.input_string:
		# when encoding input_string into byte_string: byte_string will not necessarily have the same amount of bytes as characters in the input_string ( some characters will be made of several bytes ), therefore, the input_string should not be encoded but EACH INDIVIDUAL CHAR should
		# for byte in self.input_string.encode():
			byte = char.encode()
			if byte == color_start_byte and add:
				add = False
				continue
			elif byte == color_end_byte and not add:
				add = True
				continue
			if add and byte not in ignore_these:
				self.input_size += 1

	def __str__(self):
		self.set_ouput_string()
		return self.output_string

	def set_colors(self, colors):
		if len(colors) > 1:
			colors[1] = 'on_{}'.format(colors[1])
		self.colors = colors

	def set_pads(self):
		delta_length = self.output_size - self.input_size
		excess = delta_length % 2
		exact_half = int((delta_length - excess) / 2)
		self.small_pad = self.pad * exact_half
		self.big_pad = self.pad * (exact_half + excess)

	def set_ouput_string(self):
		self.output_string = self.input_string
		self.output_string = self.output_string.replace("\t", ' ') # can't afford to have tabs in output_string as they are never displayed the same
		if self.input_size > self.output_size:
			self.resize_output_string()
		self.color_output_string()
		if self.output_size > self.input_size:
			self.align_output_string()

	def resize_output_string(self):
		delta_length = self.input_size - self.output_size
		self.output_string = self.output_string[:0-delta_length]

	def align_output_string(self):
		self.set_pads()
		uno, due, tre = self.output_string, self.small_pad, self.big_pad
		# ASSUME "l" to avoid nasty fail...
		# but I should Raise an Exception if I pass invalid value "w"
		if self.align == 'cl' or self.align == 'c':
			uno, due, tre = self.small_pad, self.output_string, self.big_pad
		elif self.align == 'cr':
			uno, due, tre = self.big_pad, self.output_string, self.small_pad
		elif self.align == 'r':
			uno, due, tre = self.small_pad, self.big_pad, self.output_string

		self.output_string = '{}{}{}'.format(uno, due, tre)

	def color_output_string(self):
		if len(self.colors) == 1:
			self.output_string = colored(self.output_string, self.colors[0], attrs=self.xtras)
		elif len(self.colors) == 2:
			self.output_string = colored(self.output_string, self.colors[0], self.colors[1], attrs=self.xtras)


def replace_special_chars(t):
	'''
	https://www.i18nqa.com/debug/utf8-debug.html
	some of the chars here im not sure are correct,
	according to dumbo dublat romana translation
	'''
	special_chars = {
		# 'Äƒ': 'Ã',
		# 'Äƒ': 'ă',

		'Ã¢': 'â',
		'Ã¡': 'á',
		'Ã ': 'à',
		'Ã¤': 'ä',
		'Å£': 'ã',

		# 'ÅŸ': 'ß',

		'ÃŸ': 'ß',
		'Ã©': 'é',
		'Ã¨': 'è',
		'Ã‰': 'É',
		'Ã­': 'í',
		'Ã': 'Í',

		# 'Ã®': 'î',

		'Ã³': 'ó',
		'Ã“': 'Ó',
		'Ã¶': 'ö',
		'Ãº': 'ú',
		'Ã¹': 'ù',
		'Ã¼': 'ü',
		'Ã±': 'ñ',
		'Ã‘': 'Ñ',
		'Â´': '\'',
		'´': '\'',
		'â€ž': '“',
		'â€œ': '”',
		'â€¦': '…',
		b'\xe2\x80\x8e'.decode() : '', # left-to-right-mark
		b'\xe2\x80\x8b'.decode() : '',	# zero-width-space
		'&amp' : '&',
		'&;': '&',
		'【': '[',
		'】': ']',
		'â€“': '-',
	}
	for o, i in special_chars.items():
		t = t.replace(o, i)
	return t

def flatten_string(string):
	old_char = ''
	new_char = bytearray()
	for c in string:
		b = bytearray(c, ENCODING)
		if sys.getsizeof(c) != CHAR_SIZE:
			old_char += c
			unicode_code_point = ord(c) # int
			new_char.append(unicode_code_point)
	new_char = new_char.decode()
	return string.replace(old_char, new_char)


def flatten_char(c):
	size = sys.getsizeof(c)
	if size != CHAR_SIZE:
		color = 'red'
		symbol = '!='
	else:
		color = 'green'
		symbol = '=='
	cprint('{} | size: {} {} {} | utf_code_point: {}'.format(c, size, symbol, CHAR_SIZE, ord(c)), color)


def redecode_unicode_chars(input_string):
	suspects = [
		'Ã', 
		'Â',
		'Å',
		'Ä',
		# 'Ã®',
	]
	output_string = ''
	detected = False
	new_char = bytearray()
	for c in input_string:
		size = sys.getsizeof(c)
		# CHAR SIZE IS NOT A GOOD IDICATOR OF WHEN WE WILL FIND
		# if size == CHAR_SIZE and not detected:
		if c not in suspects and not detected:
			debug('standard char: {}'.format(c))
			output_string += c

		elif c in suspects and not detected:
			debug('1 suspect char: {}'.format(c))
			flatten_char(c)
			detected = True
			unicode_code_point = ord(c) # int
			new_char.append(unicode_code_point)

		elif size != CHAR_SIZE and detected:
			debug('2 suspect char: {}'.format(c))
			flatten_char(c)
			unicode_code_point = ord(c) # int
			new_char.append(unicode_code_point)

			detected = False
			output_string += new_char.decode(ENCODING)
			new_char = bytearray()
			# this assumes that I will be encoding chars in chunks of length 2... is that fair ????

		# debug(output_string)
	return output_string

if __name__ == "__main__":


	d = {
		'a': 1,
		'a2': {
			'b5': 29,
			'b2': 25,
			'bp': 2,
		},
		'a3': 1,
		'a4': 1,
		'a5': 1,
		'a6': 1,
		'a7': 1,
	}


	# Dumbo DVDRip [dublat romana]
	# zburător
	# cunoştinţă
	# descoperă
	rumeno = '''Faceãi cunostinãÄƒ cu Dumbo, puiul cel mititel ÅŸi dulce al Doamnei Jumbo, care Ã®i farmecÄƒ pe to
ãi cei care Ã®l vÄƒd... pânÄƒ când lumea descoperÄƒ cÄƒ are niÅŸte urechi mari ÅŸi clÄƒpÄƒuge.

Ajutat de cel mai bun prieten al lui, ÅŸoricelul Timothy, Dumbo Ã®ÅŸi dÄƒ seama Ã®n scurtÄƒ vreme cÄ
ƒ urechile lui spectaculoase Ã®l fac sÄƒ fie un personaj unic, cu totul deosebit, care poate deveni
celebru Ã®n chip de unic elefant zburÄƒtor al lumii.'''

	print(replace_special_chars(rumeno))
	# ƒ ord() returns 402 ... out of range
	# Ÿ | size: 76 != 50 | utf_code_point: 376

	sys.exit()

	def cp_string_to_char(cp_string):
		output_char = bytearray()
		for char in cp_string:
			unicode_code_point = ord(char)
			cprint('{}: {}'.format(char, unicode_code_point), 'green')
			output_char.append(unicode_code_point)
		cprint('{}: {}'.format(output_char, type(output_char)), 'blue')
		output_char = output_char.decode()
		return output_char


	special_chars = {
		# 'Ã©': 'é', # 195, 169, 233
		# 'Ã‰': 'É', # 195, 8240, 201
	}

	# for yo in special_chars.keys():
	# 	# print(redecode_unicode_chars(yo))
	# 	print(cp_string_to_char(yo))

	def reverse_stuff(input_char):
		bs = input_char.encode()
		for b in bs:
			print(b)
			print(hex(b))
			print(chr(b))
			print()

	# yo = 'Ã'
	# bla = yo.encode()
	# print(bla)
	# foo = ord(yo) 
	# print(foo)

	# yo = '‰'
	# bla = yo.encode()
	# print(bla)
	# print(chr(8240))

	yo = 'É'
	# bla = yo.encode()
	# print(bla)
	# print(ord(yo))

	reverse_stuff(yo)


# U+0420, U+205AC - codepoint
# 0420, c3a9, E2808B - codepoint as hex. (When hex is decodable as UTF8, such as c3a9 for U+E9, we add such a link)












	# s = 'NewellÂ´s'
	# print(s)
	# print(redecode_unicode_chars(s))
	# print()
	# s = 'Real Madrid vs AtlÃ©tico de Madrid'
	# print(s)
	# print(redecode_unicode_chars(s))
	# print()
	# s = 'Macarálo'
	# print(s)
	# print(redecode_unicode_chars(s))
	# print()
	# s = 'ú'
	# print(s)
	# print(redecode_unicode_chars(s))
	# print()
	# s = 'Núñez'
	# print(s)
	# print(redecode_unicode_chars(s))
	# print()
	# s = 'EspaÃ±oletación'
	# print(s)
	# print(redecode_unicode_chars(s))
	# print()

	# how to separate ú from © ??
	# Å£Äƒ	are these 1 or 2 chars ? surely not 1 ... ?
