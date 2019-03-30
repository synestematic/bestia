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
    ''' returns output of file command '''
    try:
        return magic.from_file(file)
    except:
        return 'Unknown file type'


def say(text):
    ''' mainly intended for use in DARWIN systems '''
    say_binary = command_output('which', 'say').decode().strip()
    if not say_binary:
        return False
    say_binary = say_binary.decode().strip()
    say_command = '{} \'{}\''.format(say_binary, text)
    return system(say_command)


def command_output(*args):
    ''' returns command output as bytes, decode() if needed '''
    try:
        output = check_output(args)
    except CalledProcessError:
        output = b''
    finally:
        return output


def abort(message, pause=1.5):
    echo(message, pause, 'red')
    sysexit(-1)
