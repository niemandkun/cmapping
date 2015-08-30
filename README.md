# cmapping

*Syntactic sugar for Python 3+*

### About:
In the C programming language a [**struct**](https://en.wikipedia.org/wiki/Struct_(C_programming_language)) is a data type declaration that defines a physically grouped list of variables to be placed under one name in a block of memory.
`cmaping` add special syntax to automatically build and set up Python objects or serialize them into binary structure compatible with C types.
Project was inspired by [SQLAlchemy](http://www.sqlalchemy.org/) and aims to provide intuitive and clearly understandable syntax to define C-like structures and parse raw binary data.

### Usage example:

```python
from cmapping import CStruct
from cmapping.typedef import Integer

class Vector(CStruct):
    x = Integer()
    y = Integer()

>>> v = Vector(b'\x01\x00\x00\x00\x02\x00\x00\x00')
>>> v.x
1
>>> v.x = 42
>>> v.pack()
b'*\x00\x00\x00\x02\x00\x00\x00'
```

### How it works:
`CStruct` defines three important methods: `pack(self)`, `unpack(self, data)` and `__init__(self, data)`.
- `unpack(self, data)` - parses data and updates class members with appropriate values (data is `bytes`)
- `pack(self)` - returns bytes that represents C-struct filled by current instance values
- `__init__(self, data)` - create and initialize object from binary data (its body is only a call of `unpack`, so it's safe to override)

Another important place in module is flag `CStruct.enable_dynamic_structures`, which means that you can modify fields definitions for each class derived from CStruct on runtime. By default it is set to `False`, because if it is `True` CStruct will rebuild parser before create each new instance of class, but it is lack of performance.

### In background:
`cmapping` uses `struct` module from standard Python library and introspection. At first, it looks at all class members and builds appropriate formatting string, that provides `struct` parser with binary data format. Then, parser disassemble binary data. Finally, `cmapping` maps results to object's members and build Python object with fields initialized from raw data. `pack()` function repeats the same work in reverse order, except that formatting string is already buildet and parser is already initialized.

### Other examples of usage:
Parse array and save result in two lists. If you try to pack oversized array it rises ValueError. If array is undersized free space will be filled by zeroes.

```python
class ArrayExample(CStruct):
    int_array = Integer(10)
    uint_array = UnsignedInteger(20)
```

Convert `char[]` to `bytes`:

```python
class Person(CStruct):
    name = CString(50)
```

Convert `char[]` to `list` of integers:

```python
class Person(CStruct):
    name = Char(50)
```

Explicitly define endianness (if endianness is not defined, `Endianness.native` will be used):

```python
from cmapping import Endianness

class Package(CStruct):
    endianness = Endianness.network
    body = CString(100)
    checksum = Integer()
```

Padding using:

```python
from cmapping.typedef import Padding

class Package(CStruct):
    body = CString(100)
    padding = Padding(24)    # 24 bytes of unused space
    checksum = Integer()
```

Inheritance also works:

```python
class A(CStruct):
    a_1 = Char()
    a_2 = Char()

class B(A):
    b_1 = Char()
    b_2 = Char()
```

Total size of B is 4 bytes, and it has 4 `char` fields: a\_1, a\_2, b\_1, b\_2. Order of members is important: in derived class first members are members from parent, and then members from class itself. So, previous declaration of B equivalent to:

```python
class B(CStruct):
    a_1 = Char()
    a_2 = Char()
    b_1 = Char()
    b_2 = Char()
```
