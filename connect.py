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

if __name__ == '__main__':
	pass
