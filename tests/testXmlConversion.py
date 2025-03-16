import unittest
import os
import sys
import json
from unittest.mock import patch, MagicMock

dirPath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(dirPath)

from src.despatch.xmlConversion import xml_to_json, json_to_xml


class TestXMLConversion(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        # Sample XML documents
        self.sample_order_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <Order xmlns="urn:oasis:names:specification:ubl:schema:xsd:Order-2"
               xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
               xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
            <cbc:ID>ORD-12345</cbc:ID>
            <cbc:UUID>550e8400-e29b-41d4-a716-446655440000</cbc:UUID>
            <cbc:IssueDate>2025-03-15</cbc:IssueDate>
            <cbc:BuyerReference>CUST-001</cbc:BuyerReference>
            <cbc:CopyIndicator>true</cbc:CopyIndicator>
            <cbc:DocumentStatusCode>NoStatus</cbc:DocumentStatusCode>
            <cbc:Note>Test Order</cbc:Note>
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
            <cac:OrderLine>
                <cac:LineItem>
                    <cbc:Quantity>3</cbc:Quantity>
                    <cac:Item>
                        <cac:SellersItemIdentification>
                            <cbc:ID>ITEM-002</cbc:ID>
                        </cac:SellersItemIdentification>
                    </cac:Item>
                    <cac:Price>
                        <cbc:PriceAmount>15.75</cbc:PriceAmount>
                    </cac:Price>
                </cac:LineItem>
            </cac:OrderLine>
        </Order>"""

        self.sample_despatch_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <DespatchAdvice xmlns="urn:oasis:names:specification:ubl:schema:xsd:DespatchAdvice-2"
                xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
                xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
            <cbc:ID>D-12345</cbc:ID>
            <cbc:UUID>660e8400-e29b-41d4-a716-446655440001</cbc:UUID>
            <cbc:IssueDate>2025-03-16</cbc:IssueDate>
            <cbc:CopyIndicator>false</cbc:CopyIndicator>
            <cbc:DocumentStatusCode>NoStatus</cbc:DocumentStatusCode>
            <cbc:DespatchAdviceTypeCode>delivery</cbc:DespatchAdviceTypeCode>
            <cbc:Note>Test Despatch</cbc:Note>
        </DespatchAdvice>"""

        # Sample JSON objects
        self.sample_order_json = {
            "ID": "ORD-12345",
            "UUID": "550e8400-e29b-41d4-a716-446655440000",
            "IssueDate": "2025-03-15",
            "CustomerID": "CUST-001",
            "CopyIndicator": True,
            "DocumentStatusCode": "NoStatus",
            "Note": "Test Order",
            "Items": [
                {"item_id": "ITEM-001", "quantity": 5.0, "price": 10.5},
                {"item_id": "ITEM-002", "quantity": 3.0, "price": 15.75},
            ],
        }

        self.sample_despatch_json = {
            "ID": "D-12345",
            "UUID": "660e8400-e29b-41d4-a716-446655440001",
            "IssueDate": "2025-03-16",
            "CopyIndicator": False,
            "DocumentStatusCode": "NoStatus",
            "Note": "Test Despatch",
        }

    @patch(
        "src.xmlConversion.cbcSchema",
        "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    )
    @patch(
        "src.xmlConversion.cacSchema",
        "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    )
    def test_xml_to_json_order(self):
        """Test conversion of Order XML to JSON"""
        # Convert XML to JSON
        result = xml_to_json(self.sample_order_xml)

        # Check essential fields
        self.assertEqual(result["ID"], "ORD-12345")
        self.assertEqual(result["UUID"], "550e8400-e29b-41d4-a716-446655440000")
        self.assertEqual(result["IssueDate"], "2025-03-15")
        self.assertEqual(result["CustomerID"], "CUST-001")
        self.assertTrue(result["CopyIndicator"])
        self.assertEqual(result["DocumentStatusCode"], "NoStatus")
        self.assertEqual(result["Note"], "Test Order")

        # Check items array
        self.assertEqual(len(result["Items"]), 2)
        self.assertEqual(result["Items"][0]["item_id"], "ITEM-001")
        self.assertEqual(result["Items"][0]["quantity"], 5.0)
        self.assertEqual(result["Items"][0]["price"], 10.5)
        self.assertEqual(result["Items"][1]["item_id"], "ITEM-002")
        self.assertEqual(result["Items"][1]["quantity"], 3.0)
        self.assertEqual(result["Items"][1]["price"], 15.75)

    @patch(
        "src.xmlConversion.cbcSchema",
        "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    )
    @patch(
        "src.xmlConversion.cacSchema",
        "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    )
    def test_xml_to_json_despatch(self):
        """Test conversion of DespatchAdvice XML to JSON"""
        # Convert XML to JSON
        result = xml_to_json(self.sample_despatch_xml)

        # Check essential fields
        self.assertEqual(result["ID"], "D-12345")
        self.assertEqual(result["UUID"], "660e8400-e29b-41d4-a716-446655440001")
        self.assertEqual(result["IssueDate"], "2025-03-16")
        self.assertFalse(result["CopyIndicator"])
        self.assertEqual(result["DocumentStatusCode"], "NoStatus")
        self.assertEqual(result["Note"], "Test Despatch")

        # Check that Items array exists but is empty (no OrderLine in despatch XML)
        self.assertEqual(result["Items"], [])

    @patch(
        "src.xmlConversion.cbcSchema",
        "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    )
    @patch(
        "src.xmlConversion.cacSchema",
        "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    )
    def test_xml_to_json_invalid_input(self):
        """Test handling of invalid XML input"""
        # Test with invalid XML
        invalid_xml = "<Invalid XML>"
        with self.assertRaises(ValueError):
            xml_to_json(invalid_xml)

        # Test with empty string
        with self.assertRaises(ValueError):
            xml_to_json("")

        # Test with None
        with self.assertRaises(ValueError):
            xml_to_json(None)

    def test_json_to_xml_order(self):
        """Test conversion of JSON to Order XML"""
        # Convert JSON to XML
        result = json_to_xml(self.sample_order_json, "Order")

        # Check that result is a string
        self.assertIsInstance(result, str)

        # Check that essential elements are in the XML
        self.assertIn("<cbc:ID>ORD-12345</cbc:ID>", result)
        self.assertIn(
            "<cbc:UUID>550e8400-e29b-41d4-a716-446655440000</cbc:UUID>", result
        )
        self.assertIn("<cbc:IssueDate>2025-03-15</cbc:IssueDate>", result)
        self.assertIn("<cbc:CopyIndicator>true</cbc:CopyIndicator>", result)
        self.assertIn("<cbc:Note>Test Order</cbc:Note>", result)

    def test_json_to_xml_despatch(self):
        """Test conversion of JSON to DespatchAdvice XML"""
        # Convert JSON to XML
        result = json_to_xml(self.sample_despatch_json, "DespatchAdvice")

        # Check that result is a string
        self.assertIsInstance(result, str)

        # Check that essential elements are in the XML
        self.assertIn("<cbc:ID>D-12345</cbc:ID>", result)
        self.assertIn(
            "<cbc:UUID>660e8400-e29b-41d4-a716-446655440001</cbc:UUID>", result
        )
        self.assertIn("<cbc:IssueDate>2025-03-16</cbc:IssueDate>", result)
        self.assertIn("<cbc:CopyIndicator>false</cbc:CopyIndicator>", result)
        self.assertIn("<cbc:Note>Test Despatch</cbc:Note>", result)
        self.assertIn(
            "<cbc:DespatchAdviceTypeCode>delivery</cbc:DespatchAdviceTypeCode>", result
        )

    def test_json_to_xml_invalid_document_type(self):
        """Test handling of invalid document type"""
        # Test with unsupported document type
        with self.assertRaises(ValueError):
            json_to_xml(self.sample_order_json, "InvalidType")


if __name__ == "__main__":
    unittest.main()
