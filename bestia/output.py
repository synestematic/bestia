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

class AnsiSgrCode(object):

    def __init__(self, name, code):
        self.name = name
        self.code = code


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

ANSI_CLR_VALUES = tuple( [ n for n in range(30, 50) ] )

def validate_ansi(ansi_name, ansi_type):

    if not ansi_name:
        return

    if ansi_name not in ANSI_SGR_CODES:
        raise UndefinedAnsiSequence(ansi_name)

    if ansi_type == 'color':
        if ANSI_SGR_CODES[ansi_name] not in ANSI_CLR_VALUES:
            raise InvalidColor(ansi_name)

    elif ansi_type == 'fx':
        if ANSI_SGR_CODES[ansi_name] in ANSI_CLR_VALUES:
            raise InvalidFx(ansi_name)

    return ansi_name


def ansi_esc_seq(fx, offset=0):
    try:
        return '\033[{}m'.format(
            ANSI_SGR_CODES[fx] + offset
        )
    except KeyError:
        raise UndefinedAnsiSequence(fx)


def dquoted(s):
    return '"{}"'.format(s)


def clear_screen():
    stdout.write('\033[H')
    stdout.write('\033[J')
    stdout.flush()


def obfuscate_random_chars(input_string, amount=None, obfuscator='_'):
    ''' returns input string with amount of random chars obfuscated '''
    amount = len(input_string) - 4 if not amount or amount >= len(input_string) else amount

    string_indecae = [
        i for i in range(
            len(str(input_string))
        )
    ]

    string_as_list = string_to_list(input_string)
    for random_index in unique_random_items(string_indecae, amount):
        string_as_list[random_index] = obfuscator

    return iterable_to_string(string_as_list)


_STTY_BIN = command_output('which', 'stty').decode(ENCODING).strip()


def tty_size():
    ''' returns dynamic size of current terminal  '''
    if not _STTY_BIN:
        raise MissingBinary('stty binary not found')

    proc = popen('{} size'.format(_STTY_BIN), 'r')
    rows, columns = proc.read().split()
    return (int(rows), int(columns))


def tty_rows():
    ''' returns dynamic rows of current terminal '''
    return tty_size()[0]


def tty_columns():
    ''' returns dynamic columns of current terminal '''
    return tty_size()[1]


