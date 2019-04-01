from os import system
from subprocess import check_output, CalledProcessError
import pyperclip
import magic

from bestia.error import *

def command_output(*args):
    ''' returns command output as bytes, decode() if needed '''
    try:
        output = check_output(args)
    except CalledProcessError:
        output = b''
    finally:
        return output


def copy_to_clipboard(text):
    ''' tries to copy text to clipboard '''
    try:
        pyperclip.copy(text)
        return True
    except pyperclip.PyperclipException:
        return False


_SAY_BIN = command_output('which', 'say').decode().strip()

def say(text):
    ''' says text using accessibility voice-over feature
        mainly intended for use in DARWIN systems
    '''
    if not _SAY_BIN:
        raise SayBinMissing('say bin NOT found')
    say_command = '{} \'{}\''.format(_SAY_BIN, text)
    return system(say_command)


_FILE_BIN = command_output('which', 'file').decode().strip()

def file_type(file):
    ''' returns output of file command '''
    try:
        if not _FILE_BIN:
            raise FileBinMissing('file bin NOT found')
        return magic.from_file(file)
    except Exception as x:
        return str(x)

