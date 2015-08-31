#!/usr/bin/env python3

import struct
import unittest

from cmapping import CStruct, Endianness
from cmapping.typedef import Integer, CString, Padding, \
                             UnsignedChar, Double


class Vector(CStruct):
    endianness = Endianness.little_endian
    x = Integer()
    y = Integer()


class VectorYX(CStruct):
    ''' Demonstrates, that members order is important! '''
    y = Integer()
    x = Integer()


class BigEndianVector(CStruct):
    endianness = Endianness.big_endian
    x = Integer()
    y = Integer()


class TestVector(unittest.TestCase):
    ''' In this case we test correctness with small and simple data
    and different endianness support.
    '''
    def create_test_data(self):
        return struct.pack('<2i', 4, 5)

    def make_assert(self, vector, x=4, y=5):
        self.assertTrue(hasattr(vector, 'x'))
        self.assertTrue(hasattr(vector, 'y'))
        self.assertEqual(vector.x, x)
        self.assertEqual(vector.y, y)

    def test_can_unpack(self):
        vector = Vector(self.create_test_data())
        self.make_assert(vector)

    def test_can_pack(self):
        data = self.create_test_data()
        vector = Vector(data)
        new_data = vector.pack()
        self.assertEqual(data, new_data)

    def test_save_new_values_while_packing(self):
        vector = Vector(self.create_test_data())
        vector.x, vector.y = 10, 42
        new_vector = Vector(vector.pack())
        self.make_assert(new_vector, 10, 42)

    def test_fields_order(self):
        data = self.create_test_data()
        vectorXY = Vector(data)
        vectorYX = VectorYX(data)
        self.assertEqual(vectorXY.x, vectorYX.y)
        self.assertEqual(vectorXY.y, vectorYX.x)

    def test_big_endian(self):
        data = struct.pack('>2i', 4, 5)
        vector = BigEndianVector(data)
        self.make_assert(vector)


class Person(CStruct):
    first_name = CString(10)
    last_name = CString(10)
    age = UnsignedChar()
    email = CString(20)


class TestPerson(unittest.TestCase):
    ''' In this case we check that processing of strings works. '''
    def create_test_data(self):
        return struct.pack('10s10sB20s', b'John', b'Doe',
                           42, b'example@mail.com')

    def test_can_unpack(self):
        person = Person(self.create_test_data())

        self.assertTrue(hasattr(person, 'first_name'))
        self.assertTrue(hasattr(person, 'last_name'))
        self.assertTrue(hasattr(person, 'age'))
        self.assertTrue(hasattr(person, 'email'))

        self.assertEqual(person.first_name, b'John' + b'\x00' * 6)
        self.assertTrue(person.email.startswith(b'example@mail.com'))
        self.assertEqual(person.age, 42)

    def test_can_pack(self):
        data = self.create_test_data()
        person = Person(data)
        new_data = person.pack()
        self.assertEqual(data, new_data)

    def test_save_new_values_while_packing(self):
        john = Person(self.create_test_data())
        john.first_name = b'Ivan'
        john.last_name = b'Petrov'
        john.age = 21
        spy = Person(john.pack())
        self.assertTrue(spy.last_name.startswith(b'Petrov'))
        self.assertEqual(spy.age, 21)


class Polygon(CStruct):
    x = Integer()
    y = Integer()
    vertexes = Double(10)


