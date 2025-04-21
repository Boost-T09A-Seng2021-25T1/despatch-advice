import json
import sys
import os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from src.lambda_handlers.lambda_handler import lambda_handler

# Mock event for POST /v2/despatch
test_event = {
    "httpMethod": "POST",
    "path": "/v2/despatch",
    "headers": {
        "Content-Type": "application/json"
    },
    "body": json.dumps({
        "xmlDoc": """
        <Order xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
            xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
        <cbc:ID>ORD-123</cbc:ID>
        <cbc:UUID>abb20017-7379-43e7-baf0-dc6923a9e8e2</cbc:UUID>
        <cbc:IssueDate>2023-01-01</cbc:IssueDate>
        <cbc:BuyerReference>CUST-1</cbc:BuyerReference>
        <cac:OrderLine>
            <cac:LineItem>
            <cbc:Quantity>2</cbc:Quantity>
            <cac:Item>
                <cac:SellersItemIdentification>
                <cbc:ID>ITEM-001</cbc:ID>
                </cac:SellersItemIdentification>
            </cac:Item>
            <cac:Price>
                <cbc:PriceAmount>10</cbc:PriceAmount>
            </cac:Price>
            </cac:LineItem>
        </cac:OrderLine>
        </Order>
        """,

        "Shipment": {"ID": "SHIP-001"},
        "despatch": {
            "line_details": {
                "DeliveredQuantity": 2,
                "BackOrderQuantity": 0
            }
        },
        "supplier": {}
    }),
    "pathParameters": {},
    "queryStringParameters": {}
}

def main():
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()