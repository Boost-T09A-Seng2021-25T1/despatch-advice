import json
import unittest
from unittest.mock import patch, MagicMock
from src.despatch.despatchLine import despatchLineCreate

class TestLambdaFunction(unittest.TestCase):
    @patch("lambda_function.collection")
    def test_missing_body(self, mock_collection):
        event = {}  # No "body" in event
        result = despatchLineCreate(event, None)
        self.assertEqual(result["statusCode"], 400)
        self.assertIn("Request body missing", result["body"])

    @patch("lambda_function.collection")
    def test_invalid_json(self, mock_collection):
        # Event body that cannot be parsed as JSON
        event = {"body": "not a valid json"}
        result = despatchLineCreate(event, None)
        self.assertEqual(result["statusCode"], 400)
        self.assertIn("Invalid JSON format", result["body"])

    @patch("lambda_function.collection")
    def test_missing_order_id(self, mock_collection):
        event = {"body": json.dumps({"some_field": "value"})}
        result = despatchLineCreate(event, None)
        self.assertEqual(result["statusCode"], 400)
        self.assertIn("order_id is required", result["body"])

    @patch("lambda_function.collection")
    def test_duplicate_order_id(self, mock_collection):
        # Simulate that the collection already has a record with the given order_id
        mock_collection.find_one.return_value = {"order_id": "order123"}
        event = {"body": json.dumps({"order_id": "order123"})}
        result = despatchLineCreate(event, None)
        self.assertEqual(result["statusCode"], 409)
        self.assertIn("Despatch advice for this order already exists", result["body"])

    @patch("lambda_function.collection")
    def test_successful_insertion(self, mock_collection):
        # Simulate that there is no existing despatch advice for the order
        mock_collection.find_one.return_value = None
        # Simulate successful insertion (the return value is not used in the handler)
        mock_collection.insert_one.return_value = MagicMock()
        order_id = "order456"
        event = {"body": json.dumps({"order_id": order_id})}
        result = despatchLineCreate(event, None)
        self.assertEqual(result["statusCode"], 200)
        response_body = json.loads(result["body"])
        self.assertEqual(response_body["order_id"], order_id)
        self.assertEqual(response_body["status"], "Initiated")
        self.assertTrue(response_body["despatch_id"].startswith("D-"))
        self.assertEqual(response_body["xml"], f"<DespatchAdvice><OrderId>{order_id}</OrderId></DespatchAdvice>")
        self.assertEqual(response_body["lines"], [])

if __name__ == '__main__':
    unittest.main()