class TestPolygon(unittest.TestCase):
    ''' In this case we check array processing. '''
    def create_test_data(self):
        return struct.pack('2i10d', *list(range(0, 12)))

    def test_can_unpack(self):
        polygon = Polygon(self.create_test_data())

        self.assertTrue(hasattr(polygon, 'x'))
        self.assertTrue(hasattr(polygon, 'y'))
        self.assertTrue(hasattr(polygon, 'vertexes'))
        self.assertTrue(hasattr(polygon.vertexes, '__iter__'))
        self.assertTrue(hasattr(polygon.vertexes, '__getitem__'))
        self.assertTrue(isinstance(polygon.vertexes, list))

        self.assertEqual(polygon.x, 0)
        self.assertEqual(polygon.vertexes, list(range(2, 12)))

    def test_can_pack(self):
        data = self.create_test_data()
        polygon = Polygon(data)
        new_data = polygon.pack()
        self.assertEqual(data, new_data)

    def test_array_undersize(self):
        polygon = Polygon(self.create_test_data())
        polygon.vertexes = [1, 1, 1]
        polygon = Polygon(polygon.pack())

        for i in range(3):
            self.assertEqual(polygon.vertexes[0], 1)

        for i in range(3, 10):
            self.assertEqual(polygon.vertexes[i], 0)

    def test_array_oversize(self):
        polygon = Polygon(self.create_test_data())
        polygon.vertexes = [1] * 24
        self.assertRaises(ValueError, polygon.pack)

    def test_save_new_values_while_packing(self):
        poly1 = Polygon(self.create_test_data())
        poly1.x = 10
        poly1.vertexes = tuple(range(10, 0, -1))

        poly2 = Polygon(poly1.pack())
        self.assertEqual(poly2.x, 10)
        self.assertEqual(poly2.vertexes[0], 10)
        self.assertEqual(poly2.vertexes[9], 1)


class UserClass(CStruct):
    c_member_0 = Integer()
    c_member_1 = Integer()
    not_c_member = 2
    c_member_2 = Integer()

    def not_c_member_too(self):
        pass


class TestUserClass(unittest.TestCase):
    ''' Test that all members of type CType has been found. '''
    def create_test_data(self):
        return struct.pack('3i', 1, 2, 3)

    def test_c_members(self):
        obj = UserClass(self.create_test_data())
        c_members = CStruct.manager.get_c_attrs(UserClass)

        for i in range(3):
            self.assertEqual(c_members[i], 'c_member_{}'.format(i))

        self.assertEqual(len(c_members), 3)
        self.assertEqual(UserClass.not_c_member, 2)


class A(CStruct):
    a_member_0 = Integer()
    a_member_1 = Integer()


class B(A):
    b_member = Integer()


class C(B):
    c_member = Integer()


class TestInheritance(unittest.TestCase):
    ''' Inheritance behavior is:
            first - all grandparent-declared fields
            second - all parent-declared fields
            third - all class-declared fields

    Warning: multiple inheritance was not tested, and in this case
    order of fields may be random. Try to avoid it in your code.
    '''
    def test_inheritance_work(self):
        data = struct.pack('3i', 1, 2, 3)
        obj = B(data)
        for i in range(2):
            self.assertTrue(hasattr(obj, 'a_member_{}'.format(i)))
            self.assertTrue(isinstance(obj.a_member_0, int))

    def test_two_classes_inheritance(self):
        data = struct.pack('3i', 1, 2, 3)
        obj = B(data)

        # members order: first - parent members, then cls members
        self.assertEqual(obj.a_member_0, 1)
        self.assertEqual(obj.a_member_1, 2)
        self.assertEqual(obj.b_member, 3)

    def test_three_classes_inheritance(self):
        data = struct.pack('4i', 1, 2, 3, 4)
        obj = C(data)
        self.assertEqual(obj.a_member_0, 1)
        self.assertEqual(obj.a_member_1, 2)
        self.assertEqual(obj.b_member, 3)
        self.assertEqual(obj.c_member, 4)


class Package(CStruct):
    a = Integer()
    junk = Padding(4)
    b = Integer()


class TestPadding(unittest.TestCase):
    def create_test_data(self):
        return struct.pack('3i', 1, 0, 2)

    def make_assert(self, package):
        self.assertEqual(package.a, 1)
        self.assertEqual(package.b, 2)

    def test_padding_unpack(self):
        p = Package(self.create_test_data())
        self.make_assert(p)

    def test_padding_pack(self):
        p = Package(self.create_test_data())
        p.unpack(p.pack())
        self.make_assert(p)


if __name__ == '__main__':
    unittest.main()
