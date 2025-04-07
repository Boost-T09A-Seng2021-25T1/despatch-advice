import unittest
from src.despatch.despatchLine import despatchLine
import os
import datetime
from src.mongodb import dbConnect, addOrder
import asyncio
import json


dirPath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


filePath = os.path.join(dirPath, "public", "exampleOrderDoc.json")

# UUID to use for all tests
TEST_UUID = "6E09886B-DC6E-439F-82D1-7CCAC7F4E3B1"


class TestDespatchSupplier(unittest.TestCase):

    # Due to time constraints before the submission, gen AI
    # was used to create these tests

    def setUp(self):
        self.client, self.db = asyncio.run(dbConnect())
        self.orders = self.db["orders"]

        data = {}
        with open(filePath, "r") as file:
            data = json.load(file)

        asyncio.run(addOrder(data, self.orders))

    def tearDown(self):
        # Make sure we close the client
        if hasattr(self, "client") and self.client:
            self.client.close()

    def testDespatchLineReturn(self):
        # Test invalid UUID case
        with self.assertRaises(ValueError):
            despatchLine(
                {
                    "DeliveredQuantity": 10,
                    "BackOrderQuantity": 2,
                    "ID": "DL-001",
                    "Note": "Test Note",
                    "BackOrderReason": "Stock shortage",
                    "LotNumber": 123,
                    "ExpiryDate": "2024-12-31",
                },
                "INVALID_UUID_1234",
            )

        # Create valid despatch line input
        valid_despatch = {
            "DeliveredQuantity": 10,
            "BackOrderQuantity": 2,
            "ID": "DL-001",
            "Note": "Test Note",
            "BackOrderReason": "Stock shortage",
            "LotNumber": "123",  # Changed from "LOT-123" to "123"
            "ExpiryDate": "2024-12-31",
        }

        # Get result
        res = despatchLine(valid_despatch, TEST_UUID)

        # Top-level assertions
        self.assertIn("DespatchLine", res)
        despatch = res["DespatchLine"]

        # Basic properties
        self.assertIn("ID", despatch)
        self.assertIn("Note", despatch)
        self.assertIn("LineStatusCode", despatch)
        self.assertIn("DeliveredQuantity unitCode", despatch)
        self.assertIn("BackOrderQuantity unitCode", despatch)
        self.assertIn("BackOrderReason", despatch)

        # OrderLineReference structure
        self.assertIn("OrderLineReference", despatch)
        ol_ref = despatch["OrderLineReference"]
        self.assertIn("LineID", ol_ref)
        self.assertIn("SalesOrderLineID", ol_ref)
        self.assertIn("OrderReference", ol_ref)

        # OrderReference details
        order_ref = ol_ref["OrderReference"]
        self.assertIn("ID", order_ref)
        self.assertIn("SalesOrderID", order_ref)
        self.assertIn("UUID", order_ref)
        self.assertIn("IssueDate", order_ref)

        # Item structure
        self.assertIn("Item", despatch)
        item = despatch["Item"]
        self.assertIn("Description", item)
        self.assertIn("Name", item)

        # Item identifications
        self.assertIn("BuyersItemIdentification", item)
        self.assertIn("SellersItemIdentification", item)
        # Don't assert specific IDs as they may vary depending on test data
        self.assertIsNotNone(item["BuyersItemIdentification"]["ID"])
        self.assertIsNotNone(item["SellersItemIdentification"]["ID"])

        # ItemInstance details
        self.assertIn("ItemInstance", item)
        instance = item["ItemInstance"]
        self.assertIn("LotIdentification", instance)
        lot_id = instance["LotIdentification"]
        self.assertIn("LotNumberID", lot_id)
        self.assertIn("ExpiryDate", lot_id)

        # Verify date format
        self.assertIsInstance(lot_id["ExpiryDate"], datetime.datetime)

    def test_none_input(self):
        with self.assertRaises(ValueError) as context:
            despatchLine(None, TEST_UUID)
        self.assertEqual(
            str(context.exception), "Error: insufficient information entered."
        )

    def test_missing_keys(self):
        base_dict = {
            "DeliveredQuantity": 5,
            "BackOrderQuantity": 3,
            "ID": "123",
            "Note": "Test Note",
            "BackOrderReason": "No stock",
            "LotNumber": 1001,
            "ExpiryDate": "2023-12-31",
        }

        for key in base_dict.keys():
            with self.subTest(missing_key=key):
                test_dict = base_dict.copy()
                del test_dict[key]
                with self.assertRaises(ValueError) as context:
                    despatchLine(test_dict, TEST_UUID)
                self.assertEqual(
                    str(context.exception),
                    "Error: insufficient information entered."
                )

    def test_invalid_delivered_quantity(self):
        base_dict = {
            "DeliveredQuantity": "invalid",  # Invalid value
            "BackOrderQuantity": 3,
            "ID": "123",
            "Note": "Test Note",
            "BackOrderReason": "No stock",
            "LotNumber": 1001,
            "ExpiryDate": "2023-12-31",
        }

        test_cases = [
            {"DeliveredQuantity": "five"},
            {"DeliveredQuantity": {}},
            {"DeliveredQuantity": None},
        ]

        for case in test_cases:
            with self.subTest(case=case):
                invalid_dict = {**base_dict, **case}
                with self.assertRaises(ValueError) as context:
                    despatchLine(invalid_dict, TEST_UUID)
                self.assertEqual(
                    str(context.exception),
                    "Please re-enter an amount for quantity."
                )

    def test_invalid_backorder_quantity(self):
        base_dict = {
            "DeliveredQuantity": 5,
            "ID": "123",
            "Note": "Test Note",
            "BackOrderReason": "No stock",
            "LotNumber": 1001,
            "ExpiryDate": "2023-12-31",
        }

        test_cases = [
            {"BackOrderQuantity": "three"},
            {"BackOrderQuantity": []},
            {"BackOrderQuantity": None},
        ]

        for case in test_cases:
            with self.subTest(case=case):
                invalid_dict = {**base_dict, **case}
                with self.assertRaises(ValueError) as context:
                    despatchLine(invalid_dict, TEST_UUID)
                self.assertEqual(
                    str(context.exception),
                    "Please re-enter an amount for quantity."
                )

    def test_valid_input(self):
        # Just test one case to minimize MongoDB connections
        valid_case = {
            "DeliveredQuantity": 10,
            "BackOrderQuantity": 2,
            "ID": "ID123",
            "Note": "Test Note",
            "BackOrderReason": "No stock",
            "LotNumber": 1001,
            "ExpiryDate": "2023-12-31",
        }

        try:
            result = despatchLine(valid_case, TEST_UUID)
            # Verify we got a proper result structure
            self.assertIn("DespatchLine", result)
            despatch = result["DespatchLine"]
            self.assertEqual(despatch["ID"], "ID123")
        except ValueError as e:
            self.fail(f"despatchLine raised ValueError unexpectedly: {e}")

    def test_invalid_lot_number(self):
        base_dict = {
            "DeliveredQuantity": 5,
            "BackOrderQuantity": 3,
            "ID": "123",
            "Note": "Test Note",
            "BackOrderReason": "No stock",
            "ExpiryDate": "2023-12-31",
        }

        test_cases = [{"LotNumber": {}},
                      {"LotNumber": None}, {"LotNumber": []}]

        for case in test_cases:
            with self.subTest(case=case):
                invalid_dict = {**base_dict, **case}
                with self.assertRaises(ValueError) as context:
                    despatchLine(invalid_dict, TEST_UUID)
                self.assertEqual(
                    str(context.exception),
                    "Please re-enter an amount for quantity."
                )

    def test_invalid_expiry_date(self):
        base_dict = {
            "DeliveredQuantity": 5,
            "BackOrderQuantity": 3,
            "ID": "123",
            "Note": "Test Note",
            "BackOrderReason": "No stock",
            "LotNumber": 1001,
        }

        test_cases = [
            {"ExpiryDate": "2023/12/31"},
            {"ExpiryDate": "2023-13-01"},
            {"ExpiryDate": "2023-02-30"},
            {"ExpiryDate": "12-Dec-2023"},
            {"ExpiryDate": 20231231},
            {"ExpiryDate": {}},
        ]

        for case in test_cases:
            with self.subTest(case=case):
                invalid_dict = {**base_dict, **case}
                with self.assertRaises(ValueError) as context:
                    despatchLine(invalid_dict, TEST_UUID)
                self.assertEqual(
                    str(context.exception),
                    "Please re-enter an amount for quantity."
                )

    def test_valid_new_fields(self):
        # Just test one case to minimize MongoDB connections
        test_dict = {
            "DeliveredQuantity": 5,
            "BackOrderQuantity": 3,
            "ID": "123",
            "Note": "Test Note",
            "BackOrderReason": "No stock",
            "LotNumber": 1001,
            "ExpiryDate": "2023-12-31",
        }

        try:
            result = despatchLine(test_dict, TEST_UUID)
            # Verify we got a proper result structure
            self.assertIn("DespatchLine", result)
            self.assertIn("Item", result["DespatchLine"])
            self.assertIn("ItemInstance", result["DespatchLine"]["Item"])
        except ValueError as e:
            self.fail(f"Valid case failed: {e}")


if __name__ == "__main__":
    unittest.main()
