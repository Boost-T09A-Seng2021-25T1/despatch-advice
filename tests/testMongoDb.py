from src.mongodb import addOrder, getOrderInfo, deleteOrder
import unittest


class TestingMongo(unittest.IsolatedAsyncioTestCase):

    async def testOrderAdded(self):
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
        addOrderRes = await addOrder(newDummyOrderDoc)
        self.assertIsInstance(addOrderRes, object)

        fetchedOrder = await getOrderInfo(testUUID)
        self.assertEqual(fetchedOrder["ID"], newDummyOrderDoc["ID"])

        deleteResponse = await deleteOrder(testUUID)
        self.assertEqual(deleteResponse, True)


if __name__ == '__main__':
    unittest.main()
