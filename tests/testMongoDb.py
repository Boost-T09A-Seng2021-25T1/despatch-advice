from src.mongodb import addOrder, getOrderInfo, deleteOrder
import unittest


class TestingMongo(unittest.TestCase):

    def testOrderAdded(self):
        testUUID = "RANDOM-123F-321F-8888-RANDOM1234"

        newDummyOrderDoc = {
            "ID": "999999",
            "CopyIndicator": "false",
            "UUID": testUUID.strip(),
            "IssueDate": "2005-06-20",
            "DocumentStatusCode": "NoStatus",
            "DespatchAdviceTypeCode": "delivery",
            "Note": "sample"
        }
        self.assertIsInstance(addOrder(newDummyOrderDoc), object)

        fetchedOrder = getOrderInfo(testUUID)
        self.assertEqual(fetchedOrder["ID"], newDummyOrderDoc["ID"])

        self.assertEqual(deleteOrder(testUUID), True)


if __name__ == '__main__':
    unittest.main()
