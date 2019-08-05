from sys import getsizeof, stdout
from os.path import join as PATH_JOIN
from os import sep as PATH_SEPARATOR
from os import popen
from time import sleep
from random import randint

from bestia.iterate import string_to_list, iterable_to_string, unique_random_items
from bestia.misc import command_output
from bestia.error import *

CHAR_SIZE = getsizeof('A')
ENCODING = 'utf-8'
RETRO_LAG = 0.00003 #  0.0005

ANSI_SGR_CODES = { # Select Graphic Rendition subset

    'reset': 0,
    'bold': 1,
    'faint': 2,
    'underline': 4,
    'blink': 5,

    'black': 30,    # NOT gray...
    'red': 31,
    'green': 32,
    'yellow': 33,
    'blue': 34,
    'magenta': 35,
    'cyan': 36,
    'white': 37,

    # works NOT
    'frame': 51,
    'circle': 52,
    'overline': 53,
	# dark, reverse, concealed

}


def ansi_esc_seq(x):
    try:
        return '\033[{}m'.format(
            ANSI_SGR_CODES[x]
        )
    except KeyError:
        raise UndefinedAnsiSequence(x)


def dquoted(s):
    return '"{}"'.format(s)


def clear_screen():
    stdout.write('\033[H')
    stdout.write('\033[J')
    stdout.flush()


def obfuscate_random_chars(input_string, amount=None, obfuscator='_'):
    ''' returns input string with amount of random chars obfuscated '''
    amount = len(input_string) - 4 if not amount or amount >= len(input_string) else amount

    string_indexes = [
        i for i in range(
            len(str(input_string))
        )
    ]

    string_as_list = string_to_list(input_string)
    for random_index in unique_random_items(string_indexes, amount):
        string_as_list[random_index] = obfuscator

    return iterable_to_string(string_as_list)


_STTY_BIN = command_output('which', 'stty').decode(ENCODING).strip()


def tty_size():
    ''' dinamically returns size of current terminal  '''
    if not _STTY_BIN:
        raise SttyBinMissing('stty bin NOT found')

    proc = popen('{} size'.format(_STTY_BIN), 'r')
    rows, columns = proc.read().split()
    return (int(rows), int(columns))


def tty_rows():
    ''' dinamically returns rows of current terminal '''
    return tty_size()[0]


def tty_columns():
    ''' dinamically returns columns of current terminal '''
    return tty_size()[1]


class Row(object):

    def __init__(self, *input_strings, width=False):
        self.__output = ''
        self.__fixed_width = width
        self.__fstrings = []
        for s in input_strings:
            self.append(s)
        # self.assign_spaces()

    def assign_spaces(self):
        spaces_left = self.width

        # remove fixed_fs sizes
        for fs in self.fixed_fstrings():
            spaces_left -= len(fs)
        # what if they remove more than instantiated?

        # gather adaptive_fs
        adaptive_fs_count = len(
            [ fs for fs in self.adaptive_fstrings() ]
        )
        if not adaptive_fs_count:
            return

        # calculate individual size for each adaptive_fs + any spaces left
        adaptive_fs_size, spaces_left = divmod(
            spaces_left, adaptive_fs_count
        )

        # resize adaptive_fs
        for i, _ in enumerate(self.__fstrings):
            if not self.__fstrings[i].fixed_size:
                self.__fstrings[i].resize(
                    adaptive_fs_size
                )

        # deal spaces_left to adaptive_fs 1 by 1
        while spaces_left:

            for i, _ in enumerate(self.__fstrings):

                if self.__fstrings[i].fixed_size:
                    continue

                self.__fstrings[i].resize(
                    len(self.__fstrings[i]) +1
                )

                spaces_left -= 1
                if not spaces_left:
                    break

    @property
    def width(self):
        return self.__fixed_width if self.__fixed_width else tty_columns()

    @property
    def output(self):
        self.assign_spaces()
        for fs in self.__fstrings:
            self.__output = self.__output + '{}'.format(fs)
        return self.__output

    def fixed_fstrings(self):
        for fs in self.__fstrings:
            if fs.fixed_size:
                yield fs

    def adaptive_fstrings(self):
        for fs in self.__fstrings:
            if not fs.fixed_size:
                yield fs

    def append(self, s):
        self.__fstrings.append(
            FString(s) if type(s) != FString else s
        )

    def echo(self, *args, **kwargs):
        echo(self, *args, **kwargs)

    def __str__(self):
        return self.output


