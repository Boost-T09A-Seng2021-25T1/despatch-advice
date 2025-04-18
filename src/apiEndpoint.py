import json
from src.mongodb import dbConnect, getOrderInfo
from src.despatch.despatchCreate import (
    create_despatch_advice,
    validate_despatch_advice
)
from src.despatch.orderCreate import (
    validate_order_document,
    create_order
)
from src.despatch.xmlConversion import json_to_xml
from src.despatch.despatchSupplier import despatchSupplier
from src.despatch.deliveryCustomer import deliveryCustomer
from src.despatch.OrderReference import create_order_reference
from src.despatch.despatchLine import despatchLine
from src.despatch.shipment import create_shipment


async def endpointFunc(
    xmlDoc: str,
    shipment: dict,
    despatch: dict,
    supplier: dict
):
    """
    Main API endpoint function that coordinates the
    order and despatch creation process

    Args:
        xmlDoc (str): XML string of the order document
        shipment (dict): Information about shipment details
        despatch (dict): Information about despatch details
        supplier (dict): Information about supplier details

    Returns:
        dict: Response containing results of the operations
    """
    # Input validation
    if xmlDoc is None or not isinstance(xmlDoc, str):
        raise TypeError("Error: document is invalid.")

    if any(
        key is None or not isinstance(key, dict)
        for key in [shipment, despatch, supplier]
    ):
        raise TypeError("Error: invalid shipment or despatch information")

    try:
        # 1. Validate the XML order document and convert to JSON
        (
            is_valid,
            validation_issues,
            order_json
        ) = await validate_order_document(
            xmlDoc, "xml"
        )

        if not is_valid:
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {
                        "error": "Invalid order document",
                        "issues": validation_issues
                    }
                ),
            }

        # 2. Connect to the database
        client, db = await dbConnect()
        try:
            # 3. Create an order from the validated document
            order_create_input = {
                "customer_id": order_json.get("CustomerID"),
                "items": order_json.get("Items", []),
            }

            order_result = await create_order(order_create_input)
            order_response = json.loads(order_result.get("body", "{}"))

            if order_result.get("statusCode") != 200:
                return order_result

            # Get the order ID and UUID for subsequent operations
            order_id = order_response.get("order_id")
            order_uuid = order_response.get("uuid")
            order = await getOrderInfo(order_id, db)
            salesOrderId = order.get('SalesOrderId', "")

            # 4. Create order reference
            order_ref = await create_order_reference(
                order_id,
                salesOrderId,
                db
            )

            # 5. Get supplier information
            supplier_info = {}
            try:
                supplier_info = await despatchSupplier(order_uuid)
            except ValueError as e:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": f"Supplier error: {str(e)}"}),
                }

            # 6. Get customer information for delivery
            customer_info = {}
            try:
                if order_uuid:
                    customer_info = await deliveryCustomer(order_uuid)
            except ValueError as e:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": f"Customer error: {str(e)}"}),
                }

            # 7. Handle delivery period requirements
            delivery_period_result = process_delivery_period(
                shipment, order_id
            )

            # 8. Process shipment data if provided
            shipment_result = {}
            if 'ID' in shipment:
                try:
                    # Use a valid shipment ID format (SHIP-XXXXXX)
                    shipment_id = shipment.get('ID', f"SHIP-{order_id[4:]}")
                    if not shipment_id.startswith("SHIP-"):
                        shipment_id = f"SHIP-{shipment_id[-6:]}"

                    shipment_result = await create_shipment(
                        shipment_id, shipment
                    )
                    if not shipment_result.get("success"):
                        return {
                            "statusCode": 400,
                            "body": json.dumps({
                                "error": f"Shipment error: {
                                    shipment_result.get(
                                        'error', 'Unknown error'
                                    )
                                }"
                            }),
                        }
                except ValueError as e:
                    return {
                        "statusCode": 400,
                        "body": json.dumps({
                            "error": f"Shipment error: {str(e)}"
                        }),
                    }

            # 9. Process backordering information
            backordering_result = process_backordering(
                despatch, order_id
            )

            # 10. Prepare despatch line if details provided
            despatch_line_result = {}
            if despatch.get('line_details'):
                try:
                    line_details = despatch.get('line_details', {})
                    line_details.setdefault('ID', '1')
                    line_details.setdefault('Note', 'Generated by system')
                    line_details.setdefault('BackOrderReason', 'N/A')
                    line_details.setdefault('LotNumber', '100001')
                    line_details.setdefault('ExpiryDate', '2025-12-31')

                    if not line_details.get('DeliveredQuantity'):
                        # Default to full delivery if not specified
                        items = order_json.get("Items", [])
                        if items:
                            line_details[
                                'DeliveredQuantity'
                            ] = items[0].get('quantity', 0)

                    if not line_details.get('BackOrderQuantity'):
                        line_details['BackOrderQuantity'] = 0

                    despatch_line_result = despatchLine(
                        line_details,
                        order_uuid
                    )
                except ValueError as e:
                    return {
                        "statusCode": 400,
                        "body": json.dumps({
                            "error": f"Despatch line error: {str(e)}"
                        }),
                    }

            # 11. Create the despatch advice with ALL collected data
            despatch_input = {
                "order_id": order_id,
                "order_reference": order_ref,
                "supplier": supplier_info,
                "customer": {
                    "id": order_json.get("CustomerID"),
                    "details": customer_info
                },
                "shipment": shipment_result,
                "despatch_line": despatch_line_result,
                "backordering": backordering_result,
                "delivery_period": delivery_period_result
            }

            # Call the fixed create_despatch_advice function
            despatch_result = await create_despatch_advice(despatch_input)
            despatch_response = json.loads(despatch_result.get("body", "{}"))

            if despatch_result.get("statusCode") != 200:
                return despatch_result

            # 12. Validate the created despatch advice
            validation_result = await validate_despatch_advice(
                despatch_response.get("despatch_id")
            )
            validation_response = json.loads(
                validation_result.get("body", "{}")
            )

            # 13. Convert despatch data to XML
            despatch_data = despatch_response.get("despatch_data", {})
            if not despatch_data:
                # Fallback if despatch_data is not available
                complete_despatch_json = {
                    "ID": despatch_response.get("despatch_id", ""),
                    "OrderReference": order_ref,
                    "DespatchSupplierParty": supplier_info,
                    "DeliveryCustomerParty": customer_info,
                    "Shipment": shipment_result.get("document", {}),
                    "DespatchLine": despatch_line_result.get(
                        "DespatchLine", {}
                    )
                }
                despatch_xml = json_to_xml(
                    complete_despatch_json, "DespatchAdvice"
                )
            else:
                # Use the despatch_data directly if available
                despatch_xml = json_to_xml(despatch_data, "DespatchAdvice")

            # 14. Return the complete response with XML content
            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "order": order_response,
                        "despatch": despatch_response,
                        "despatch_xml": despatch_xml,  # Add the XML string
                        "validation": validation_response,
                        "delivery_period": delivery_period_result,
                        "backordering": backordering_result,
                        "shipment": shipment_result,
                        "despatch_line": despatch_line_result
                    }
                ),
            }
        finally:
            client.close()

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": f"Error processing request: {str(e)}"
            }),
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
    # Extract delivery period data from shipment info
    delivery_period = shipment_info.get(
        'Delivery',
        {}
    ).get('RequestedDeliveryPeriod', {})

    # Process delivery date information
    start_date = delivery_period.get('StartDate', 'Not specified')
    start_time = delivery_period.get('StartTime', 'Not specified')
    end_date = delivery_period.get('EndDate', start_date)
    end_time = delivery_period.get('EndTime', 'Not specified')

    # Calculate estimated delivery based on available information
    if start_date != 'Not specified':
        if end_date != 'Not specified' and end_date != start_date:
            delivery_window = f"{start_date} to {end_date}"
        else:
            delivery_window = start_date

        if start_time != 'Not specified' and end_time != 'Not specified':
            delivery_window += f" (between {start_time} and {end_time})"
        elif start_time != 'Not specified':
            delivery_window += f" at {start_time}"
    else:
        delivery_window = "Not specified"

    # Get shipping method from shipment info if available
    shipping_method = shipment_info.get('shipping_method', 'Standard')

    # Create and return delivery period processing result
    return {
        "status": "processed",
        "order_id": order_id,
        "delivery_details": {
            "estimated_arrival": delivery_window,
            "shipping_method": shipping_method,
            "delivery_period": {
                "start_date": start_date,
                "start_time": start_time,
                "end_date": end_date,
                "end_time": end_time
            }
        }
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
    # Extract backordering configuration values with defaults
    allow_backordering = despatch_info.get("allow_backordering", False)
    max_delay_days = despatch_info.get("max_delay_days", 0)

    # Extract line-specific backordering information if available
    line_details = despatch_info.get("line_details", {})

    backorder_items = []
    if line_details:
        backorder_qty = line_details.get("BackOrderQuantity", 0)
        if backorder_qty > 0:
            backorder_items.append({
                "line_id": line_details.get("ID", "1"),
                "quantity": backorder_qty,
                "reason": line_details.get(
                    "BackOrderReason",
                    "Insufficient stock"
                )
            })

    # Additional backordering configuration
    notification_config = {
        "notify_customer": despatch_info.get(
            "notify_customer_backorder",
            True
        ),
        "notification_method": despatch_info.get(
            "notification_method",
            "email"
        )
    }

    # Create and return backordering processing result
    return {
        "status": "processed",
        "order_id": order_id,
        "backordering": {
            "allowed": allow_backordering,
            "max_delay_days": max_delay_days,
            "backorder_items": backorder_items,
            "notification_config": notification_config
        }
    }


async def get_shipment_qr_code(shipment_id, additional_info=None):
    """

    Get QR code for a shipment

    Args:
        shipment_id (str): ID of the shipment
        additional_info (dict, optional): Additional info to include in QR code
        
    Returns:
        dict: Response with QR code data
    """
    from src.despatch.shipment import generate_shipment_qr_code
    
    try:
        result = await generate_shipment_qr_code(shipment_id, additional_info)
        
        if result.get("success"):
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "shipment_id": result.get("shipment_id"),
                    "qr_code": result.get("qr_code"),
                    "data": result.get("qr_data")
                })
            }
        else:
            return {
                "statusCode": 404 if "not found" in result.get("error", "") else 500,
                "body": json.dumps({"error": result.get("error")})
            }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Error generating QR code: {str(e)}"})
        }