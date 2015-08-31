import itertools


class Indexed:
    ''' Counts instances of this class and gives them unique _index. '''
    __counter = itertools.count()

    def __new__(cls, *args, **kwargs):
        obj = super(Indexed, cls).__new__(cls)
        obj._index = next(Indexed.__counter)
        return obj


class CType(Indexed):
    pass
