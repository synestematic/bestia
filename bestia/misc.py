import pyperclip
import magic
from os import system

def copy_to_clipboard(text):
	try:
		pyperclip.copy(text)
		return True
	except pyperclip.PyperclipException:
		return False


def items_are_equal(iterable):
   return iterable[1:] == iterable[:-1]


def file_type(file):
    try:
        return magic.from_file(file)
    except:
        return 'Unknown file type'


def say(string):
	return system('say {}'.format(string))
