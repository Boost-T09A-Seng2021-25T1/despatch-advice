import unittest
from src.mongodb import dbConnect, clearDb
from src.despatch.OrderReference\
    import OrderNotFoundError, InvalidOrderReferenceError, \
    create_order_reference
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
            "UUID": "existing-uuid",
            "IssueDate": "2023-01-01",
            "AdditionalField": "should-be-preserved"
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
        result = await create_order_reference(
            self.valid_order_id, self.valid_sales_order_id, self.orders)
        
        # Verify the returned document
        self.assertIsInstance(result, dict)
        self.assertEqual(result["ID"], self.valid_order_id)
        self.assertEqual(result["SalesOrderID"], self.valid_sales_order_id)
        self.assertEqual(result["UUID"], "existing-uuid")  # Existing field preserved
        self.assertEqual(result["IssueDate"], "2023-01-01")  # Existing field preserved
        self.assertEqual(result["AdditionalField"], "should-be-preserved")  # Additional field preserved

    async def test_order_reference_fields_initialized_correctly(self):
        """Ensure existing fields are preserved after creation."""
        result = await create_order_reference(
            self.valid_order_id, self.valid_sales_order_id, self.orders)
        
        self.assertEqual(result["UUID"], "existing-uuid")
        self.assertEqual(result["IssueDate"], "2023-01-01")

    async def test_id_and_sales_order_id_persisted(self):
        """Ensure ID and SalesOrderID are correctly set in returned document."""
        result = await create_order_reference(
            self.valid_order_id, self.valid_sales_order_id, self.orders)
        
        self.assertEqual(result["ID"], self.valid_order_id)
        self.assertEqual(result["SalesOrderID"], self.valid_sales_order_id)

    async def test_create_multiple_order_references(self):
        """Test creating multiple order references doesn't override existing ones."""
        new_order_id = self.test_data["new_order_id"]
        new_sales_order_id = self.test_data["new_sales_order_id"]

        # Insert the new order into the database
        await self.orders.insert_one({
            "ID": new_order_id,
            "SalesOrderID": "original-sales-id",
            "UUID": "original-uuid",
            "IssueDate": "original-date",
            "CustomField": "custom-value"
        })

        # Create the order reference
        result = await create_order_reference(
            new_order_id, new_sales_order_id, self.orders)

        # Verify the returned document
        self.assertEqual(result["ID"], new_order_id)
        self.assertEqual(result["SalesOrderID"], new_sales_order_id)  # Updated field
        self.assertEqual(result["UUID"], "original-uuid")  # Preserved field
        self.assertEqual(result["CustomField"], "custom-value")  # Additional preserved field

    # ============================================
    # Failing Tests
    # ============================================

    async def test_create_order_reference_missing_id(self):
        """Test error when OrderId is missing."""
        with self.assertRaises(InvalidOrderReferenceError):
            await create_order_reference(None,
                                         self.valid_sales_order_id,
                                         self.orders)

    async def test_create_order_reference_missing_sales_order_id(self):
        """Test error when SalesOrderID is missing."""
        with self.assertRaises(InvalidOrderReferenceError):
            await create_order_reference(self.valid_order_id,
                                         None, self.orders)

    async def test_create_order_reference_nonexistent_order(self):
        """Test 404 error when order does not exist."""
        nonexistent_order_id = self.test_data["nonexistent_order_id"]
        nonexistent_sales_order_id =\
            self.test_data["nonexistent_sales_order_id"]
        with self.assertRaises(OrderNotFoundError):
            await create_order_reference(nonexistent_order_id,
                                         nonexistent_sales_order_id,
                                         self.orders)

    async def test_create_order_reference_invalid_types(self):
        """Test 400 error when incorrect types are provided."""
        with self.assertRaises(InvalidOrderReferenceError):
            await create_order_reference(12345, ["invalid-list"], self.orders)


if __name__ == '__main__':
    unittest.main()
