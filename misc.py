import pyperclip

def copy_to_clipboard(text):
	try:
		pyperclip.copy(text)
		return True
	except pyperclip.PyperclipException:
		return False

def items_are_equal(iterable):
   return iterable[1:] == iterable[:-1]
