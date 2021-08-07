import sys
import os
import time
import random

from .iterate import iterable_to_string, unique_random_items
from .error import *

ANSI_ESC = '\033' # octal form   aka 0x1B, 27, '\e'

CSI_CODES = {
    # https://en.wikipedia.org/wiki/ANSI_escape_code#CSI_sequences
    'CUU'  : 'A', # Cursor Up
    'CUD'  : 'B', # Cursor Down
    'CUF'  : 'C', # Cursor Forward
    'CUB'  : 'D', # Cursor Back
    'CUP'  : 'H', # Cursor Position
    'ED'   : 'J', # Erase in Display
    'SGR'  : 'm', # Select Graphic Rendition
    'DECSM': 'h', # show   DECTCEM (DEC text cursor enable mode)
    'DECRM': 'l', # remove DECTCEM (DEC text cursor enable mode)
}

SGR_CODES = {
    'reset':     0,
    'bold':      1,    # bolds  ONLY fg, NOT ul
    'faint':     2,    # faints ONLY fg, NOT ul           (AKA dark)
    'underline': 4,    # should not affect padding
    'blink':     5,    # blinks ONLY fg, ul
    'reverse':   7,    # reverses fg + ul, bg
    'conceal':   8,    # conceals ONLY fg, ul, NOT bg
    'cross':     9,    # little support...

    'black':     30,   # NOT gray...
    'red':       31,
    'green':     32,
    'yellow':    33,
    'blue':      34,
    'magenta':   35,
    'cyan':      36,
    'white':     37,

    # fx above this index are rarely supported...
    'frame':     51,
    'circle':    52,
    'overline':  53,
}

SGR_COLOR_NUMBERS = tuple( [ n for n in range(30, 50) ] )

NO_SPACE_CHARS = (
    b'\xe2\x80\x8e', # left-to-right-mark
    b'\xe2\x80\x8b', # zero-width-space
)

MULTI_SPACE_CHARS = {
    '⭐': '*',
    '【': '[',
    '】': ']',
    '\t': ' ',
    # '�': '?',
}


def _validate_sgr(sgr, sgr_type=None):
    if not sgr:
        return
    if sgr not in SGR_CODES:
        raise InvalidSgr(f'"{sgr}"')
    if not sgr_type:
        return sgr
    elif sgr_type == 'color':
        if SGR_CODES[sgr] not in SGR_COLOR_NUMBERS:
            raise InvalidColor(f'"{sgr}"')
    elif sgr_type == 'fx':
        if SGR_CODES[sgr] in SGR_COLOR_NUMBERS:
            raise InvalidFx(f'"{sgr}"')
    return sgr


def ansi_sgr_seq(fx: str, offset: int = 0) -> str:
    """ returns ansi sequence for given color|fx :
            "blink" =>  \033[5m
        offset param allows to get bg sequences, instead of fg
    """
    try:
        param_n = SGR_CODES[fx] + offset
        return ansi_esc_seq(csi='SGR', params=param_n)
    except InvalidAnsi:
        raise InvalidSgr(f'"{fx}"')

def ansi_esc_seq(csi: str, params: str = '') -> str:
    """ params are usually supposed to be ints in string form """
    try:
        return ANSI_ESC + '[' + str(params) + CSI_CODES[csi]
    except KeyError:
        raise InvalidAnsi(f'"{csi}"')


def echo(init_string='', *fx, mode='modern'):
    output = str(init_string)
    fx = [ _validate_sgr(f, sgr_type=None) for f in fx if f ]
    fg = ''
    bg = ''
    # filter colors from fx
    colors = [ c for c in fx if SGR_CODES[c] in SGR_COLOR_NUMBERS ]
    if len(colors) > 0:
        fg = colors[0]
        fx.remove(colors[0])
    if len(colors) > 1:
        bg = colors[1]
        fx.remove(colors[1])
    if len(colors) > 2:
        raise InvalidColor('Exceeded 2 maximum colors')

    if mode not in ('modern', 'retro', 'raw'):
        raise InvalidMode(f'"{mode}"')

    try:
        exception = None
        if fg:
            sys.stdout.write( ansi_sgr_seq(fg) )
        if bg:
            sys.stdout.write( ansi_sgr_seq(bg, offset=10) )
        for fx in fx:
            sys.stdout.write( ansi_sgr_seq(fx) )

        for c in output:
            # only output chars get lagged...
            if mode == 'retro':
                time.sleep(
                    # random_multipler     * default_lag
                    random.randint(1, 100) * 0.00001
                )
            sys.stdout.write(c)
            sys.stdout.flush()

    except Exception as x:
        exception = x

    finally:
        if fg or bg or fx:
            sys.stdout.write( ansi_sgr_seq('reset') )
            sys.stdout.flush()

        if exception:
            raise exception

        if mode != 'raw':
            sys.stdout.write('\n')
            sys.stdout.flush()


