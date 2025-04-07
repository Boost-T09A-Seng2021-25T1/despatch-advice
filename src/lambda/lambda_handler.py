from src.apiEndpoint import endpointFunc
import json


# def endpointHelper():
#     res = endpointFunc()

#     # if
#     return {
#         "statusCode": 400,
#         "body": json.dumps({"error": "Error: document is invalid."}),
#     }

#    if not isinstance(shipment, dict) or not isinstance(despatch, dict):
#         return {
#             "statusCode": 400,
#             "body": json.dumps(
#                 {"error": "Error: invalid shipment or despatch information"}
#             ),
#         }

def lambda_handler(event, context):
    """
    Route function that gets called by AWS Gateway
    Params:
        event: dict containing the lambda_func event data
        context: lambda runtime context

    Returns:
        dict containing status message
    """
    body = json.loads(event['body'])

    xmlDoc = body.get("xmlDoc", {})
    shipment = body.get("Shipment", {})
    despatch = body.get("despatch", {})
    supplier = body.get("supplier", {})

    try:
        endpointFunc(xmlDoc, shipment, despatch, supplier)

    except TypeError as e:
        return {
            "statusCode": 400,
            "body": json.dumps(
                {
                    "error": {e}
                }
            )
        }
