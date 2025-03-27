import unittest
from src.mongodb import dbConnect, clearDb
from src.despatch.OrderReference\
    import OrderNotFoundError, InvalidOrderReferenceError, \
    createOrderReference
import os
import json

# Construct the full path to the JSON file in the 'public' folder
dirPath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
filePath = os.path.join(dirPath, "public", "exampleOrderReference.json")


class TestCreateOrderReference(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        """Setup valid test data and database connection."""
        self.client, self.db = await dbConnect()
        self.orders = self.db["orders"]

        # Load test data from JSON file
        with open(filePath, "r") as file:
            self.test_data = json.load(file)

        # Insert the test order into the database
        self.valid_order_id = self.test_data["valid_order_id"]
        self.valid_sales_order_id = self.test_data["valid_sales_order_id"]

        # Insert the order into the database
        await self.orders.insert_one({
            "ID": self.valid_order_id,
            "SalesOrderID": self.valid_sales_order_id,
            "UUID": "",
            "IssueDate": ""
        })

    async def asyncTearDown(self):
        """Clean up the database after each test."""
        if self.client.close:
            await clearDb(self.db)
            self.client.close()

    # ============================================
    # Success Tests
    # ============================================

    async def test_create_order_reference_success(self):
        """Test successful creation of OrderReference."""
        result = await createOrderReference(
            self.valid_order_id, self.valid_sales_order_id, self.orders)
        self.assertIsNone(result)

        # Verify the order reference was created
        order_ref = await self.orders.find_one({"ID": self.valid_order_id})
        self.assertEqual(order_ref["ID"], self.valid_order_id)
        self.assertEqual(order_ref["SalesOrderID"], self.valid_sales_order_id)

    async def test_order_reference_fields_initialized_correctly(self):
        """Ensure UUID and IssueDate are empty after creation."""
        order_ref = await self.orders.find_one({"ID": self.valid_order_id})
        self.assertEqual(order_ref["UUID"], "")
        self.assertEqual(order_ref["IssueDate"], "")

    async def test_id_and_sales_order_id_persisted(self):
        """Ensure ID and SalesOrderID are correctly set."""
        order_ref = await self.orders.find_one({"ID": self.valid_order_id})
        self.assertEqual(order_ref["ID"], self.valid_order_id)
        self.assertEqual(order_ref["SalesOrderID"], self.valid_sales_order_id)

    async def test_create_multiple_order_references(self):
        """Test creating multiple order references
        doesn't override existing ones."""
        new_order_id = self.test_data["new_order_id"]
        new_sales_order_id = self.test_data["new_sales_order_id"]

        # Insert the new order into the database
        await self.orders.insert_one({
            "ID": new_order_id,
            "SalesOrderID": new_sales_order_id,
            "UUID": "",
            "IssueDate": ""
        })

        # Create the order reference
        await createOrderReference(new_order_id,
                                   new_sales_order_id, self.orders)

        # Verify the new order reference
        new_order_ref = await self.orders.find_one({"ID": new_order_id})
        self.assertEqual(new_order_ref["ID"], new_order_id)
        self.assertEqual(new_order_ref["SalesOrderID"], new_sales_order_id)

    # ============================================
    # Failing Tests
    # ============================================

    async def test_create_order_reference_missing_id(self):
        """Test error when OrderId is missing."""
        with self.assertRaises(InvalidOrderReferenceError):
            await createOrderReference(None,
                                       self.valid_sales_order_id, self.orders)

    async def test_create_order_reference_missing_sales_order_id(self):
        """Test error when SalesOrderID is missing."""
        with self.assertRaises(InvalidOrderReferenceError):
            await createOrderReference(self.valid_order_id, None, self.orders)

    async def test_create_order_reference_nonexistent_order(self):
        """Test 404 error when order does not exist."""
        nonexistent_order_id = self.test_data["nonexistent_order_id"]
        nonexistent_sales_order_id =\
            self.test_data["nonexistent_sales_order_id"]
        with self.assertRaises(OrderNotFoundError):
            await createOrderReference(nonexistent_order_id,
                                       nonexistent_sales_order_id, self.orders)

    async def test_create_order_reference_invalid_types(self):
        """Test 400 error when incorrect types are provided."""
        with self.assertRaises(InvalidOrderReferenceError):
            await createOrderReference(12345, ["invalid-list"], self.orders)


if __name__ == '__main__':
    unittest.main()
