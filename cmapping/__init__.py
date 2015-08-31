import struct
from enum import Enum

from cmapping.typedef import Padding
from cmapping.base import CType


class Endianness(Enum):
    little_endian = 1
    big_endian = 2
    network = 2
    native = 3


class CStruct:
    ''' Python object, capable to pack and unpack itself into C structure. '''

    enable_dynamic_structures = False

    __endianness = {
        Endianness.little_endian: '<',
        Endianness.big_endian: '>',
        Endianness.native: '@',
    }

    __packer = {}
    __c_members = {}

    def __new__(cls, *args, **kwargs):
        if not (cls in CStruct.__packer and cls in CStruct.__c_members) \
                or CStruct.enable_dynamic_structures:
            cls.__init_class()
        return super(CStruct, cls).__new__(cls)

    @classmethod
    def __init_class(cls):
        ''' Find all fields of type CType declared as <cls> members or members
        of <cls> parents and create parser which is used to pack and 
        unpack <cls> instances.
        '''
        CStruct.__c_members[cls] = []
        for parent in cls.mro()[::-1]:
            CStruct.__c_members[cls] += cls.__find_c_members(parent)

        fmt = ''.join([str(getattr(cls, x)) for x in CStruct.__c_members[cls]])
        if hasattr(cls, 'endianness'):
            fmt = CStruct.__endianness[cls.endianness] + fmt
        CStruct.__packer[cls] = struct.Struct(fmt)

    @classmethod
    def __find_c_members(cls, target):
        ''' Find all fields of type CType declared as <target> members '''
        c_members = [x for x in target.__dict__
                     if isinstance(getattr(cls, x), CType)]
        # members order is important due to memory mapping
        c_members.sort(key=lambda x: getattr(cls, x)._index)
        return c_members

    def __init__(self, binary_data):
        ''' Create instance from its binary representation. '''
        self.unpack(binary_data)

    def unpack(self, binary_data):
        ''' Extract values of CType fields declared in <type(self)>
        according to their type and length from binary data.
        '''
        cls = type(self)    # Derived class, should be already initialized
        values = list(CStruct.__packer[cls].unpack(binary_data))[::-1]
        for attr in CStruct.__c_members[cls]:
            member = getattr(cls, attr)
            if isinstance(member, Padding):
                continue
            elif len(member) == 1:
                setattr(self, attr, values.pop())
            else:
                setattr(self, attr, values[-len(member):][::-1])
                values = values[:-len(member)]

    def pack(self):
        ''' Returns string of bytes containing values of CType fields declared
        in <type(self)> according to their type and declaration order.
        '''
        cls = type(self)
        values = []

        for attr in CStruct.__c_members[cls]:
            member = getattr(cls, attr)
            if isinstance(member, Padding):
                continue
            elif len(member) == 1:
                values.append(getattr(self, attr))
            else:
                values += self.__padded_with_zeros(getattr(self, attr),
                                                   len(member))
        return CStruct.__packer[cls].pack(*values)

    def __padded_with_zeros(self, array, length):
        ''' Returns <array> padded with zeroes at the end to match <length> '''
        if len(array) > length:
            raise ValueError("Max array len is {}, but was {}.".format(
                             length, len(array)))
        if len(array) < length:
            array += [0,] * (length - len(array))
        return array