class FString(object):

    ALIGN_VALUES = ('l', 'r', 'c', 'lc', 'cl', 'rc', 'cr')

    def __init__(self, init_string='', size=0, pad=' ', align='l', fg='', bg='', fx=[]):

        self.fixed_size = size  # used by Row to decide whether to resize or not

        self.__input_string = ''
        self.append(init_string)

        self.__output_size = self.__input_size
        self.size = size

        self.__pad = ' '
        self.pad = pad

        self.__align = 'l'
        self.align = align

        # black, red, green, yellow, blue, magenta, cyan, white
        self.__fg = ''
        self.fg = fg

        self.__bg = ''
        self.bg = bg

        # bold, dark, underline, blink, reverse, concealed
        self.__fx = []
        self.fx = fx


    def append(self, string):
        self.__input_string = '{}{}'.format(
            self.__input_string,
            string,
        )
        self.set_input_size()

    def set_input_size(self):
        """ calculates input_string len disregarding sgr bytes """
        color_start_byte = ANSI_ESC.encode()        #  b'\x1b'
        color_end_byte = CSI_CODES['SGR'].encode()  #  b'm'
        self.__input_size = 0
        add = True
        for char in self.__input_string:
        # when encoding input_string into byte_string: byte_string will not necessarily have the same amount of bytes as characters in the input_string ( some characters will be made of several bytes ), therefore, the input_string should not be encoded but EACH INDIVIDUAL CHAR should
            byte = char.encode('utf-8')
            if byte == color_start_byte and add:
                add = False
                continue
            elif byte == color_end_byte and not add:
                add = True
                continue
            if add and byte not in NO_SPACE_CHARS:
                self.__input_size += 1

    def __str__(self):
        return self.output

    def __iter__(self):
        for c in self.output:
            yield c

    def __len__(self):
        return self.__output_size if self.__output_size > 0 else 0

    def __add__(self, other):
        return self.output + str(other)

    def echo(self, mode='modern'):
        echo(self, mode=mode)

    @property
    def size(self):
        return len(self)

    @size.setter
    def size(self, s):
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
        if a not in self.ALIGN_VALUES:
            raise InvalidAlignment(f'"{a}"')
        self.__align = a

    @property
    def fg(self):
        return self.__fg

    @property
    def bg(self):
        return self.__bg

    @property
    def fx(self):
        return self.__fx

    @fg.setter
    def fg(self, c):
        if _validate_sgr(c, sgr_type='color'):
            self.__fg = c

    @bg.setter
    def bg(self, c):
        if _validate_sgr(c, sgr_type='color'):
            self.__bg = c

    @fx.setter
    def fx(self, fx):
        if type(fx) != list:
            raise TypeError('fx argument must be list')
        self.__fx = []
        for f in fx:
            if _validate_sgr(f, sgr_type='fx'):
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


    def __paint_pad(self, p):
        ''' pads get bg as well BUT NOT if reverse option is specified '''

        if 'reverse' in self.__fx:
            # s = ansi_sgr_seq('reverse') + s
            return p

        if self.__fg:
            p = ansi_sgr_seq(self.__fg) + p

        if self.__bg:
            p = ansi_sgr_seq(self.__bg, 10) + p

        return p + ansi_sgr_seq('reset')


    @property
    def output(self):

        tmp = self.__input_string
        for k, v in MULTI_SPACE_CHARS.items():
            # flatten these into single space chars
            tmp = tmp.replace(k, v)
        self.__output = tmp

        if self.__input_size > self.__output_size:
            self.__crop_output()

        if self.__fg or self.__bg or self.__fx:
            self.__paint_output()

        if self.__output_size > self.__input_size:
            self.__align_output()

        return self.__output


    def __crop_output(self):
        delta_len = self.__input_size - self.__output_size
        self.__output = self.__output[:0 - delta_len]


    def __paint_output(self):

        for f in self.__fx:
            self.__output = ansi_sgr_seq(f) + self.__output

        if self.__fg:
            self.__output = ansi_sgr_seq(self.__fg) + self.__output

        if self.__bg:
            # background color range is +10 respect to foreground color
            self.__output = ansi_sgr_seq(self.__bg, offset=10) + self.__output

        self.__output = self.__output + ansi_sgr_seq('reset')


    def __align_output(self):

        if self.__align == 'l':
            self.__output = self.__output + self.__paint_pad(self.__sml_pad + self.__big_pad)

        elif self.__align == 'r':
            self.__output = self.__paint_pad(self.__sml_pad + self.__big_pad) + self.__output

        elif self.__align in ('c', 'cl', 'lc'):
            self.__output = self.__paint_pad(self.__sml_pad) + self.__output + self.__paint_pad(self.__big_pad)

        elif self.__align in ('cr', 'rc'):
            self.__output = self.__paint_pad(self.__big_pad) + self.__output + self.__paint_pad(self.__sml_pad)


