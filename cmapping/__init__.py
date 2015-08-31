from cmapping.base import CType, ClassInitManager
from cmapping.utils import padded_with_zeros
from cmapping.typedef import Padding
import cmapping.endianness as endian


class Endianness:
    little_endian = endian.little_endian
    big_endian = endian.big_endian
    network = endian.network_endian
    native = endian.native_endian


class CStruct:
    ''' Python object, capable to pack and unpack itself into C structure. '''

    enable_dynamic_structures = False
    manager = ClassInitManager()

    def __new__(cls, *args, **kwargs):
        if CStruct.enable_dynamic_structures or \
                not CStruct.manager.is_ready(cls):
            CStruct.manager.init_class(cls)
        return super(CStruct, cls).__new__(cls)

    def __init__(self, binary_data):
        ''' Create instance from its binary representation. '''
        self.unpack(binary_data)

    def unpack(self, binary_data):
        ''' Extract values of CType fields declared in <type(self)>
        according to their type and length from binary data.
        '''
        cls = type(self)    # Derived class, should be already initialized
        packer = CStruct.manager.get_packer(cls)
        values = list(packer.unpack(binary_data))

        for attr in CStruct.manager.get_c_attrs(cls)[::-1]:
            ctype = getattr(cls, attr)
            if isinstance(ctype, Padding):
                continue
            elif len(ctype) == 1:
                setattr(self, attr, values.pop())
            else:
                setattr(self, attr, values[-len(ctype):])
                values = values[:-len(ctype)]

    def pack(self):
        ''' Returns string of bytes containing values of CType fields declared
        in <type(self)> according to their type and declaration order.
        '''
        cls = type(self)
        values = []

        for attr in CStruct.manager.get_c_attrs(cls):
            ctype = getattr(cls, attr)
            if isinstance(ctype, Padding):
                continue
            elif len(ctype) == 1:
                values.append(getattr(self, attr))
            else:
                values += padded_with_zeros(getattr(self, attr), len(ctype))
        return CStruct.manager.get_packer(cls).pack(*values)
