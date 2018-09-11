import pyperclip

def copy_to_clipboard(text):
	try:
		pyperclip.copy(text)
		return True
	except pyperclip.PyperclipException:
		return False
