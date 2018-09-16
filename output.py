import os, sys, unidecode
from time import sleep

from unicodedata import normalize
from termcolor import cprint, colored

CHAR_SIZE = sys.getsizeof('A')
ENCODING = 'utf-8'
DEBUG = True

def debug(message):
	if DEBUG:
		print(message)

def clear_screen():
	slow_print('\033[H\033[J')

def abort(message):
	slow_print(message, 'pause', color='red')
	sys.exit()

def remove_path(path, deepness=-1):
    try:
        if deepness > -1:
            return
        else:
            levels = []
            while deepness <= -1:
                levels.append(path.split('/')[deepness])
                deepness += 1
            return os.path.join(*levels)
    except IndexError:
        return remove_path(path, deepness=deepness+1)

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
	special_chars = {
		'Ã¡': 'á', 
		'Ã ': 'à',
		'Ã©': 'é',
		'Ã‰': 'É',
		'Ã­': 'í',
		'Ã': 'Í',
		'Ã³': 'ó',
		'Ã“': 'Ó',
		'Ãº': 'ú',
		'Ã¼': 'ü',
		'Ã±': 'ñ',
		'Ã‘': 'Ñ',
		'Â´': '\'', 
		'´': '\'',
		b'\xe2\x80\x8e'.decode() : '', # left-to-right-mark
		b'\xe2\x80\x8b'.decode() : '',	# zero-width-space
		'&amp' : '&',
		# 'á': 'a', 
		# 'é': 'e',
		# 'í': 'i',
		# 'ó': 'o',
		# 'ú': 'u',
		# 'ñ': 'n',
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

		# elif c not in suspects and detected:
		# 	debug('back to normal: {}'.format(c))
			# detected = False
			# output_string += new_char.decode(ENCODING)
			# new_char = bytearray()
			# output_string += c

		debug(output_string)

	return output_string

if __name__ == "___main__":

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

	# s = '''FaceÅ£i cunostinÅ£ cu Dumbo, puiul cel mititel i dulce al Doamnei Jumbo, care Ã®i farmec pe to
	# Å£i cei care Ã®l vd... pÃ¢ cÃ¢nd lumea descoper c are nite urechi mari i clpuge.

	# Ajutat de cel mai bun prieten al lui, oricelul Timothy, Dumbo Ã®i d seama Ã®n scurt vreme c
	#  urechile lui spectaculoase Ã®l fac s fie un personaj unic, cu totul deosebit, care poate deveni
	# celebru Ã®n chip de unic elefant zburtor al lumii.'''

	rumeno = '''FaceÅ£i cunostinÅ£Äƒ cu Dumbo, puiul cel mititel ÅŸi dulce al Doamnei Jumbo, care Ã®i farmecÄƒ pe to
	Å£i cei care Ã®l vÄƒd... pÃ¢nÄƒ cÃ¢nd lumea descoperÄƒ cÄƒ are niÅŸte urechi mari ÅŸi clÄƒpÄƒuge.

	Ajutat de cel mai bun prieten al lui, ÅŸoricelul Timothy, Dumbo Ã®ÅŸi dÄƒ seama Ã®n scurtÄƒ vreme cÄ
	ƒ urechile lui spectaculoase Ã®l fac sÄƒ fie un personaj unic, cu totul deosebit, care poate deveni
	celebru Ã®n chip de unic elefant zburÄƒtor al lumii.'''

	deutsch = ''' Nach rund zweimonatigen Dreharbeiten feiert der islamkritische Film der Pro-Bewegung, der von türki
	schen Medien schon als â€œDeutscher Fitnaâ€ bezeichnet wird, im Rahmen einer Pressekonferenz in KÃ¶
	ln am 31. MÃ¤rz seine Premiere. Der 13-minütige Film, der als Werbefilm für den diesjÃ¤hrigen Anti
	-Islamisierungskongress am 9. Mai produziert wurde, zeigt nach dem Vorbild des niederlÃ¤ndischen Isl
	amkritikers Geert Wilders Tabu-Themen wie die Unvereinbarkeit der islamischen Ideologie mit unserem
	Grundgesetz. Aber auch die skandalÃ¶sen Vorkommnisse am 20. September in KÃ¶ln werden in dem Film no
	ch einmal beleuchtet. Türkische Medien wie die auflagenstarke AKP-nahe Tageszeitung â€œZAMANâ€ (di
	e auch in Deutschland kostenlos verteilt wird) oder haber7.com haben bereits vor der VerÃ¶ffentlichu
	ng des islamkritischen deutschen Fitna-Films gewarnt.'''

	print(rumeno)
	print(redecode_unicode_chars(rumeno))
	print()
	# ƒ ord() returns 402 ... out of range
	# Ÿ | size: 76 != 50 | utf_code_point: 376
