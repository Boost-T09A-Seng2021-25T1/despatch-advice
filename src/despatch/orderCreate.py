import uuid
import datetime
import json
from src.mongodb import addOrder, getOrderInfo, dbConnect
from src.despatch.xmlConversion import xml_to_json


async def validate_order_document(document, format_type="json"):
    validation_issues = []
    converted_document = None
 
    try:
        if format_type.lower() == "xml":
            try:
                converted_document = xml_to_json(document)
            except Exception as e:
                validation_issues.append(f"XML parsing error: {str(e)}")
                return False, validation_issues, None
        else:
            converted_document = document

        required_fields = ["ID", "UUID", "IssueDate"]
        for field in required_fields:
            if field not in converted_document:
                validation_issues.append(f"Missing required field: {field}")

        if "CustomerID" not in converted_document:
            validation_issues.append("Missing CustomerID")

        items = converted_document.get("Items", [])
        if not items:
            validation_issues.append("No items in order")

        for i, item in enumerate(items):
            if not item.get("item_id"):
                validation_issues.append(f"Item {i} missing item_id")
            if not isinstance(item.get("quantity"), (int, float)) or item.get("quantity") <= 0:
                validation_issues.append(f"Item {i} has invalid quantity")
            if not isinstance(item.get("price"), (int, float)) or item.get("price") < 0:
                validation_issues.append(f"Item {i} has invalid price")

        if "CopyIndicator" in converted_document and not isinstance(converted_document["CopyIndicator"], bool):
            validation_issues.append("CopyIndicator must be a boolean value")

        if "DocumentStatusCode" in converted_document and converted_document["DocumentStatusCode"] not in ["NoStatus", "Completed", "Cancelled"]:
            validation_issues.append("Invalid DocumentStatusCode")

        return len(validation_issues) == 0, validation_issues, converted_document

    except Exception as e:
        validation_issues.append(f"Validation error: {str(e)}")
        return False, validation_issues, None

async def create_order(event_body):
    try:
        body = event_body

        if "customer_id" not in body or "items" not in body:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid request format: missing required fields"})
            }

        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        order_uuid = str(uuid.uuid4())

        current_time = datetime.datetime.now().isoformat()
        order_data = {
            "OrderID": order_id,
            "UUID": order_uuid,
            "CustomerID": body["customer_id"],
            "Items": body["items"],
            "Status": "Created",
            "CreationDate": current_time,
            "LastModified": current_time
        }

        client, db = await dbConnect()
        inserted_id = await addOrder(order_data, db)
        client.close()

        if not inserted_id:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "Failed to create order"})
            }

        return {
            "statusCode": 200,
            "body": json.dumps({
                "order_id": order_id,
                "uuid": order_uuid,
                "status": "Order Created"
            })
        }

    except Exception as e:
        print(f"Error creating order: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Server error: {str(e)}"})
        }

async def validate_order(order_id):
    try:
        client, db = await dbConnect()
        order = await getOrderInfo(order_id, db)
        client.close()

        if not order:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Order does not exist"})
            }

        validation_issues = []

        if not order.get("CustomerID"):
            validation_issues.append("Missing customer ID")

        items = order.get("Items", [])
        if not items:
            validation_issues.append("No items in order")

        for i, item in enumerate(items):
            if not item.get("item_id"):
                validation_issues.append(f"Item {i} missing item_id")
            if not isinstance(item.get("quantity"), (int, float)) or item.get("quantity") <= 0:
                validation_issues.append(f"Item {i} has invalid quantity")
            if not isinstance(item.get("price"), (int, float)) or item.get("price") < 0:
                validation_issues.append(f"Item {i} has invalid price")

        if validation_issues:
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "order_id": order.get("OrderID"),
                    "validation_status": "Invalid",
                    "issues": validation_issues
                })
            }
        else:
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "order_id": order.get("OrderID"),
                    "validation_status": "Valid"
                })
            }

    except Exception as e:
        print(f"Error validating order: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Server error: {str(e)}"})
        }

async def get_order(order_id):
    try:
        client, db = await dbConnect()
        order = await getOrderInfo(order_id, db)
        client.close()

        if not order:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Order does not exist"})
            }

        return {
            "statusCode": 200,
            "body": json.dumps({
                "order_id": order.get("OrderID"),
                "customer_id": order.get("CustomerID"),
                "items": order.get("Items")
            })
        }

    except Exception as e:
        print(f"Error retrieving order: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Server error: {str(e)}"})
        }


async def check_stock(order_id):
    try:
        client, db = await dbConnect()
        order = await getOrderInfo(order_id, db)
        client.close()

        if not order:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Order does not exist"})
            }

        items = order.get("Items", [])

        stock_status = []

        for item in items:
            item_id = item.get("item_id")
            requested_quantity = item.get("quantity", 0)

            mock_available = 100 if int(item_id.split("-")[1]) % 2 == 0 else 40

            status = "Available" if mock_available >= requested_quantity else "Insufficient Stock"

            stock_status.append({
                "item_id": item_id,
                "requested_quantity": requested_quantity,
                "available_quantity": mock_available,
                "unit": "pcs",
                "status": status
            })

        return {
            "statusCode": 200,
            "body": json.dumps({
                "order_id": order.get("OrderID"),
                "stock_status": stock_status
            })
        }

    except Exception as e:
        print(f"Error checking stock: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Server error: {str(e)}"})
        }
