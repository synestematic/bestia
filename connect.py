import sys
import requests

def http_get(url):
	try:
		headers = {
			'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
		}
		r = requests.get(url, headers=headers)
		if r.status_code == 200:
			return r.text
		else:
			return False
	except requests.exceptions.ConnectionError:
		sys.exit('No Internet connection...')

# def http_get(url, attempt=1):
# 	max_attempts = 3
# 	try:
# 		headers = {
# 			# 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
# 			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
# 			'cookie': '__cfduid=dc007f70cc6e84fe5cf05b13b9d7022361536178218; _ga=GA1.2.1741958857.1536178240; _gid=GA1.2.1955541911.1536178240; ppu_main_b1f57639c83dbef948eefa8b64183e1e=1; ppu_sub_b1f57639c83dbef948eefa8b64183e1e=1; _gat=1'
# 		}
# 		r = requests.get(url, headers=headers)
# 		if r.status_code == 200:
# 			h = r.text
# 			if type(h) != str:
# 				abort('I got {} instead of a string'.format(type(h)))
# 			return h
# 		else:
# 			return False
# 	except requests.exceptions.ConnectionError:
# 		if attempt > max_attempts:
# 			abort(BYE_MESSAGE)
# 		else:
# 			slow_print('No Internet connection. Retry {}/{}'.format(attempt, max_attempts), color='red')
# 			time.sleep(5)
# 			http_get(url, attempt=attempt + 1)

if __name__ == '__main__':
	pass
	# use commented function for rcard as well