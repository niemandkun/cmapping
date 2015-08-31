from itertools import count
from struct import Struct

import cmapping.endianness as endian


class Indexed:
    ''' Counts instances of this class and gives them unique _index. '''
    __counter = count()

    def __new__(cls, *args, **kwargs):
        obj = super(Indexed, cls).__new__(cls)
        obj._index = next(Indexed.__counter)
        return obj


class CType(Indexed):
    pass


class ClassInitManager:
    def __init__(self):
        self.__packers = {}
        self.__c_attrs = {}

    def get_packer(self, cls):
        ''' Returns packer created for <cls> '''
        return self.__packers[cls]

    def get_c_attrs(self, cls):
        ''' Returns list of attrs derived from CType and declared in <cls>
        by the time when <cls> was initialized by init_class().
        '''
        return self.__c_attrs[cls]

    def is_ready(self, cls):
        ''' True if cls was initialized by init_class(), else False '''
        return cls in self.__packers and cls in self.__c_attrs

    def init_class(self, cls):
        ''' Find all fields of type CType declared as <cls> attrs or attrs
        of <cls> parents and create parser which is used to pack and
        unpack <cls> instances.
        '''
        self.__find_c_attrs(cls)
        self.__build_packer(cls)

    def __find_c_attrs(self, cls):
        ''' Find all fields of type CType declared as <target> attrs
        or as attrs of <target> parents
        '''
        self.__c_attrs[cls] = []
        for parent in cls.mro()[::-1]:
            parent_attrs = [x for x in parent.__dict__
                              if isinstance(getattr(cls, x), CType)]
            parent_attrs.sort(key=lambda x: getattr(cls, x)._index)
            self.__c_attrs[cls] += parent_attrs

    def __build_packer(self, cls):
        format_line = cls.endianness if hasattr(cls, 'endianness') else ''
        ctypes = (getattr(cls, x) for x in self.get_c_attrs(cls))
        format_line += ''.join([str(t) for t in ctypes])
        self.__packers[cls] = Struct(format_line)
