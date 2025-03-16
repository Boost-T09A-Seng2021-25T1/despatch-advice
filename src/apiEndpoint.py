import os
import json
from src.mongodb import getOrderInfo, dbConnect
from src.despatch.xmlConversion import xml_to_json
from src.despatch.despatchCreate import create_despatch_advice, validate_despatch_advice
from src.despatch.orderCreate import validate_order_document, create_order
import copy

def endpointFunc(
    xmlDoc: str,
    shipment: dict,
    despatch: dict,
    supplier: dict
):

    if xmlDoc is None or not isinstance(xmlDoc, str):
        raise TypeError("Error: document is invalid.")

    if any(key is None or not isinstance(key, dict) for key in [
            shipment, despatch, supplier
    ]):
        raise TypeError(
            "Error: invalid shipment or despatch information"
        )

    # call Arnav's func here for xml to json

    # assign return, and call arnav's func to save to db

    # call Yousef's func and pass in deliverPeriodReq info

    # call Edward's func and pass in Backordering info

    # call my func to determine if seller == supplier

    """
    Main API endpoint function that coordinates the order and despatch creation process
    
    Args:
        xmlDoc (str): XML string of the order document
        shipment (dict): Information about shipment details
        despatch (dict): Information about despatch details
        sellerIsSupplier (bool): Flag indicating if seller is also supplier
    
    Returns:
        dict: Response containing results of the operations
    """
    if xmlDoc is None or not isinstance(xmlDoc, str):
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Error: document is invalid."})
        }
        
    if not isinstance(shipment, dict) or not isinstance(despatch, dict):
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Error: invalid shipment or despatch information"})
        }
    
    try:
        is_valid, validation_issues, order_json = validate_order_document(xmlDoc, "xml")
        
        if not is_valid:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "Invalid order document",
                    "issues": validation_issues
                })
            }
        
        client, db = dbConnect()
        
        order_create_input = {
            "customer_id": order_json.get("CustomerID"),
            "items": order_json.get("Items", [])
        }
        
        order_result = create_order(order_create_input)
        order_response = json.loads(order_result.get("body", "{}"))
        
        if order_result.get("statusCode") != 200:
            client.close()
            return order_result
        
        # Call Yousef's function to handle delivery period requirements
        delivery_period_result = process_delivery_period(shipment, order_response.get("order_id"))
        
        # Call Edward's function to handle backordering information
        # This will be implemented when available
        backordering_result = process_backordering(despatch, order_response.get("order_id"))
        
        despatch_input = {
            "order_id": order_response.get("order_id"),
            "supplier": {
                "is_seller": sellerIsSupplier,
                # Add any other supplier information from the input
                **({} if not sellerIsSupplier else {"details": despatch.get("supplier_details", {})})
            },
            "customer": {
                # Extract customer info from order or despatch input
                "id": order_json.get("CustomerID"),
                "details": despatch.get("customer_details", {})
            }
        }
        
        despatch_result = create_despatch_advice(despatch_input)
        despatch_response = json.loads(despatch_result.get("body", "{}"))
        
        if despatch_result.get("statusCode") != 200:
            client.close()
            return despatch_result
        
        validation_result = validate_despatch_advice(despatch_response.get("despatch_id"))
        validation_response = json.loads(validation_result.get("body", "{}"))
        
        client.close()
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "order": order_response,
                "despatch": despatch_response,
                "validation": validation_response,
                "delivery_period": delivery_period_result,
                "backordering": backordering_result
            })
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Error processing request: {str(e)}"})
        }

def process_delivery_period(shipment_info, order_id):
    """
    Process delivery period requirements (Yousef's function)
    
    Args:
        shipment_info (dict): Shipment information
        order_id (str): ID of the created order
    
    Returns:
        dict: Result of processing
    """
    # This is a placeholder that will be replaced with actual implementation
    # from Yousef
    return {
        "status": "processed",
        "order_id": order_id,
        "delivery_details": {
            "estimated_arrival": shipment_info.get("estimated_arrival", "Not specified"),
            "shipping_method": shipment_info.get("shipping_method", "Standard")
        }
    }

def process_backordering(despatch_info, order_id):
    """
    Process backordering information (Edward's function)
    
    Args:
        despatch_info (dict): Despatch information
        order_id (str): ID of the created order
    
    Returns:
        dict: Result of processing
    """
    # This is a placeholder that will be replaced with actual implementation
    # from Edward
    return {
        "status": "processed",
        "order_id": order_id,
        "backordering": {
            "allowed": despatch_info.get("allow_backordering", False),
            "max_delay_days": despatch_info.get("max_delay_days", 0)
        }
    }