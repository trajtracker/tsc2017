import unittest
from TestUtils import TestTouchpad


class Tsc2017Tests(unittest.TestCase):

    #------------------------------------------------------------------------------
    def test_create_and_configure(self):
        TestTouchpad()
        self.assertRaises(TypeError, lambda: TestTouchpad(reverse_left_right=1))
        self.assertRaises(TypeError, lambda: TestTouchpad(reverse_left_right=None))
        self.assertRaises(TypeError, lambda: TestTouchpad(reverse_up_down=1))
        self.assertRaises(TypeError, lambda: TestTouchpad(reverse_up_down=None))

    #------------------------------------------------------------------------------
    def test_types(self):
        tp = TestTouchpad()
        tp.connect("dummy")
        self.assertEqual(int, type(tp.get_data()[0]))
        self.assertEqual(int, type(tp.get_data()[1]))

    #------------------------------------------------------------------------------
    def test_reverse_h(self):
        tp = TestTouchpad()
        tp.connect("dummy")
        tp.data = True, 3048, 3048

        self.assertEqual((True, 1000, 1000), tp.get_data())

        tp.reverse_left_right = True
        self.assertEqual((True, -1000, 1000), tp.get_data())

    #------------------------------------------------------------------------------
    def test_reverse_v(self):
        tp = TestTouchpad()
        tp.connect("dummy")
        tp.data = True, 3048, 3048
        tp.reverse_up_down = True
        self.assertEqual((True, 1000, -1000), tp.get_data())

    #------------------------------------------------------------------------------
    def test_change_center(self):
        tp = TestTouchpad()
        tp.connect("dummy")
        tp.data = True, 3048, 3048
        tp.output_center = (500, 500)
        self.assertEqual((True, 1500, 1500), tp.get_data())

    #------------------------------------------------------------------------------
    def test_change_center_and_reverse(self):
        tp = TestTouchpad()
        tp.connect("dummy")
        tp.data = True, 3048, 3048
        tp.output_center = (500, 500)
        tp.reverse_left_right = True
        self.assertEqual((True, -500, 1500), tp.get_data())

    #------------------------------------------------------------------------------
    def test_change_screen_size(self):
        tp = TestTouchpad()
        tp.connect("dummy")
        tp.data = True, 1024, 1024
        tp.output_screen_size = (2000, 1000)
        self.assertEqual((True, -500, -250), tp.get_data())


if __name__ == '__main__':
    unittest.main()
