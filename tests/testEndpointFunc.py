from src.mongodb import dbConnect, clearDb, addOrder
from src.apiEndpoint import endpointFunc
import unittest
import os


os.path.abspath(os.path.join(
    os.path.dirname(__file__), ".."))


class testDespatchSupplier(unittest.TestCase):

    # ============================================
    # These two funcs run before and after every test
    # def setUp(self):

    # def tearDown(self):

    # ============================================
    # ============================================


    def testForNone(self):
        invalidArgs = [
            (None, {}, {}, {}),
            ("", None, {}, {}),
            ("", {}, None, {}),
            ("", {}, {}, None),
            (123, {}, {}, {}),
            ("", 123, {}, {}),
            ("", {}, 123, {}),
            ("", {}, {}, 123)
        ]

        for arguments in invalidArgs:
            with self.assertRaises(TypeError):
                endpointFunc(*arguments)


if __name__ == '__main__':
    unittest.main()
