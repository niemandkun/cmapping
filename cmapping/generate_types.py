#!/usr/bin/env python3

OUTPUT = 'typedef.py'

HEADER = '''# This code is autogenerated by {script_name}
# If you found a bug, please, don't try to edit this file.
# Edit {script_name} instead.

from cmapping.{base_name} import CType
'''.format(script_name=__file__, base_name='base')

PARENT_CLS = '''

class {name}(CType):
    def __init__(self, length{len_init}):
        if not isinstance(length, int):
            raise ValueError("Expected integer as count of bytes")
        self.__len = length

    def __len__(self):
        return {len_ret}

    def __str__(self):
        if self.__len == 1:
            return type(self).fmt
        return str(self.__len) + type(self).fmt
'''

TYPE_CLS = '''

class {name}({p_name}):
    fmt = '{fmt}'
'''

types = [
    ('Char', 'c'),
    ('SignedChar', 'b'),
    ('UnsignedChar', 'B'),
    ('Bool', '?'),
    ('Short', 'h'),
    ('UnsignedShort', 'H'),
    ('Integer', 'i'),
    ('UnsignedInteger', 'I'),
    ('Long', 'l'),
    ('UnsignedLong', 'L'),
    ('LongLong', 'q'),
    ('UnsignedLongLong', 'Q'),
    ('SsizeT', 'n'),
    ('SizeT', 'N'),
    ('Float', 'f'),
    ('Double', 'd'),
    ('VoidPtr', 'P'),
]

strings = [
    ('CString', 's'),
    ('PascalString', 'p'),
    ('Padding', 'x'),
]


def generate_parent(name, allow_one_arg, length=None):
    return PARENT_CLS.format(name=name, len_init='=1' if allow_one_arg else '',
                             len_ret='self.__len' if allow_one_arg else '1')


def generate_type(name, p_name, fmt):
    return TYPE_CLS.format(**locals())


def main():
    output = open(OUTPUT, 'w')

    output.write(HEADER)
    output.write(generate_parent('__Number', allow_one_arg=True))
    output.write(generate_parent('__Array', allow_one_arg=False))

    for x in types:
        output.write(generate_type(x[0], '__Number', x[1]))

    for x in strings:
        output.write(generate_type(x[0], '__Array', x[1]))


if __name__ == '__main__':
    main()
