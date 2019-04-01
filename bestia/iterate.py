from random import randrange, choice

def items_are_equal(iterable):
    ''' compares that all items in list are equal '''
    return iterable[1:] == iterable[:-1]

def indexes_from_string(string):
    ''' returns indexes from string '''
    return [i for i in range(len(str(string)))]

def random_unique_items_from_list(lst, amount=1):
    ''' returns random items form list '''
    items = []
    while amount != 0:
        random_item = choice(lst)
        if random_item not in items:
            items.append(random_item)
            amount -= 1
    return items

def pop_random_item(lst):
    ''' returns/removes random item from list  '''
    try:
        random_index = randrange(len(lst))
        return lst.pop(random_index)
    except ValueError:
        return

def string_to_list(string):
    ''' turns string into a list '''
    return [char for char in str(string)]

def list_to_string(lst):
    ''' turns string into a list '''
    string = ''
    for c in lst:
        string = string + c
    return string

def looped_list_item(i, vector):
    ''' returns vector[i] but loops thru vector if i > len(vector)
        ...works also for large negative i's
        recursion is NOT a good approach for very large i's
    '''
    count = len(vector)
    if abs(i) < count:
        return vector[i]
    _, remainder = divmod(i, count)
    return vector[remainder]

if __name__ == '__main__':
    pass

