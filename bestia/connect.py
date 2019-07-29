from os import system, remove, path
from uuid import uuid4

from bestia.misc import command_output
from bestia.output import echo, dquoted, ENCODING
from bestia.iterate import unique_random_items
from bestia.error import *

_WEB_BROWSERS = {
    'Chrome': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Firefox': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
    'Edge': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',
    'Vivaldi': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36 Vivaldi/2.2.1388.37',
    'Safari': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.2 Safari/605.1.15',
    'IE11': 'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko',
}

def __random_browser():
    ''' returns random browser for basic anti-crawler prevention '''
    allowed_browsers = [v for k, v in _WEB_BROWSERS.items() if k != 'IE11'] # IE11 gets banned on several sites...
    return unique_random_items(allowed_browsers, amount=1)[0]


_CURL_BIN = command_output('which', 'curl').decode(ENCODING).strip()

def http_get(url, browser='', credentials=(), follow_redirects=True, silent=True, store=None, raw=False):
    ''' performs HTTP GET requests using local CURL command
        HTTP response data is always stored into a file which can be kept or discarded since
        this function returns the contents anyway.
        can return data as raw bytes or as utf-8 encoded string
    '''
    if not _CURL_BIN:
        raise CurlBinMissing('curl bin NOT found')

    request_data = None
    if '?' in url:
        url, request_data = url.split('?')

    if '\'' in url or '\"' in url:
        input('THIS URL SUCKS: {}'.format(url))

    out_file = path.join('/', 'tmp', uuid4().hex) if not store else store
    browser = __random_browser() if not browser else browser

    curl_command = [
        _CURL_BIN, '-G', dquoted(url),
        '--user-agent', dquoted(browser),
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
                curl_command.append(dquoted(param))
        else:
            curl_command.append('--data-urlencode')
            curl_command.append(dquoted(request_data))


    curl_command = ' '.join(curl_command)
    # input(echo(curl_command, 'cyan'))
    rc = system(curl_command)
    if rc != 0: # system when NOT want to store cmd output to var
        raise CurlFailed('curl returned: {}'.format(rc))

    with open(out_file, 'rb') as stream:
        response_data = stream.read()

    if not store:
        remove(out_file)

    return response_data if raw else response_data.decode(ENCODING).strip()

