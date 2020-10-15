from os import system, popen
from subprocess import check_output, CalledProcessError
import pyperclip

from bestia.error import *

def copy_to_clipboard(text):
    ''' copies text to clipboard '''
    try:
        pyperclip.copy(text)
        return True
    except pyperclip.PyperclipException:
        return

