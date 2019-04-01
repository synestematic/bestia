from os import system, remove, path
from uuid import uuid4

from bestia.misc import command_output
from bestia.output import echo, ENCODING
from bestia.iterate import random_unique_items_from_list
from bestia.error import *

_CURL_BIN = command_output('which', 'curl').decode().strip()

_WEB_BROWSERS = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36', # chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0', # firefox
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393', # edge
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36 Vivaldi/2.2.1388.37', # vivaldi
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.2 Safari/605.1.15', # safari
    # 'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko', # ie11 gets banned on several sites...
)

def __random_browser():
    return random_unique_items_from_list(_WEB_BROWSERS, amount=1)[0]

def __quoted(s):
    return '"{}"'.format(s)

def http_get(url, browser='', credentials=(), follow_redirects=True, silent=True, store=None, raw=False):
    ''' performs HTTP GET requests using CURL command
    
        if store:
            return True/False
        else:
            return response_data/False
    '''
    if not _CURL_BIN:
        raise CurlBinMissing('curl command NOT found, please install')

    request_data = None
    if '?' in url:
        url, request_data = url.split('?')

    if '\'' in url or '\"' in url:
        input('THIS URL SUCKS: {}'.format(url))

    out_file = path.join('/', 'tmp', uuid4().hex) if not store else store
    browser = __random_browser() if not browser else browser

    curl_command = [
        _CURL_BIN, '-G', __quoted(url),
        '--user-agent', __quoted(browser),
        '--output', out_file,
    ]

    if credentials:
        curl_command.append('--user')
        curl_command.append('{}:{}'.format(credentials[0], credentials[1]))

    if follow_redirects:
        curl_command.append('--location')

    if silent:
        curl_command.append('--silent')

    if request_data:

        if '&' in request_data:
            params = request_data.split('&')
            for param in params:
                curl_command.append('--data-urlencode')
                curl_command.append(__quoted(param))

        else:
            curl_command.append('--data-urlencode')
            curl_command.append(__quoted(request_data))


    curl_command = ' '.join(curl_command)
    input(echo(curl_command, 'cyan'))
    rc = system(curl_command)
    if rc != 0: # system when NOT want to store cmd output to var
        raise CurlFailed('curl returned: {}'.format(rc))

    if store:
        # stored to file, no need to return data
        return True

    response_data = bytearray()
    with open(out_file, 'rb') as stream:
        for b in stream.read():
            response_data.append(b)

    remove(out_file)
    return response_data if raw else response_data.decode(ENCODING).strip()


if __name__ == '__main__':


    pb = 'http://localhost?a=4 4&user=bla'
    pb = 'http://localhost?a=4 678'
    pb = 'http://localhost'
    pb = 'http://localhost/sam/target.php?do=login&da=123'

    r = http_get(pb)
    echo(r, 'blue')