class echo(object):

    modes = (
        # first item is default
        'modern',
        'retro',
        'raw',
    )

    def __init__(self, input_string='', fg='', mode='modern'):

        self.__output = input_string

        self.__fg_color = ''
        if fg in ANSI_SGR_CODES.keys():
            self.__fg_color = fg

        self.__mode = self.modes[0]
        if mode in self.modes:
            self.__mode = mode

        self()
        
    def __call__(self):
        screen_str(
            self.__output,
            lag = RETRO_LAG if self.__mode == 'retro' else 0,
            random_lag = 100 if self.__mode == 'retro' else 1,
            color = self.__fg_color
        )
        if self.__mode != 'raw':
            screen_str()


def screen_chr(char=' ', lag=0, random_lag=1):
    random_multiplier = randint(1, random_lag)
    sleep(lag *random_multiplier)
    stdout.write(char)
    stdout.flush()


def screen_str(string='\n', color=None, lag=0, random_lag=1):

    try:
        exception = None
        if color in ANSI_SGR_CODES.keys():
            screen_str(ansi_esc_seq(color))

        for c in str(string):
            screen_chr(c, lag, random_lag)

    except Exception as x:
        exception = x

    finally:
        if color in ANSI_SGR_CODES.keys():
            screen_str(ansi_esc_seq('reset'))
        if exception:
            raise exception


class FString(object):

    def __init__(self, input_string='', size=False, align='l', pad=None, colors=[], fx=[]):

        self.fixed_size = True if size else False

        self.__input_string = ''
        self.append(input_string)

        self.resize(size)

        self.__pad = pad

        self.align = align			# l, r, cl, cr
        self.colors = colors        # black, red, green, yellow, blue, magenta, cyan, white
        self.fx = fx				# bold, dark, underline, blink, reverse, concealed

    def resize(self, size=None):
        self.__output_size = int(size) if size else self.input_size # desired len of output


    def filter_utf_chars(self, string):
        '''
            filters out chars that can cause misalignments
            because made of more than a byte... makes sense?
        '''
        return bytearray(
            ord(c.encode(ENCODING)) for c in replace_special_chars(
                string
            ) if len(c.encode(ENCODING)) == 1
        ).decode(ENCODING)

    def append(self, string):

        self.__input_string = '{}{}'.format(
            self.__input_string,
            self.filter_utf_chars(string),
            # string
        )

        self.set_input_size()

    def set_input_size(self):
        # calculate input_string length without color bytes
        ignore_these = [
            b'\xe2\x80\x8e', # left-to-right-mark
            b'\xe2\x80\x8b', # zero-width-space
        ]
        color_start_byte = b'\x1b'
        color_end_byte = b'm'
        self.input_size = 0
        add = True
        for char in self.__input_string:
        # when encoding input_string into byte_string: byte_string will not necessarily have the same amount of bytes as characters in the input_string ( some characters will be made of several bytes ), therefore, the input_string should not be encoded but EACH INDIVIDUAL CHAR should
            byte = char.encode(ENCODING)
            if byte == color_start_byte and add:
                add = False
                continue
            elif byte == color_end_byte and not add:
                add = True
                continue
            if add and byte not in ignore_these:
                self.input_size += 1

    def __str__(self):
        return self.output

    def __len__(self):
        return self.__output_size

    def __add__(self, other):
        return self.output + '{}'.format(other)

    def echo(self, *args, **kwargs):
        return echo(self, *args, **kwargs)

    @property
    def __pad(self):
        return self.__pad_char

    @__pad.setter
    def __pad(self, p):
        self.__pad_char = str(p)[0] if p else ' '

    @property
    def __sml_pad(self):
        exact_half, excess = divmod(
            self.__output_size -self.input_size, 2
        )
        return self.__pad * exact_half

    @property
    def __big_pad(self):
        exact_half, excess = divmod(
            self.__output_size -self.input_size, 2
        )
        return self.__pad * (exact_half +excess)

    @property
    def output(self):
        self.__output = self.__input_string
        self.__output = self.__output.replace("\t", ' ') # can't afford to have tabs in output as they are never displayed the same
        if self.input_size > self.__output_size:
            self.resize_output()
        self.color_output()
        if self.__output_size > self.input_size:
            self.align_output()
        return self.__output

    def resize_output(self):
        delta_len = self.input_size - self.__output_size
        self.__output = self.__output[:0 -delta_len]

    def align_output(self):
        # assumes "l" to avoid nasty fail...
        # but I should Raise an Exception if I pass invalid value "w"
        uno, due, tre = self.__output, self.__sml_pad, self.__big_pad

        if self.align == 'cl' or self.align == 'lc' or self.align == 'c':
            uno, due, tre = self.__sml_pad, self.__output, self.__big_pad
        elif self.align == 'cr' or self.align == 'rc':
            uno, due, tre = self.__big_pad, self.__output, self.__sml_pad
        elif self.align == 'r':
            uno, due, tre = self.__sml_pad, self.__big_pad, self.__output

        self.__output = uno + due + tre

    def color_output(self):
        if len(self.colors) == 1 and self.colors[0] in ANSI_SGR_CODES.keys() :

            for f in self.fx:
                self.__output = ansi_esc_seq(f) +self.__output
            # self.__output = colored(self.__output, self.colors[0], attrs=self.fx)
            self.__output = '{}{}{}'.format(
                ansi_esc_seq(self.colors[0]),
                self.__output,
                ansi_esc_seq('reset'),
            )

        # elif len(self.colors) == 2:
        #     self.__output = colored(self.__output, self.colors[0], self.colors[1], attrs=self.fx)


