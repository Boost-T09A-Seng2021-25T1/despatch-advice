from src.mongodb import addOrder, getOrderInfo, deleteOrder, mongoDb
import pymongo.errors
import unittest
import asyncio
# import motor.motor_asyncio


class TestingMongo(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.testUUID = "RANDOM-123F-321F-8888-RANDOM1234"

        self.fakeOrder = {
            "ID": "999999",
            "CopyIndicator": "false",
            "UUID": self.testUUID.strip(),
            "IssueDate": "2005-06-20",
            "DocumentStatusCode": "NoStatus",
            "DespatchAdviceTypeCode": "delivery",
            "Note": "sample"
        }
        await deleteOrder(self.testUUID)

    async def asyncTearDown(self):
        await deleteOrder(self.testUUID)
        mongoDb.close()


    async def testOrderAdded(self):
        # testUUID = "RANDOM-123F-321F-8888-RANDOM1234"

        # fakeOrder = {
        #     "ID": "999999",
        #     "CopyIndicator": "false",
        #     "UUID": testUUID.strip(),
        #     "IssueDate": "2005-06-20",
        #     "DocumentStatusCode": "NoStatus",
        #     "DespatchAdviceTypeCode": "delivery",
        #     "Note": "sample"
        # }
        addOrderRes = await addOrder(self.fakeOrder)
        self.assertIsInstance(addOrderRes, object)


    # async def testOrderDuplicate(self):
        # test for duplicate insertions
        test = {"UUID": "1234"}
        await addOrder(test)
        # await asyncio.sleep(.2)
        with self.assertRaises(pymongo.errors.DuplicateKeyError):
            await addOrder(test)
        await deleteOrder("1234")
    

    # async def testFetchAndDelete(self):    
        # tests for correct fetching
        fetchedOrder = await getOrderInfo(self.testUUID)
        self.assertEqual(
            fetchedOrder["ID"], 
            self.__class__.fakeOrder["ID"]
        )

        deleteResponse = await deleteOrder(self.testUUID)
        self.assertEqual(deleteResponse, True)

        # mongoDb.close()

        # @classmethod
        # async def tearDownClass(cls):

if __name__ == '__main__':
    unittest.main()
