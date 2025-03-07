import unittest
from src/dummyFile.py import testingPipeline

class testing(unittest.TestCase):

    def testDummyTestingFile():
        self.assertEqual(testingPipeline, False)

if __name__ == '__main__':
    unittest.main()