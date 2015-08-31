import itertools


class Indexed:
    ''' Counts instances of this class and gives them unique _index. '''
    _counter = itertools.count()

    def __new__(cls, *args, **kwargs):
        obj = super(Indexable, cls).__new__(cls)
        obj._index = next(Indexable._counter)
        return obj


class CType(Indexed):
    pass
