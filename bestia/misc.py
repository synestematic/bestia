from os import system
from sys import exit as sysexit
from subprocess import check_output, CalledProcessError
import pyperclip
import magic

from bestia.output import echo

def copy_to_clipboard(text):
	try:
		pyperclip.copy(text)
		return True
	except pyperclip.PyperclipException:
		return False


def file_type(file):
    try:
        return magic.from_file(file)
    except:
        return 'Unknown file type'



def command_output(*args):
	''' returns command output as bytes, decode() as needed '''
	try:
		return check_output(args)
	except CalledProcessError as x:
		return None


def abort(message, pause=1.5):
	echo(message, pause, 'red')
	sysexit()
