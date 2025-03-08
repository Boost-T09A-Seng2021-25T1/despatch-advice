import unittest
from src.dummyFile import testingPipeline


# Dummy test that checks if the return is false.
class Testing(unittest.TestCase):

    def testDummyTestingFile(self):
        self.assertEqual(testingPipeline(), False)


if __name__ == '__main__':
    unittest.main()
