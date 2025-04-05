from src.apiEndpoint import endpointFunc
import asyncio
import json
from src.utils.constants import STATUS_SUCCESS


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
                    "error": {e}
                }
            )
        }
