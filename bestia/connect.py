import sys
import requests
from time import sleep

from bestia.output import echo, abort

def http_get(url, retries=3, verbose=False):
	try:
		headers = {
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
			# 'cookie': '__cfduid=dc007f70cc6e84fe5cf05b13b9d7022361536178218; _ga=GA1.2.1741958857.1536178240; _gid=GA1.2.1955541911.1536178240; ppu_main_b1f57639c83dbef948eefa8b64183e1e=1; ppu_sub_b1f57639c83dbef948eefa8b64183e1e=1; _gat=1'
		}
		r = requests.get(url, headers=headers)
		if r.status_code == 200:
			html = r.text
			if type(html) != str:
				if verbose:
					echo('http request returned {} insetad of <str>'.format(type(html)), 'red')
				return
			return html
		else:
			return
	except requests.exceptions.ConnectionError:
		if retries < 1:
			if verbose:
				echo('Unable to connect', 'red')
			return
		else:
			if verbose:
				echo('No connection, {} attempts left...'.format(retries), 'red')
			sleep(5)
			http_get(url, retries=retries-1, verbose=verbose)

if __name__ == '__main__':
	pass
	# implement referrers and cookies