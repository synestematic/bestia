from os import system, remove, path
from subprocess import check_output, CalledProcessError
from uuid import uuid4

from bestia.output import echo, ENCODING
from bestia.iterate import random_unique_items_from_list
from bestia.error import *

_WEB_BROWSERS = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36', # chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0', # firefox
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393', # Edge
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36 Vivaldi/2.2.1388.37', # Vivaldi
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.2 Safari/605.1.15', # Safari
    # 'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko', # IE11 gets banned on several sites...
)

def __random_browser():
    return random_unique_items_from_list(_WEB_BROWSERS, amount=1)[0]

def command_output(*args):
    output = ''
    try:
        output = check_output(args)
        if output:
            output = output.decode().strip()
    except CalledProcessError:
        pass
    finally:
        return output

_CURL_PATH = command_output('which', 'curl')

def http_get(url, browser='', credentials=(), follow_redirects=True, silent=True, store=None, raw=False):
    ''' if store:
            return True/False
        else:
            return data/False
    '''
    if not _CURL_PATH:
        raise CUrlMissing('cUrl required, please install')

    if '\'' in url or '\"' in url:
        input('THIS URL SUCKS: {}'.format(url))

    # HOW DO I PROPERLY ENCODE THIS?
    # DO NOT USE EXTERNAL LIBRARY FOR IT
    # WHAT IF URL HAS " in IT?

    url = '"{}"'.format(url)
    out_file = path.join('/', 'tmp', uuid4().hex) if not store else store
    browser = __random_browser() if not browser else browser

    curl_command = [
        _CURL_PATH, url,
        '--user-agent', '"{}"'.format(browser),
        '--output', out_file,
    ]

    if credentials:
        curl_command.append('--user')
        curl_command.append('{}:{}'.format(credentials[0], credentials[1]))

    if follow_redirects:
        curl_command.append('--location')

    if silent:
        curl_command.append('--silent')

    curl_command = ' '.join(curl_command)
    # input(curl_command)
    rc = system(curl_command)
    if rc != 0: # system when NOT want to store cmd output to var
        raise CUrlFailed('cUrl returned: {}'.format(rc))

    if store:
        # stored to file, no need to return data
        return True

    data = bytearray()
    with open(out_file, 'rb') as stream:
        for b in stream.read():
            data.append(b)
    remove(out_file)
    return data if raw else data.decode(ENCODING).strip()


if __name__ == '__main__':

    # /anaconda3/bin/curl "https://proxbea.com/s/?q=Php&page=0&orderby=99" --user-agent "Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko" --output /tmp/9e75e7be737c4821bec37a1e71348aec --location --silent

    pb = 'https://www.google.com'
    pb = 'https://thepiratebay-proxylist.org/'

    pb = 'https://proxbea.com/s/?q=Php&page=0&orderby=99'
    # r = http_get_old(pb)
    # echo(r, 'green')

    r = http_get(pb)
    echo(r, 'blue')


    # r = http_get_old('http://localhost/sam/target.php?do=login')

    # r = http_get_old('http://releases.ubuntu.com/18.04.1.0/ubuntu-18.04.1.0-live-server-amd64.iso?_ga=2.37110947.2086347288.1548630714-895763213.1548630714')

    # r = http_get_old('https://dl2018.sammobile.com/premium/NV1aQy8rLD1WLDc8QDcoQUdYLzwuMEcqNyVUKDU8JFoOARlJUyA5RSRbVkc1UlNGQF9aQFlJThwXGwBNSVlbRUVbUEBa/A530FXXU3BRK3_A530FOGC3BRK1_FTM.zip')

    # echo(r, 'red')


