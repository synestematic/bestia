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


def say(text):
	say_binary = command_output('which', 'say')
	if not say_binary:
		return
	else:
		say_binary = say_binary.decode().strip()
		say_command = '{} {}'.format(say_binary, text)
		return system(say_command)


def command_output(*args):
	''' returns command output as bytes, decode() as needed '''
	try:
		return check_output(args)
	except CalledProcessError as x:
		return None


def abort(message, pause=1.5):
	echo(message, pause, 'red')
	sysexit()
