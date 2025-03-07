import unittest
from src.dummyFile.py import testingPipeline


class Testing(unittest.TestCase):

    def testDummyTestingFile(self):
        self.assertEqual(testingPipeline, False)


if __name__ == '__main__':
    unittest.main()
