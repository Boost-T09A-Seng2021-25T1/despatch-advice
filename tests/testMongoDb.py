from src.mongodb import addOrder, getOrderInfo, deleteOrder, dbConnect
import pymongo.errors
import unittest
import motor.motor_asyncio


testUUID = "RANDOM-123F-321F-8888-RANDOM1234"
fakeOrder = {
    "ID": "999999",
    "CopyIndicator": "false",
    "UUID": testUUID.strip(),
    "IssueDate": "2005-06-20",
    "DocumentStatusCode": "NoStatus",
    "DespatchAdviceTypeCode": "delivery",
    "Note": "sample"
}


class TestOrder(unittest.IsolatedAsyncioTestCase):

    # ============================================
    # These two funcs run before and after every test
    async def asyncSetUp(self):
        # isolated connection to db for every test
        self.client, self.db = await dbConnect()
        self.orders = self.db["orders"]

    async def asyncTearDown(self):
        self.client.close()
    # ============================================

    async def testOrderAdded(self):
        addOrderRes = await addOrder(fakeOrder, self.orders)
        self.assertIsInstance(addOrderRes, object)

        # test for duplicate insertions
        test = {"UUID": "1234"}
        await addOrder(test, self.orders)

        with self.assertRaises(pymongo.errors.DuplicateKeyError):
            await addOrder(test, self.orders)
        await deleteOrder("1234", self.orders)

    async def testFetchAndDelete(self):
        await addOrder(fakeOrder, self.orders)
        # tests for correct fetching
        fetchedOrder = await getOrderInfo(testUUID, self.orders)
        self.assertEqual(
            fetchedOrder["ID"],
            fakeOrder["ID"]
        )

        self.assertEqual(
            await deleteOrder(testUUID, self.orders),
            True
        )

        self.assertEqual(
            await deleteOrder("FAKKEEE", self.orders),
            False
        )

    async def testDbConnect(self):
        client, db = await dbConnect()

        self.assertIsInstance(
            client,
            motor.motor_asyncio.AsyncIOMotorClient
        )

        self.assertIsInstance(
            db,
            motor.motor_asyncio.AsyncIOMotorDatabase
        )
        client.close()


if __name__ == '__main__':
    unittest.main()