class Row(object):
    '''a string with size === terminal_len (unless otherwise specified). Instantiate a Row object with str|FString instances and it will keep its size constant by cropping/aligning objects with no fixed_size'''

    def __init__(self, *items, size=0):
        self.__output = ''
        self.__fixed_size = size
        self.__fstrings = []
        for item in items:
            self.append(item)

    def __len__(self):
        return self.__fixed_size if self.__fixed_size else tty_cols()

    def assign_spaces(self):
        spaces_left = len(self)

        # remove fixed_fs sizes
        for fs in self.__fstrings:
            if fs.fixed_size:
                spaces_left -= len(fs)

        # gather adaptive_fs
        adaptive_fs_count = len(
            [ fs for fs in self.__fstrings if not fs.fixed_size ]
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
    def size(self):
        return self.__fixed_size

    @size.setter
    def size(self, s):
        self.__fixed_size = s

    @property
    def output(self):
        self.__output = ''
        self.assign_spaces()
        for fs in self.__fstrings:
            self.__output = self.__output + str(fs)
        return self.__output

    def append(self, s):
        self.__fstrings.append(
            FString(s) if type(s) != FString else s
        )

    def echo(self, mode='modern'):
        echo(self, mode=mode)

    def __str__(self):
        return self.output


def tty_cursor(enable=True):
    sys.stdout.write(
        ansi_esc_seq(
            #   \033[?25h              \033[?25l
            csi='DECSM' if enable else 'DECRM',
            params='?25',
        )
    )
    sys.stdout.flush()


def tty_clear():
    sys.stdout.write(
        ansi_esc_seq(csi='CUP') # \033[H
    )
    sys.stdout.write(
        ansi_esc_seq(csi='ED')  # \033[J
    )
    sys.stdout.flush()


def tty_up():
    sys.stdout.write(
        ansi_esc_seq(csi='CUU') # \033[A
    )
    sys.stdout.flush()


def tty_rows():
    ''' returns dynamic rows of current terminal '''
    return os.get_terminal_size().lines

def tty_cols():
    ''' returns dynamic cols of current terminal '''
    return os.get_terminal_size().columns


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


def human_bytes(byts, round=2, suffix='B'):
    ''' converts bytes as integer into a human readable string '''
    for unit in ('','K','M','G','T','P','E','Z'):
        if abs(byts) < 1024.0:
            return "{:3.{}f}{}{}".format(byts, round, unit, suffix)
        byts /= 1024.0
    return "{:.{}f}{}{}".format(byts, round, 'Y', suffix)


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
            levels.append(input_path.split(os.sep)[depth])
            depth += 1
        return os.path.join(*levels)
    except IndexError:
        return remove_path(input_path, depth=depth+1)


def obfuscate_random_chars(input_string, amount=0, obfuscator='_'):
    ''' returns input string with amount of random chars obfuscated '''
    amount = len(input_string) - 4 if not amount or amount >= len(input_string) else amount

    string_indecae = [
        i for i in range(
            len( str(input_string) )
        )
    ]

    string_as_list = list(input_string)
    for random_index in unique_random_items(string_indecae, amount):
        string_as_list[random_index] = obfuscator

    return iterable_to_string(string_as_list)


class ProgressBar(object):

    def __init__(self, goal, width=0, pad='=', color=''):

        self.goal = float(goal)
        self.score = 0.0

        self.spaces = int(
            width if width else tty_cols() - 3
        )

        self.scores_by_space = [
            # 100.1, 100.1, 100.1
        ]
        self.calculate_space_scores()

        self.pad = str(pad)[0]
        self.color = color

    @property
    def done(self):
        return self.score >= self.goal


    def eval_score(self, value):

        self.score += float(value)

        overcome_scores = []
        for i, space_score in enumerate(self.scores_by_space):
            if self.score < space_score:
                break
            overcome_scores.append(i)
            echo(
                self.pad,
                self.color,
                mode='raw'
            )

        for d in range(len(overcome_scores)):
            del self.scores_by_space[0]


    def calculate_space_scores(self):
        ''' sets threshold needed to fill each space '''
        score_x_space = self.goal / self.spaces
        for s in range(self.spaces):
            self.scores_by_space.append(
                score_x_space * (s + 1)
            )
        # assert self.scores_by_space[-1] == self.goal


    def update(self, value=0.0):

        if self.done:
            return

        if self.score == 0:
            echo('[', 'faint', self.color, mode='raw')
            echo('.' * self.spaces, 'faint', self.color, mode='raw')
            echo(']', 'faint', self.color, mode='raw')
            sys.stdout.write('\b' * (self.spaces +1 ))

        self.eval_score(value)

        if self.done:
            echo(']', 'faint', self.color)
