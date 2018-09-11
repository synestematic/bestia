import sys, unidecode
from unicodedata import normalize
from termcolor import cprint

CHAR_SIZE = sys.getsizeof('A')
ENCODING = 'utf-16'
DEBUG = True

def debug(message):
	if DEBUG:
		print(message)
		# input()

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

	s = '''FaceÅ£i cunostinÅ£Äƒ cu Dumbo, puiul cel mititel ÅŸi dulce al Doamnei Jumbo, care Ã®i farmecÄƒ pe to
	Å£i cei care Ã®l vÄƒd... pÃ¢nÄƒ cÃ¢nd lumea descoperÄƒ cÄƒ are niÅŸte urechi mari ÅŸi clÄƒpÄƒuge.

	Ajutat de cel mai bun prieten al lui, ÅŸoricelul Timothy, Dumbo Ã®ÅŸi dÄƒ seama Ã®n scurtÄƒ vreme cÄ
	ƒ urechile lui spectaculoase Ã®l fac sÄƒ fie un personaj unic, cu totul deosebit, care poate deveni
	celebru Ã®n chip de unic elefant zburÄƒtor al lumii.'''

	print(s)
	print(redecode_unicode_chars(s))
	print()
	# ƒ ord() returns 402 ... out of range
	# Ÿ | size: 76 != 50 | utf_code_point: 376

