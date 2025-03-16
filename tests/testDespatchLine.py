import unittest
import asyncio
import json
import os
from src.mongodb import dbConnect, clearDb
from src.despatch.despatchLine import DespatchLinceCreate, despatch_advice_store, despatch_lines_store

class TestDespatchLineCreate(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client, self.db = await dbConnect()
        self.orders = self.db["orders"]

        # Reset in-memory stores.
        despatch_advice_store.clear()
        despatch_lines_store.clear()

        # Add sample data: an existing despatch ID with an order quantity of 10.
        despatch_advice_store["DESP-123456"] = 10

    async def asyncTearDown(self):
        if self.client:
            await clearDb(self.db)
            self.client.close()

    async def test_despatch_not_found(self):
        event = {
            "pathParameters": {"despatchId": "DESP-123123"},
            "body": json.dumps({"delivered_quantity": 5})
        }
        response = await DespatchLinceCreate(event, None)
        self.assertEqual(response["statusCode"], 404)
        self.assertIn("not found", json.loads(response["body"])["message"].lower())

    async def test_missing_delivered_quantity(self):
        event = {
            "pathParameters": {"despatchId": "DESP-123456"},
            "body": json.dumps({})
        }
        response = await DespatchLinceCreate(event, None)
        self.assertEqual(response["statusCode"], 400)
        self.assertIn("delivered_quantity is required", json.loads(response["body"])["message"].lower())

    async def test_invalid_delivered_quantity_type(self):
        event = {
            "pathParameters": {"despatchId": "DESP-123456"},
            "body": json.dumps({"delivered_quantity": "five"})
        }
        response = await DespatchLinceCreate(event, None)
        self.assertEqual(response["statusCode"], 400)
        self.assertIn("non-negative number", json.loads(response["body"])["message"].lower())

    async def test_delivered_exceeds_order(self):
        event = {
            "pathParameters": {"despatchId": "DESP-123456"},
            "body": json.dumps({"delivered_quantity": 15})
        }
        response = await DespatchLinceCreate(event, None)
        self.assertEqual(response["statusCode"], 400)
        self.assertIn("exceeds order quantity", json.loads(response["body"])["message"].lower())

    async def test_missing_backorder_reason(self):
        event = {
            "pathParameters": {"despatchId": "DESP-123456"},
            "body": json.dumps({"delivered_quantity": 8})
        }
        response = await DespatchLinceCreate(event, None)
        self.assertEqual(response["statusCode"], 400)
        self.assertIn("backorder reason is required", json.loads(response["body"])["message"].lower())

    async def test_successful_completed_status(self):
        event = {
            "pathParameters": {"despatchId": "DESP-123456"},
            "body": json.dumps({"delivered_quantity": 10})
        }
        response = await DespatchLinceCreate(event, None)
        self.assertEqual(response["statusCode"], 200)
        lines = despatch_lines_store.get("DESP-123456", [])
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]["status"], "Completed")
        self.assertIsNone(lines[0]["backorder_reason"])

    async def test_successful_revised_status(self):
        event = {
            "pathParameters": {"despatchId": "DESP-123456"},
            "body": json.dumps({"delivered_quantity": 7, "backorder_reason": "Out of stock"})
        }
        response = await DespatchLinceCreate(event, None)
        self.assertEqual(response["statusCode"], 200)
        lines = despatch_lines_store.get("DESP-123456", [])
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]["status"], "Revised")
        self.assertEqual(lines[0]["backorder_quantity"], 3)
        self.assertEqual(lines[0]["backorder_reason"], "Out of stock")

    async def test_multiple_lines_creation(self):
        event1 = {
            "pathParameters": {"despatchId": "DESP-123456"},
            "body": json.dumps({"delivered_quantity": 5, "backorder_reason": "Partial shipment"})
        }
        response1 = await DespatchLinceCreate(event1, None)
        self.assertEqual(response1["statusCode"], 200)

        event2 = {
            "pathParameters": {"despatchId": "DESP-123456"},
            "body": json.dumps({"delivered_quantity": 5})
        }
        response2 = await DespatchLinceCreate(event2, None)
        self.assertEqual(response2["statusCode"], 200)

        lines = despatch_lines_store.get("DESP-123456", [])
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0]["backorder_quantity"], 5)
        self.assertEqual(lines[1]["status"], "Completed")

if __name__ == '__main__':
    unittest.main()
