import json
from src.mongodb import dbConnect
from src.despatch.despatchCreate import (
    create_despatch_advice,
    validate_despatch_advice
)
from src.despatch.despatchSupplier import despatchSupplier
from src.despatch.deliveryCustomer import deliveryCustomer
from src.despatch.shipment import create_shipment
from src.despatch.orderCreate import (
    validate_order_document,
    create_order
)
from src.despatch.despatchLine import despatchLine
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
        (
            is_valid,
            validation_issues,
            order_json
        ) = await validate_order_document(xmlDoc, "xml")

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
            uuid = order_response.uuid

            if order_result.get("statusCode") != 200:
                return order_result

            # ============ ORDER REFERENCE =========================
            # Need SalesOrderId to call orderReference
            # db[order_result.order_id]
            order_ref = createOrderReference(
                order_response['order_id'],
                # salesOrderId here,
                client
            )

            # ======================================================


            # MUST UPDATE SUPPLIER ARGUMENTS AND LOGIC (future fix)
            # sellerIsSupplier = supplier.get("is_seller", True)
            supplier = despatchSupplier(uuid)

            # Monique's part
            delivery_customer = deliveryCustomer(uuid)

            # Yousef's part
            # need clarity on shipment id?
            # the return is a dict, need to access the right data
            shipment = create_shipment(shipment_id, shipment).document

            # Edward's part
            # double check this part - currently, the argument
            # check is done inside the function.
            despatch_line = despatchLine(despatch, uuid)

            # must update the function taking in this argument
            # correct sequence of args etc
            despatch_input = {
                "order_id": order_response.get("order_id"),
                "order_ref"
                "supplier": supplier,
                "shipment": shipment,
                "customer": delivery_customer,
                "despatch_line": despatch_line
            }

            # ==============================================

            despatch_result = await create_despatch_advice(despatch_input)
            despatch_response = json.loads(despatch_result.get("body", "{}"))

            if despatch_result.get("statusCode") != 200:
                return despatch_result

            validation_result = await validate_despatch_advice(
                despatch_response.get("despatch_id")
            )
            validation_response = json.loads(validation_result.
                                             get("body", "{}"))


            # ===================================
            # call create despatch advice to create the 
            # initial section of the DA


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
