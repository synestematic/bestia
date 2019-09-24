from random import randrange, choice


def items_are_equal(iterable):
    ''' compares all items in iterable for equality '''
    return iterable[1:] == iterable[:-1]


def string_to_list(string):
    ''' returns list of chars from string
        useful for item assignment
    '''
    return [char for char in str(string)]


def iterable_to_string(iterable):
    ''' returns string of items in iterable '''
    string = ''
    for i in iterable:
        string = string + str(i)
    return string


def unique_random_items(iterable, amount=5):
    ''' returns tuple of unique random items from iterable 
        UNIQUE items == CANNOT get more items than iterable originally had

        can ALSO be used to randomize the order items in iterable
    '''
    iterable_count = len(iterable)
    amount = iterable_count if amount > iterable_count else amount

    items_to_return = []
    while amount != 0:
        random_item = choice(iterable)
        if random_item not in items_to_return:
            items_to_return.append(random_item)
            amount -= 1
    return tuple(items_to_return)


def pop_random_item(lst):
    ''' returns/removes random item from list  '''
    try:
        random_index = randrange(len(lst))
        return lst.pop(random_index)
    except ValueError:
        return None


def looped_list_item(i, iterable):
    ''' returns iterable[i] but loops thru iterable if i > len(iterable)
        works also for large negative i's
        recursion is NOT a good approach for very large i's
    '''
    if abs(i) < len(iterable):
        return iterable[i]
    _, remainder = divmod(i, len(iterable))
    return iterable[remainder]


class LoopedList(list):
    ''' a mutable array that loops thru items when required index is out of range '''

    def __init__(self, *i):
        ''' Note the slightly different init syntax:
            * list( [ 1, 2, 3 ] )   single iterable arg
            * LoopedList(1, 2, 3)   arbitrary number of args
        '''
        super().__init__(i)

    def __getitem__(self, i):
        if abs(i) < super().__len__():
            return super().__getitem__(i)
        _, r = divmod(i, super().__len__())
        return super().__getitem__(r)

