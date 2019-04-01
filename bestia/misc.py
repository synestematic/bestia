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
    if not _FILE_BIN:
        raise FileBinMissing('file bin NOT found')

    proc = popen('{} {}'.format(_FILE_BIN, file), 'r')

    std_out = proc.read()
    if proc.close() is not None: # return None on success
        return False

    ignore_first_chars = len(file) + 2
    return std_out[ignore_first_chars:].strip()







if __name__ == '__main__':
    print(file_type('/Users/Shared/sulfur_testing/oobe.py'))
    print(file_type('Jenkinsfile'))