def expand_seconds(input_seconds, output_string=False):
    ''' expands input_seconds into a dict with as less keys as needed: 
            seconds, minutes, hours, days, weeks

        can also return string
    '''
    expanded_time = {}
    expanded_time['minutes'], expanded_time['seconds'] = divmod(input_seconds, 60)
    expanded_time['hours'], expanded_time['minutes'] = divmod(expanded_time['minutes'], 60)
    expanded_time['days'], expanded_time['hours'] = divmod(expanded_time['hours'], 24)
    expanded_time['weeks'], expanded_time['days'] = divmod(expanded_time['days'], 7)

    if output_string:
        seconds = ' {} seconds'.format(round(expanded_time['seconds'], 2))
        minutes = ' {} minutes'.format(int(expanded_time['minutes'])) if expanded_time['minutes'] else ''
        hours = ' {} hours'.format(int(expanded_time['hours'])) if expanded_time['hours'] else ''
        days = ' {} days'.format(int(expanded_time['days'])) if expanded_time['days'] else ''
        weeks = ' {} weeks'.format(int(expanded_time['weeks'])) if expanded_time['weeks'] else ''
        return '{}{}{}{}{}'.format(weeks, days, hours, minutes, seconds).strip()

    return expanded_time


def remove_path(input_path, depth=-1):
    ''' removes directories from file path
        supports various levels of dir removal
    '''
    try:
        if depth > 0:
            depth = 0 - depth
        elif depth == 0:
            depth = -1
        levels = []
        while depth <= -1:
            levels.append(input_path.split(PATH_SEPARATOR)[depth])
            depth += 1
        return PATH_JOIN(*levels)
    except IndexError:
        return remove_path(input_path, depth=depth+1)


def replace_special_chars(t):
    ''' https://www.i18nqa.com/debug/utf8-debug.html
        some of the chars here im not sure are correct,
        check dumbo dublat romana translation
    '''
    special_chars = {
        # 'Äƒ': 'Ã',
        # 'Äƒ': 'ă',
        'Ã¢': 'â',
        'Ã¡': 'á', 'ã¡': 'á',
        'Ã ': 'à',
        'Ã¤': 'ä',
        'Å£': 'ã',
        # 'ÅŸ': 'ß',
        'ÃŸ': 'ß',
        'Ã©': 'é', 'ã©': 'é',
        'Ã¨': 'è',
        'Ã' : 'É', 'Ã‰': 'É',
        'Ã­': 'í',
        'Ã': 'Í',
        # 'Ã®': 'î',
        'Ã³': 'ó',
        'Ã“': 'Ó',
        'Ã¶': 'ö',
        'Ãº': 'ú',
        'Ã¹': 'ù',
        'Ã¼': 'ü',
        'Ã±': 'ñ',
        'Ã‘': 'Ñ',
        'Â´': '\'',
        '´': '\'',
        'â€ž': '“',
        'â€œ': '”',
        'â€¦': '…',
        b'\xe2\x80\x8e'.decode(ENCODING) : '', # left-to-right-mark
        b'\xe2\x80\x8b'.decode(ENCODING) : '',	# zero-width-space
        '&amp' : '&',
        '&;': '&',
        '【': '[',
        '】': ']',
        'â€“': '-',
        '⑥': '6',
    }

    for o, i in special_chars.items():
        t = str(t).replace(o, i)
    return t
