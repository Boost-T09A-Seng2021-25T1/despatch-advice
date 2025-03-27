import unittest
from src.mongodb import dbConnect, clearDb
from src.despatch.OrderReference import (
    OrderNotFoundError,
    InvalidOrderReferenceError,
    createOrderReference
)
import os
import json
from datetime import datetime
import uuid

# Construct the full path to the JSON file
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

        # Insert test orders into the database
        self.valid_order_id = self.test_data["valid_order_id"]
        self.valid_sales_order_id = self.test_data["valid_sales_order_id"]
        self.existing_uuid_order_id = self.test_data["existing_uuid_order_id"]
        self.existing_issue_date_order_id = self.test_data["existing_issue_date_order_id"]
        
        await self.orders.insert_many([
            {
                "ID": self.valid_order_id,
                "SalesOrderID": self.valid_sales_order_id,
                "UUID": "",
                "IssueDate": ""
            },
            {
                "ID": self.existing_uuid_order_id,
                "SalesOrderID": "SO-456",
                "UUID": str(uuid.uuid4()),
                "IssueDate": ""
            },
            {
                "ID": self.existing_issue_date_order_id,
                "SalesOrderID": "SO-789",
                "UUID": "",
                "IssueDate": datetime.utcnow().isoformat()
            }
        ])

    async def asyncTearDown(self):
        """Clean up the database after each test."""
        if self.client:
            await clearDb(self.db)
            await self.client.close()

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
        await createOrderReference(
            self.valid_order_id, self.valid_sales_order_id, self.orders)
        order_ref = await self.orders.find_one({"ID": self.valid_order_id})
        self.assertEqual(order_ref["UUID"], "")
        self.assertEqual(order_ref["IssueDate"], "")

    async def test_id_and_sales_order_id_persisted(self):
        """Ensure ID and SalesOrderID are correctly set."""
        await createOrderReference(
            self.valid_order_id, self.valid_sales_order_id, self.orders)
        order_ref = await self.orders.find_one({"ID": self.valid_order_id})
        self.assertEqual(order_ref["ID"], self.valid_order_id)
        self.assertEqual(order_ref["SalesOrderID"], self.valid_sales_order_id)

    async def test_create_multiple_order_references(self):
        """Test creating multiple order references doesn't override existing ones."""
        new_order_id = self.test_data["new_order_id"]
        new_sales_order_id = self.test_data["new_sales_order_id"]

        await self.orders.insert_one({
            "ID": new_order_id,
            "SalesOrderID": new_sales_order_id,
            "UUID": "",
            "IssueDate": ""
        })

        await createOrderReference(new_order_id, new_sales_order_id, self.orders)

        # Verify both orders exist
        original_order = await self.orders.find_one({"ID": self.valid_order_id})
        new_order = await self.orders.find_one({"ID": new_order_id})
        self.assertIsNotNone(original_order)
        self.assertIsNotNone(new_order)

    async def test_create_with_existing_uuid_does_not_modify(self):
        """Test that existing UUID is not modified."""
        order_ref_before = await self.orders.find_one({"ID": self.existing_uuid_order_id})
        original_uuid = order_ref_before["UUID"]
        
        await createOrderReference(
            self.existing_uuid_order_id, 
            "SO-456", 
            self.orders
        )
        
        order_ref_after = await self.orders.find_one({"ID": self.existing_uuid_order_id})
        self.assertEqual(order_ref_after["UUID"], original_uuid)

    async def test_create_with_existing_issue_date_does_not_modify(self):
        """Test that existing IssueDate is not modified."""
        order_ref_before = await self.orders.find_one({"ID": self.existing_issue_date_order_id})
        original_issue_date = order_ref_before["IssueDate"]
        
        await createOrderReference(
            self.existing_issue_date_order_id, 
            "SO-789", 
            self.orders
        )
        
        order_ref_after = await self.orders.find_one({"ID": self.existing_issue_date_order_id})
        self.assertEqual(order_ref_after["IssueDate"], original_issue_date)

    # ============================================
    # Failing Tests
    # ============================================

    async def test_create_order_reference_missing_id(self):
        """Test error when OrderId is missing."""
        with self.assertRaises(InvalidOrderReferenceError):
            await createOrderReference(None, self.valid_sales_order_id, self.orders)

    async def test_create_order_reference_missing_sales_order_id(self):
        """Test error when SalesOrderID is missing."""
        with self.assertRaises(InvalidOrderReferenceError):
            await createOrderReference(self.valid_order_id, None, self.orders)

    async def test_create_order_reference_nonexistent_order(self):
        """Test 404 error when order does not exist."""
        nonexistent_order_id = self.test_data["nonexistent_order_id"]
        nonexistent_sales_order_id = self.test_data["nonexistent_sales_order_id"]
        with self.assertRaises(OrderNotFoundError):
            await createOrderReference(
                nonexistent_order_id,
                nonexistent_sales_order_id,
                self.orders
            )

    async def test_create_order_reference_invalid_types(self):
        """Test 400 error when incorrect types are provided."""
        with self.assertRaises(InvalidOrderReferenceError):
            await createOrderReference(12345, ["invalid-list"], self.orders)

    async def test_empty_string_order_id(self):
        """Test error when OrderId is empty string."""
        with self.assertRaises(InvalidOrderReferenceError):
            await createOrderReference("", self.valid_sales_order_id, self.orders)

    async def test_empty_string_sales_order_id(self):
        """Test error when SalesOrderID is empty string."""
        with self.assertRaises(InvalidOrderReferenceError):
            await createOrderReference(self.valid_order_id, "", self.orders)

    async def test_whitespace_only_order_id(self):
        """Test error when OrderId contains only whitespace."""
        with self.assertRaises(InvalidOrderReferenceError):
            await createOrderReference("   ", self.valid_sales_order_id, self.orders)

    async def test_whitespace_only_sales_order_id(self):
        """Test error when SalesOrderID contains only whitespace."""
        with self.assertRaises(InvalidOrderReferenceError):
            await createOrderReference(self.valid_order_id, "   ", self.orders)

    async def test_sql_injection_attempt(self):
        """Test that SQL injection attempts are properly handled."""
        with self.assertRaises(InvalidOrderReferenceError):
            await createOrderReference(
                "1; DROP TABLE orders; --",
                self.valid_sales_order_id,
                self.orders
            )

    async def test_xss_attempt(self):
        """Test that XSS attempts are properly handled."""
        with self.assertRaises(InvalidOrderReferenceError):
            await createOrderReference(
                "<script>alert('xss')</script>",
                self.valid_sales_order_id,
                self.orders
            )

    async def test_very_long_order_id(self):
        """Test error when OrderId is excessively long."""
        with self.assertRaises(InvalidOrderReferenceError):
            await createOrderReference(
                "A" * 1001,  # Assuming 1000 is max length
                self.valid_sales_order_id,
                self.orders
            )


if __name__ == '__main__':
    unittest.main()