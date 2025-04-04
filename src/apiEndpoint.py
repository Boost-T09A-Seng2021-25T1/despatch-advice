import json
from src.mongodb import dbConnect
from src.despatch.despatchCreate import (
    create_despatch_advice,
    validate_despatch_advice
)
from src.despatch.orderCreate import (
    validate_order_document,
    create_order
)
from src.despatch.OrderReference import createOrderReference

"""
Main API endpoint function that coordinates the
order and despatch creation process

Args:
    xmlDoc (str): XML string of the order document
    shipment (dict): Information about shipment details
    despatch (dict): Information about despatch details
    supplier (dict): supplier info

Returns:
    dict: Response containing results of the operations
"""


async def endpointFunc(xmlDoc: str, shipment: dict,
                       despatch: dict, supplier: dict):

    if xmlDoc is None or not isinstance(xmlDoc, str):
        raise TypeError("Error: document is invalid.")

    if any(
        key is None or not isinstance(key, dict)
        for key in [shipment, despatch, supplier]
    ):
        raise TypeError("Error: invalid shipment or despatch information")


    try:
        (is_valid, validation_issues,
            order_json) = await validate_order_document(
            xmlDoc, "xml"
        )

        if not is_valid:
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {"error": "Invalid order document",
                     "issues": validation_issues}
                ),
            }

        client, db = await dbConnect()
        try:
            order_create_input = {
                "customer_id": order_json.get("CustomerID"),
                "items": order_json.get("Items", []),
            }

            order_result = await create_order(order_create_input)
            order_response = json.loads(order_result.get("body", "{}"))

            if order_result.get("statusCode") != 200:
                return order_result

            # ============ ORDER REFERENCE =========================
            # res = await db.orders.find_one({"UUID": orderUUID})

            # ======================================================


            # MUST UPDATE SUPPLIER ARGUMENTS AND LOGIC
            # REPLACE WITH DESPATCH LINE
            sellerIsSupplier = supplier.get("is_seller", True)

            # CALL DESPATCH CUSTOMER

            # REPLACE WITH SHIPMENT
            delivery_period_result = process_delivery_period(
                shipment, order_response.get("order_id")
            )

            # REPLACE WITH DESPATCH LINE
            backordering_result = process_backordering(
                despatch, order_response.get("order_id")
            )

            despatch_input = {
                "order_id": order_response.get("order_id"),
                "supplier": {
                    "is_seller": sellerIsSupplier,
                    # Add any other supplier information from the input
                    **(supplier or {}),
                },
                "customer": {
                    # Extract customer info from order or despatch input
                    "id": order_json.get("CustomerID"),
                    "details": despatch.get("customer_details", {}),
                },
            }

            despatch_result = await create_despatch_advice(despatch_input)
            despatch_response = json.loads(despatch_result.get("body", "{}"))

            if despatch_result.get("statusCode") != 200:
                return despatch_result

            validation_result = await validate_despatch_advice(
                despatch_response.get("despatch_id")
            )
            validation_response = json.loads(validation_result.
                                             get("body", "{}"))

            # call create despatch advice to create the initial section of the DA


            return {
            }
        
        finally:
            client.close()

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error":
                                f"Error processing request: {str(e)}"}),
        }


def process_delivery_period(shipment_info, order_id):
    """
    Process delivery period requirements

    Args:
        shipment_info (dict): Shipment information
        order_id (str): ID of the created order

    Returns:
        dict: Result of processing
    """
    # This is a placeholder that will be replaced with actual implementation
    return {
        "status": "processed",
        "order_id": order_id,
        "delivery_details": {
            "estimated_arrival": shipment_info.get(
                "estimated_arrival", "Not specified"
            ),
            "shipping_method": shipment_info.
            get("shipping_method", "Standard"),
        },
    }


def process_backordering(despatch_info, order_id):
    """
    Process backordering information

    Args:
        despatch_info (dict): Despatch information
        order_id (str): ID of the created order

    Returns:
        dict: Result of processing
    """
    # This is a placeholder that will be replaced with actual implementation
    return {
        "status": "processed",
        "order_id": order_id,
        "backordering": {
            "allowed": despatch_info.get("allow_backordering", False),
            "max_delay_days": despatch_info.get("max_delay_days", 0),
        },
    }
