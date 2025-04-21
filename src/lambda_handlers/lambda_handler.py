from src.apiEndpoint import endpointFunc, get_shipment_qr_code
import asyncio
import json
from src.utils.constants import STATUS_SUCCESS
# from src.despatch.despatchCreate import generate_despatch_pdf
# from src.despatch.despatchCreate import send_despatch_notificatio
from datetime import datetime

import motor.motor_asyncio

# Trap accidental collection calls
def trap(*args, **kwargs):
    import traceback
    print("🚨 MongoDB collection was called like a function!")
    traceback.print_stack()
    raise RuntimeError("You are calling a MongoDB collection like a function!")

motor.motor_asyncio.AsyncIOMotorCollection.__call__ = trap


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def lambda_handler(event, context):
    """
    Route function that gets called by AWS Gateway
    Params:
        event: dict containing the lambda_func event data
        context: lambda runtime context

    Returns:
        dict containing status message
    """
    # Extract path and method info to determine the endpoint type
    path = event.get('path', '')
    method = event.get('httpMethod', 'POST')

    path_parameters = event.get('pathParameters', {}) or {}

    # Handle PDF generation endpoint
    # if '/pdf/' in path and method == 'GET':
    #     # Extract despatch ID from the path
    #     path_parts = path.split('/')
    #     try:
    #         despatch_index = path_parts.index('pdf') + 1
    #         if despatch_index < len(path_parts):
    #             despatch_id = path_parts[despatch_index]
    #             return asyncio.run(generate_despatch_pdf(despatch_id))
    #     except (ValueError, IndexError):
    #         return {
    #             "statusCode": 400,
    #             "body": json.dumps({"error": "Invalid PDF request: Missing despatch ID"})
    #         }

    # Handle email notification endpoint
    # if path.endswith('/notify') and method == 'POST':
    #     despatch_id = path_parameters.get('despatchId')

    #     # Get recipient email from request body if provided
    #     notification_body = json.loads(event.get('body', '{}'))
    #     recipient_email = notification_body.get('email')

    #     if not despatch_id:
    #         return {
    #             "statusCode": 400,
    #             "body": json.dumps({"error": "Missing despatch ID in request"})
    #         }

    #     return asyncio.run(
    #         send_despatch_notification(despatch_id, recipient_email)
    #     )

    # Handle QR code generation endpoint
    # if path.endswith('/qrcode') and method == 'GET':
    #     shipment_id = path_parameters.get('shipmentId')

    #     # Get additional info from query parameters if provided
    #     query_params = event.get('queryStringParameters', {}) or {}
    #     additional_info = {
    #         k: v for k, v in query_params.items() if k != 'shipmentId'
    #     }

    #     if not shipment_id:
    #         return {
    #             "statusCode": 400,
    #             "body": json.dumps({"error": "Missing shipment ID in request"})
    #         }

    #     return asyncio.run(
    #         get_shipment_qr_code(
    #             shipment_id, additional_info if additional_info else None
    #         )
    #     )

    # Default behavior - process despatch creation
    body = json.loads(event.get('body', '{}'))

    xmlDoc = body.get("xmlDoc", {})
    shipment = body.get("shipment", {})
    despatch = body.get("despatch", {})
    supplier = body.get("supplier", {})

    try:
        res = asyncio.run(
            endpointFunc(xmlDoc, shipment, despatch, supplier)
        )

        return {
            "statuscode": STATUS_SUCCESS,
            "body": json.dumps(res, cls=DateTimeEncoder)
        }

    except TypeError as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Invalid input: {str(e)}"}, cls=DateTimeEncoder)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Internal Server Error: {str(e)}"}, cls=DateTimeEncoder)
        }
