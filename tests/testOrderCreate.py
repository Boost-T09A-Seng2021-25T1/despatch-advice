import unittest
import os
import sys
import json
from unittest.mock import patch, MagicMock, AsyncMock

from src.despatch.orderCreate import (
    validate_order_document,
    create_order,
    validate_order,
    get_order,
    check_stock,
)

dirPath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(dirPath)


class TestOrderCreate(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.valid_order_json = {
            "ID": "ORD-12345",
            "UUID": "550e8400-e29b-41d4-a716-446655440000",
            "IssueDate": "2025-03-15",
            "CustomerID": "CUST-001",
            "Items": [
                {"item_id": "ITEM-001", "quantity": 5, "price": 10.5},
                {"item_id": "ITEM-002", "quantity": 3, "price": 15.75},
            ],
        }

        self.valid_order_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <Order xmlns="urn:oasis:names:specification:ubl:schema:xsd:Order-2"
               xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
               xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
            <cbc:ID>ORD-12345</cbc:ID>
            <cbc:UUID>550e8400-e29b-41d4-a716-446655440000</cbc:UUID>
            <cbc:IssueDate>2025-03-15</cbc:IssueDate>
            <cbc:BuyerReference>CUST-001</cbc:BuyerReference>
            <cac:OrderLine>
                <cac:LineItem>
                    <cbc:Quantity>5</cbc:Quantity>
                    <cac:Item>
                        <cac:SellersItemIdentification>
                            <cbc:ID>ITEM-001</cbc:ID>
                        </cac:SellersItemIdentification>
                    </cac:Item>
                    <cac:Price>
                        <cbc:PriceAmount>10.50</cbc:PriceAmount>
                    </cac:Price>
                </cac:LineItem>
            </cac:OrderLine>
        </Order>"""

        self.valid_event_body = {
            "customer_id": "CUST-001",
            "items": [
                {"item_id": "ITEM-001", "quantity": 5, "price": 10.5},
                {"item_id": "ITEM-002", "quantity": 3, "price": 15.75},
            ],
        }

        self.sample_order = {
            "OrderID": "ORD-12345",
            "UUID": "550e8400-e29b-41d4-a716-446655440000",
            "CustomerID": "CUST-001",
            "Items": [
                {"item_id": "ITEM-001", "quantity": 5, "price": 10.5},
                {"item_id": "ITEM-002", "quantity": 3, "price": 15.75},
            ],
            "Status": "Created",
            "CreationDate": "2025-03-15T10:00:00",
            "LastModified": "2025-03-15T10:00:00",
        }

        # Use AsyncMock for better coroutine mocking
        self.client = MagicMock()
        self.db = MagicMock()

        # Set up db mock with orders collection
        self.db.orders = MagicMock()
        self.db.orders.find_one = AsyncMock()
        self.db.orders.insert_one = AsyncMock()
        self.db.orders.update_one = AsyncMock()
        self.db.orders.delete_one = AsyncMock()

    async def asyncTearDown(self):
        if hasattr(self, "client") and hasattr(self.client, "close"):
            self.client.close()

    async def test_validate_order_document_valid_json(self):
        is_valid, issues, document = await validate_order_document(
            self.valid_order_json
        )

        self.assertTrue(is_valid)
        self.assertEqual(len(issues), 0)
        self.assertEqual(document, self.valid_order_json)

    @patch("src.despatch.orderCreate.xml_to_json")
    async def test_validate_order_document_valid_xml(self, mock_xml_to_json):
        mock_xml_to_json.return_value = self.valid_order_json

        is_valid, issues, document = await validate_order_document(
            self.valid_order_xml, "xml"
        )

        self.assertTrue(is_valid)
        self.assertEqual(len(issues), 0)
        self.assertEqual(document, self.valid_order_json)
        mock_xml_to_json.assert_called_once_with(self.valid_order_xml)

    @patch("src.despatch.orderCreate.xml_to_json")
    async def test_validate_order_document_xml_parsing_error(
        self, mock_xml_to_json
    ):
        mock_xml_to_json.side_effect = ValueError("XML parsing error")

        is_valid, issues, document = await validate_order_document(
            self.valid_order_xml, "xml"
        )

        self.assertFalse(is_valid)
        self.assertEqual(len(issues), 1)
        self.assertIn("XML parsing error", issues[0])
        self.assertIsNone(document)
        mock_xml_to_json.assert_called_once_with(self.valid_order_xml)

    async def test_validate_order_document_missing_required_fields(self):
        invalid_order = {
            "UUID": "550e8400-e29b-41d4-a716-446655440000",
            "IssueDate": "2025-03-15",
            "Items": [],
        }

        is_valid, issues, document = await validate_order_document(
            invalid_order)

        self.assertFalse(is_valid)
        self.assertGreater(len(issues), 0)
        self.assertIn("Missing required field: ID", issues)
        self.assertIn("Missing CustomerID", issues)
        self.assertIn("No items in order", issues)
        self.assertEqual(document, invalid_order)

    async def test_validate_order_document_invalid_items(self):
        invalid_order = {
            "ID": "ORD-12345",
            "UUID": "550e8400-e29b-41d4-a716-446655440000",
            "IssueDate": "2025-03-15",
            "CustomerID": "CUST-001",
            "Items": [
                {"quantity": 5, "price": 10.5},
                {"item_id": "ITEM-002", "quantity": -3, "price": 15.75},
                {"item_id": "ITEM-003", "quantity": 2, "price": -5.0},
            ],
        }

        is_valid, issues, document = await validate_order_document(
            invalid_order)

        self.assertFalse(is_valid)
        self.assertGreater(len(issues), 0)
        self.assertIn("Item 0 missing item_id", issues)
        self.assertIn("Item 1 has invalid quantity", issues)
        self.assertIn("Item 2 has invalid price", issues)
        self.assertEqual(document, invalid_order)

    @patch("src.despatch.orderCreate.dbConnect", new_callable=AsyncMock)
    @patch("src.despatch.orderCreate.addOrder", new_callable=AsyncMock)
    @patch("uuid.uuid4")
    async def test_create_order_success(
        self, mock_uuid, mock_add_order, mock_db_connect
    ):
        # Setup UUID mock
        random_uuid = MagicMock()
        random_uuid.hex = "abcdef1234567890"
        mock_uuid.return_value = random_uuid

        mock_db_connect.return_value = (self.client, self.db)

        # Set up the insert_one mock to return a result
        insert_result = MagicMock()
        insert_result.inserted_id = "mock_id"
        mock_add_order.return_value = insert_result

        result = await create_order(self.valid_event_body)

        self.assertEqual(result["statusCode"], 200)
        response_body = json.loads(result["body"])
        self.assertIn("order_id", response_body)
        self.assertIn("uuid", response_body)
        self.assertEqual(response_body["status"], "Order Created")

        mock_db_connect.assert_called_once()
        mock_add_order.assert_called_once()
        self.assertEqual(
            mock_add_order.call_args[0][0]["CustomerID"],
            "CUST-001"
        )
        self.assertEqual(len(mock_add_order.call_args[0][0]["Items"]), 2)
        self.client.close.assert_called_once()

    @patch("src.despatch.orderCreate.dbConnect", new_callable=AsyncMock)
    @patch("src.despatch.orderCreate.addOrder", new_callable=AsyncMock)
    async def test_create_order_invalid_input(
        self, mock_add_order, mock_db_connect
    ):
        invalid_event_body = {"customer_id": "CUST-001"}

        result = await create_order(invalid_event_body)

        self.assertEqual(result["statusCode"], 400)
        response_body = json.loads(result["body"])
        self.assertIn("error", response_body)
        self.assertIn("missing required fields", response_body["error"])

        mock_db_connect.assert_not_called()
        mock_add_order.assert_not_called()

    @patch("src.despatch.orderCreate.dbConnect", new_callable=AsyncMock)
    @patch("src.despatch.orderCreate.getOrderInfo", new_callable=AsyncMock)
    async def test_validate_order_valid(self, mock_get_order, mock_db_connect):
        mock_db_connect.return_value = (self.client, self.db)

        mock_get_order.return_value = self.sample_order

        result = await validate_order("ORD-12345")

        self.assertEqual(result["statusCode"], 200)
        response_body = json.loads(result["body"])
        self.assertEqual(response_body["order_id"], "ORD-12345")
        self.assertEqual(response_body["validation_status"], "Valid")
        self.assertNotIn("issues", response_body)

        mock_db_connect.assert_called_once()
        mock_get_order.assert_called_once_with("ORD-12345", self.db)
        self.client.close.assert_called_once()

    @patch("src.despatch.orderCreate.dbConnect", new_callable=AsyncMock)
    @patch("src.despatch.orderCreate.getOrderInfo", new_callable=AsyncMock)
    async def test_validate_order_not_found(
        self, mock_get_order, mock_db_connect
    ):
        mock_db_connect.return_value = (self.client, self.db)

        mock_get_order.return_value = None

        result = await validate_order("ORD-NOTFOUND")

        self.assertEqual(result["statusCode"], 404)
        response_body = json.loads(result["body"])
        self.assertIn("error", response_body)
        self.assertEqual(response_body["error"], "Order does not exist")

        mock_db_connect.assert_called_once()
        mock_get_order.assert_called_once_with("ORD-NOTFOUND", self.db)
        self.client.close.assert_called_once()

    @patch("src.despatch.orderCreate.dbConnect", new_callable=AsyncMock)
    @patch("src.despatch.orderCreate.getOrderInfo", new_callable=AsyncMock)
    async def test_get_order_success(self, mock_get_order, mock_db_connect):
        mock_db_connect.return_value = (self.client, self.db)

        mock_get_order.return_value = self.sample_order

        result = await get_order("ORD-12345")

        self.assertEqual(result["statusCode"], 200)
        response_body = json.loads(result["body"])
        self.assertEqual(response_body["order_id"], "ORD-12345")
        self.assertEqual(response_body["customer_id"], "CUST-001")
        self.assertEqual(len(response_body["items"]), 2)

        mock_db_connect.assert_called_once()
        mock_get_order.assert_called_once_with("ORD-12345", self.db)
        self.client.close.assert_called_once()

    @patch("src.despatch.orderCreate.dbConnect", new_callable=AsyncMock)
    @patch("src.despatch.orderCreate.getOrderInfo", new_callable=AsyncMock)
    async def test_check_stock_available(
        self, mock_get_order, mock_db_connect
    ):
        mock_db_connect.return_value = (self.client, self.db)

        test_order = self.sample_order.copy()
        test_order["Items"] = [
            {"item_id": "ITEM-002", "quantity": 50, "price": 10.5},
            {"item_id": "ITEM-001", "quantity": 30, "price": 15.75},
        ]
        mock_get_order.return_value = test_order

        result = await check_stock("ORD-12345")

        self.assertEqual(result["statusCode"], 200)
        response_body = json.loads(result["body"])
        self.assertEqual(response_body["order_id"], "ORD-12345")

        stock_status = response_body["stock_status"]
        self.assertEqual(len(stock_status), 2)

        self.assertEqual(stock_status[0]["item_id"], "ITEM-002")
        self.assertEqual(stock_status[0]["requested_quantity"], 50)
        self.assertEqual(stock_status[0]["available_quantity"], 100)
        self.assertEqual(stock_status[0]["status"], "Available")

        self.assertEqual(stock_status[1]["item_id"], "ITEM-001")
        self.assertEqual(stock_status[1]["requested_quantity"], 30)
        self.assertEqual(stock_status[1]["available_quantity"], 40)
        self.assertEqual(stock_status[1]["status"], "Available")

        mock_db_connect.assert_called_once()
        mock_get_order.assert_called_once_with("ORD-12345", self.db)
        self.client.close.assert_called_once()

    @patch("src.despatch.orderCreate.dbConnect", new_callable=AsyncMock)
    @patch("src.despatch.orderCreate.getOrderInfo", new_callable=AsyncMock)
    async def test_check_stock_insufficient(
        self, mock_get_order, mock_db_connect
    ):
        mock_db_connect.return_value = (self.client, self.db)

        test_order = self.sample_order.copy()
        test_order["Items"] = [
            {"item_id": "ITEM-002", "quantity": 50, "price": 10.5},
            {"item_id": "ITEM-001", "quantity": 60, "price": 15.75},
        ]
        mock_get_order.return_value = test_order

        result = await check_stock("ORD-12345")

        self.assertEqual(result["statusCode"], 200)
        response_body = json.loads(result["body"])
        self.assertEqual(response_body["order_id"], "ORD-12345")

        stock_status = response_body["stock_status"]
        self.assertEqual(len(stock_status), 2)

        self.assertEqual(stock_status[0]["item_id"], "ITEM-002")
        self.assertEqual(stock_status[0]["status"], "Available")

        self.assertEqual(stock_status[1]["item_id"], "ITEM-001")
        self.assertEqual(stock_status[1]["requested_quantity"], 60)
        self.assertEqual(stock_status[1]["available_quantity"], 40)
        self.assertEqual(stock_status[1]["status"], "Insufficient Stock")

        mock_db_connect.assert_called_once()
        mock_get_order.assert_called_once_with("ORD-12345", self.db)
        self.client.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
