import unittest
from src.despatch.despatchLine import app, despatch_advice_store, despatch_lines_store
# from src.mongodb import getOrderInfo
# from src.despatch.despatchLine import despatchLineCreate

# Testing the despatch line section
class testDespatchLineCreate(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
        # Reset stores before each test
        despatch_advice_store.clear()
        despatch_lines_store.clear()
        
        # Add sample data for existing despatch ID
        despatch_advice_store["DESP-123456"] = 10

    def test_despatchNotFound(self):
        response = self.app.put(
            "/v1/despatch/DESP-123123/createDespatchLine",
            json={"delivered_quantity": 5}
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("not found", response.get_json()["message"])

    def test_missingDeliveredQuantity(self):
        response = self.app.put(
            "/v1/despatch/DESP-123456/createDespatchLine",
            json={}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing", response.get_json()["message"])

    def test_invaliDeliveredQuantityType(self):
        response = self.app.put(
            "/v1/despatch/DESP-123456/createDespatchLine",
            json={"delivered_quantity": "five"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("non-negative number", response.get_json()["message"])

    def test_deliveredExceedsOrder(self):
        response = self.app.put(
            "/v1/despatch/DESP-123456/createDespatchLine",
            json={"delivered_quantity": 15}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("exceeds", response.get_json()["message"])

    def test_missingBackorderReason(self):
        response = self.app.put(
            "/v1/despatch/DESP-123456/createDespatchLine",
            json={"delivered_quantity": 8}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("reason", response.get_json()["message"])

    def test_successfulCompletedStatus(self):
        response = self.app.put(
            "/v1/despatch/DESP-123456/createDespatchLine",
            json={"delivered_quantity": 10}
        )
        self.assertEqual(response.status_code, 200)
        lines = despatch_lines_store.get("DESP-123456", [])
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]["status"], "Completed")
        self.assertIsNone(lines[0]["backorder_reason"])

    def test_successfulRevisedStatus(self):
        response = self.app.put(
            "/v1/despatch/DESP-123456/createDespatchLine",
            json={
                "delivered_quantity": 7,
                "backorder_reason": "Out of stock"
            }
        )
        self.assertEqual(response.status_code, 200)
        lines = despatch_lines_store.get("DESP-123456", [])
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]["status"], "Revised")
        self.assertEqual(lines[0]["backorder_quantity"], 3)
        self.assertEqual(lines[0]["backorder_reason"], "Out of stock")

    def test_multipleLinesCreation(self):
        # First request
        self.app.put(
            "/v1/despatch/DESP-123456/createDespatchLine",
            json={
                "delivered_quantity": 5,
                "backorder_reason": "Partial shipment"
            }
        )
        # Second request
        self.app.put(
            "/v1/despatch/DESP-123456/createDespatchLine",
            json={"delivered_quantity": 5}
        )
        
        lines = despatch_lines_store.get("DESP-123456", [])
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0]["backorder_quantity"], 5)
        self.assertEqual(lines[1]["status"], "Completed")

if __name__ == '__main__':
    unittest.main()