class Row(object):

    '''a string with width == terminal size (unless otherwise specified). Instantiate a Row object with as many str|FString items as you like and it will keep its width constant by cropping/aligning items without a fixed_size'''

    def __init__(self, *items, width=False):
        self.__output = ''
        self.__fixed_width = width
        self.__fstrings = []
        for item in items:
            self.append(item)

    def __len__(self):
        return self.__fixed_width if self.__fixed_width else tty_columns()

    def assign_spaces(self):
        spaces_left = self.width

        # remove fixed_fs sizes
        for fs in self.fixed_fstrings():
            spaces_left -= len(fs)

        # gather adaptive_fs
        adaptive_fs_count = len(
            [ fs for fs in self.adaptive_fstrings() ]
        )
        if not adaptive_fs_count:
            return

        # if spaces_left < 1:
            ### CROP if removed more spaces than available?
            # return

        ### ALIGN

        # calculate individual size for each adaptive_fs + any spaces left
        adaptive_fs_size, spaces_left = divmod(
            spaces_left, adaptive_fs_count
        )

        # resize adaptive_fs
        for i, _ in enumerate(self.__fstrings):
            if not self.__fstrings[i].fixed_size:
                self.__fstrings[i].size = adaptive_fs_size

        # deal spaces_left to adaptive_fs 1 by 1
        while spaces_left:

            for i, _ in enumerate(self.__fstrings):

                if self.__fstrings[i].fixed_size:
                    continue

                self.__fstrings[i].size += 1

                spaces_left -= 1
                if not spaces_left:
                    break

    @property
    def width(self):
        return len(self)

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

    def __init__(self, input_string='', *args, mode='modern'):

        self.__output = input_string

        self.__fg_color = ''
        for a in args:
            if a in ANSI_SGR_CODES.keys():
                self.__fg_color = a

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

    def __init__(self, init_string='', size=0, pad=' ', align='l', fg='', bg='', fx=[]):

        self.fixed_size = True if size else False

        self.__input_string = ''
        self.append(init_string)

        self.__output_size = self.__input_size
        self.size = size

        self.__pad = ' '
        self.pad = pad

        # l, r, c, cl, lc, cr, rc
        self.__align = 'l'
        self.align = align

        # black, red, green, yellow, blue, magenta, cyan, white
        self.__fg_color = ''
        self.fg_color = fg

        self.__bg_color = ''
        self.bg_color = bg

        # bold, dark, underline, blink, reverse, concealed
        self.__fx = []
        self.fx = fx


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
            # string,
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
        self.__input_size = 0
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
                self.__input_size += 1

    def __str__(self):
        return self.output

    def __len__(self):
        return self.__output_size if self.__output_size > 0 else 0

    def __add__(self, other):
        return self.output + '{}'.format(other)

    def echo(self, *args, **kwargs):
        return echo(self, *args, **kwargs)

    @property
    def size(self):
        return len(self)

    @size.setter
    def size(self, s=None):
        self.__output_size = int(s) if s else self.__input_size # desired len of output


    @property
    def pad(self):
        return self.__pad

    @pad.setter
    def pad(self, p):
        self.__pad = str(p)[0] if p else ' '

    @property
    def align(self):
        return self.__align

    @align.setter
    def align(self, a):
        if a not in ('l', 'r', 'c', 'lc', 'cl', 'rc', 'cr'):
            raise UndefinedAlignment(a)
        self.__align = a

    @property
    def fg_color(self):
        return self.__fg_color

    @property
    def bg_color(self):
        return self.__bg_color

    @property
    def fx(self):
        return self.__fx

    @fg_color.setter
    def fg_color(self, c):
        if validate_ansi(c, ansi_type='color'):
            self.__fg_color = c

    @bg_color.setter
    def bg_color(self, c):
        if validate_ansi(c, ansi_type='color'):
            self.__bg_color = c

    @fx.setter
    def fx(self, fx):
        self.__fx = []
        for f in fx:
            if validate_ansi(f, ansi_type='fx'):
                self.__fx.append(f)


    @property
    def __big_pad(self):
        exact_half, excess = divmod(
            self.__output_size - self.__input_size, 2
        )
        return self.pad * (exact_half + excess)

    @property
    def __sml_pad(self):
        exact_half, excess = divmod(
            self.__output_size - self.__input_size, 2
        )
        return self.pad * exact_half

    @property
    def output(self):

        self.__output = self.__input_string.replace('\t', ' ') # can't afford to have tabs in output as they are never displayed the same

        if self.__input_size > self.__output_size:
            self.__crop_output()

        if self.__fg_color or self.__bg_color or self.__fx:
            self.__paint_output()

        if self.__output_size > self.__input_size:
            self.__align_output()

        return self.__output


    def __crop_output(self):
        delta_len = self.__input_size - self.__output_size
        self.__output = self.__output[:0 - delta_len]


    def __paint_output(self):

        for f in self.__fx:
            self.__output = ansi_esc_seq(f) + self.__output

        if self.__fg_color:
            self.__output = ansi_esc_seq(self.__fg_color) + self.__output

        if self.__bg_color:
            # background color range is +10 respect to foreground color
            self.__output = ansi_esc_seq(self.__bg_color, offset=10) + self.__output

        self.__output = self.__output + ansi_esc_seq('reset')


    def __align_output(self):

        if self.__align == 'l':
            self.__output = self.__output + self.__sml_pad + self.__big_pad

        elif self.__align == 'r':
            self.__output = self.__sml_pad + self.__big_pad + self.__output

        elif self.__align in ('c', 'cl', 'lc'):
            self.__output = self.__sml_pad + self.__output + self.__big_pad

        elif self.__align in ('cr', 'rc'):
            self.__output = self.__big_pad + self.__output + self.__sml_pad


def expand_seconds(input_seconds, output=dict):
    ''' expands input_seconds into a dict with as less keys as needed:
            seconds, minutes, hours, days, weeks

        can also return string
    '''
    time = {}
    time['minutes'], time['seconds'] = divmod(input_seconds, 60)
    time['hours'], time['minutes'] = divmod(time['minutes'], 60)
    time['days'], time['hours'] = divmod(time['hours'], 24)
    time['weeks'], time['days'] = divmod(time['days'], 7)

    if output == str:
        seconds = ' {} seconds'.format(round(time['seconds'], 2))
        minutes = ' {} minutes'.format(int(time['minutes'])) if time['minutes'] else ''
        hours = ' {} hours'.format(int(time['hours'])) if time['hours'] else ''
        days = ' {} days'.format(int(time['days'])) if time['days'] else ''
        weeks = ' {} weeks'.format(int(time['weeks'])) if time['weeks'] else ''
        return '{}{}{}{}{}'.format(weeks, days, hours, minutes, seconds).strip()

    return time


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

a = Row(width=12)

print(
    len(a)
)
