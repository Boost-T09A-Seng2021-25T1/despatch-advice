from src.apiEndpoint import endpointFunc, get_shipment_qr_code
import asyncio
import json
from src.utils.constants import STATUS_SUCCESS
from src.despatch.despatchCreate import generate_despatch_pdf
from src.despatch.despatchCreate import send_despatch_notification


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
    if '/pdf/' in path and method == 'GET':
        # Extract despatch ID from the path
        path_parts = path.split('/')
        despatch_index = path_parts.index('pdf') + 1
        if despatch_index < len(path_parts):
            despatch_id = path_parts[despatch_index]
            return asyncio.run(generate_despatch_pdf(despatch_id))

    # Handle email notification endpoint
    if path.endswith('/notify') and method == 'POST':
        despatch_id = path_parameters.get('despatchId')

        # Get recipient email from request body if provided
        notification_body = json.loads(event.get('body', '{}'))
        recipient_email = notification_body.get('email')

        if despatch_id:
            return asyncio.run(
                send_despatch_notification(despatch_id, recipient_email)
            )

    # Handle QR code generation endpoint
    if path.endswith('/qrcode') and method == 'GET':
        shipment_id = path_parameters.get('shipmentId')

        # Get additional info from query parameters if provided
        query_params = event.get('queryStringParameters', {}) or {}
        additional_info = {}

        for key, value in query_params.items():
            if key != 'shipmentId':
                additional_info[key] = value

        if shipment_id:
            return asyncio.run(
                get_shipment_qr_code(
                    shipment_id, additional_info if additional_info else None
                )
            )

    # Default behavior - process despatch creation
    body = json.loads(event.get('body', '{}'))

    xmlDoc = body.get("xmlDoc", {})
    shipment = body.get("Shipment", {})
    despatch = body.get("despatch", {})
    supplier = body.get("supplier", {})

    try:
        res = asyncio.run(
            endpointFunc(xmlDoc, shipment, despatch, supplier)
        )

        return {
            "statuscode": STATUS_SUCCESS,
            "body": res
        }

    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps(
                {
                    "error": str(e)
                }
            )
        }
