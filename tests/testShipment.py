from src.mongodb import dbConnect, clearDb
from src.despatch.shipment import create_shipment, setup_indexes
import unittest
import json
import os

# Construct the full path to the JSON file in the 'public' folder
dirPath = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
filePath = os.path.join(dirPath, "public", "exampleShipmentDoc.json")


class TestShipmentCreation(unittest.IsolatedAsyncioTestCase):
    # ============================================
    # These two funcs run before and after every test
    async def asyncSetUp(self):
        """Set up the MongoDB connection and load test data."""
        # Check if the JSON file exists
        if not os.path.exists(filePath):
            self.fail(f"JSON file not found at: {filePath}")

        self.client, self.db = await dbConnect()
        self.shipments = self.db["shipments"]
        await clearDb(self.db)  # Clear the database before each test
        index_result = await setup_indexes()  # Ensure indexes are set up
        self.assertTrue(index_result["success"], "Index setup failed")

        # Load test data from JSON file
        with open(filePath, "r") as file:
            self.valid_payload = json.load(file)

        # Define test data
        self.valid_shipment_id = "SHIP-123456"
        self.invalid_shipment_id = "SHIP-INVALID"

    async def asyncTearDown(self):
        """Clean up after each test."""
        if self.client:
            await self.shipments.delete_many({})
            self.client.close()
    # ============================================
    # ============================================

    async def test_create_shipment_success(self):
        """Test successful creation of a shipment."""
        result = await create_shipment(
            self.valid_shipment_id, self.valid_payload
        )
        self.assertTrue(
            result["success"], f"Expected success but got: {result}"
        )
        self.assertIn("inserted_id", result)
        self.assertIn("document", result)
        self.assertEqual(result["document"]["ID"], self.valid_shipment_id)
        self.assertTrue(result["operation_details"]["acknowledged"])

    async def test_create_shipment_duplicate_id(self):
        """Test creating a shipment with a duplicate ID."""
        # First insertion (should succeed)
        first_result = await create_shipment(
            self.valid_shipment_id, self.valid_payload
        )
        self.assertTrue(first_result["success"])

        # Second insertion (should fail due to duplicate ID)
        duplicate_result = await create_shipment(
            self.valid_shipment_id, self.valid_payload
        )
        self.assertFalse(duplicate_result["success"])
        self.assertEqual(duplicate_result["error"], "Duplicate shipment ID")
        self.assertIn("existing_document", duplicate_result)
        self.assertEqual(
            duplicate_result["existing_document"]["ID"],
            self.valid_shipment_id
        )
        self.assertIn("attempted_data", duplicate_result)

    async def test_create_shipment_invalid_id_format(self):
        """Test creating a shipment with an invalid ID format."""
        with self.assertRaises(ValueError):
            await create_shipment(
                self.invalid_shipment_id, self.valid_payload
            )

    async def test_create_shipment_missing_required_fields(self):
        """Test creating a shipment with missing required fields."""
        invalid_payload = self.valid_payload.copy()
        del invalid_payload["Delivery"]  # Remove required field
        with self.assertRaises(ValueError):
            await create_shipment(
                self.valid_shipment_id, invalid_payload
            )

    async def test_create_shipment_invalid_data_type(self):
        """Test creating a shipment with invalid data types."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload["ID"] = 123456  # Invalid type (should be string)
        with self.assertRaises(TypeError):
            await create_shipment(
                self.valid_shipment_id, invalid_payload
            )

    async def test_create_shipment_empty_data(self):
        """Test creating a shipment with empty data."""
        with self.assertRaises(ValueError):
            await create_shipment(self.valid_shipment_id, {})

    async def test_create_shipment_invalid_consignment_id_type(self):
        """Test creating a shipment with an invalid consignment ID type."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload["Consignment"]["ID"] = 123
        with self.assertRaises(TypeError):
            await create_shipment(
                self.valid_shipment_id, invalid_payload
            )

    async def test_create_shipment_large_data(self):
        """Test creating a shipment with a large amount of data."""
        large_payload = self.valid_payload.copy()
        large_payload["AdditionalData"] = {
            "LargeField": "A" * 1000000
        }  # Large data field
        result = await create_shipment(
            self.valid_shipment_id, large_payload
        )
        self.assertTrue(result["success"])
        self.assertIn("inserted_id", result)
        self.assertIn("document", result)
        self.assertEqual(
            result["document"]["AdditionalData"]["LargeField"],
            "A" * 1000000
        )

    async def test_setup_indexes(self):
        """Test that indexes are properly set up."""
        result = await setup_indexes()
        self.assertTrue(result["success"])
        self.assertEqual(result["index_name"], "ID")
        self.assertIn("operation_result", result)


if __name__ == "__main__":
    unittest.main()
