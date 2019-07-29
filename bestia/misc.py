from os import system, popen
from subprocess import check_output, CalledProcessError
import pyperclip

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
    ''' copies text to clipboard '''
    try:
        pyperclip.copy(text)
        return True
    except pyperclip.PyperclipException:
        return False


_SAY_BIN = command_output('which', 'say').decode('UTF-8').strip()

def say(text):
    ''' says text using accessibility voice-over feature
        mainly intended for use with DARWIN systems
    '''
    if not _SAY_BIN:
        raise SayBinMissing('say bin NOT found')
    say_command = '{} \'{}\''.format(_SAY_BIN, text)
    return system(say_command)


_FILE_BIN = command_output('which', 'file').decode('UTF-8').strip()

def file_type(resource):
    ''' returns file_type of input resource
        requires installation of "file" binary
    '''
    if not _FILE_BIN:
        raise FileBinMissing('file bin NOT found')

    proc = popen('{} {}'.format(_FILE_BIN, resource), 'r')

    std_out = proc.read()
    if proc.close() is not None: # return None on success
        return None

    if '(No such file or directory)' in std_out:
        return None

    ignore_first_chars = len(resource) + 2
    return std_out[ignore_first_chars:].strip()
