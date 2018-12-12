from random import randrange, choice


def items_are_equal(iterable):
   return iterable[1:] == iterable[:-1]


def indexes_from_string(string):
	return [ i for i in range(len(str(string))) ]


def random_unique_items_from_list(lst, amount):
	items = []
	while amount != 0:
		random_item = choice(lst)
		if random_item not in items:
			items.append(random_item)
			amount -= 1
	return items


def pop_random_item(lst):
	try:
		random_index = randrange(len(lst))
		return lst.pop(random_index)
	except ValueError:
		return


def string_to_list(string):
	return [ c for c in str(string) ]


def list_to_string(lst):
	string = ''
	for c in lst:
		string = string + c
	return string
