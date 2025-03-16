# ================================================
# This file will handle sending the final
# despatch line section.

# ================================================
import json
import uuid

# Global in-memory stores (note: these are not persistent across Lambda invocations)
despatch_advice_store = {}
despatch_lines_store = {}

def DespatchLinceCreate(event, context):
    """
    AWS Lambda handler for the PUT /v1/despatch/{despatchId}/createDespatchLine endpoint.
    Expects a JSON body with at least 'delivered_quantity' and, if needed, 'backorder_reason'.
    """
    # Extract despatchId from path parameters
    path_params = event.get("pathParameters", {})
    despatchId = path_params.get("despatchId")
    if not despatchId:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Missing despatchId in path parameters"})
        }
    
    # Check if despatchId exists in the advice store
    if despatchId not in despatch_advice_store:
        return {
            "statusCode": 404,
            "body": json.dumps({"message": "Despatch ID not found"})
        }
    
    # Get and parse the JSON body
    try:
        body = event.get("body")
        if body is None:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Missing JSON data"})
            }
        # API Gateway usually passes the body as a JSON string
        if isinstance(body, str):
            body = json.loads(body)
    except Exception:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Invalid JSON data"})
        }
    
    # Validate delivered_quantity field
    delivered_quantity = body.get("delivered_quantity")
    if delivered_quantity is None:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "delivered_quantity is required"})
        }
    if not isinstance(delivered_quantity, (int, float)) or delivered_quantity < 0:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "delivered_quantity must be a non-negative number"})
        }
    
    # Determine remaining_quantity:
    # If there are existing lines, sum their backorder_quantity;
    # otherwise, assume the total order quantity is stored in despatch_advice_store.
    if despatchId in despatch_lines_store and despatch_lines_store[despatchId]:
        remaining_quantity = sum(line["backorder_quantity"] for line in despatch_lines_store[despatchId])
    else:
        # In the original code, the entire order quantity is stored in despatch_advice_store[despatchId]
        remaining_quantity = despatch_advice_store[despatchId]
    
    # Calculate backorder quantity
    backorder_quantity = remaining_quantity - delivered_quantity
    if backorder_quantity < 0:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Delivered quantity exceeds order quantity"})
        }
    
    # If there's a backorder, require a reason
    backorder_reason = None
    if backorder_quantity > 0:
        backorder_reason = body.get("backorder_reason")
        if not backorder_reason:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Backorder reason is required when backorder quantity is positive"})
            }
    
    # Build the new despatch line record
    new_line = {
        "line_id": str(uuid.uuid4()),
        "status": "Revised" if backorder_quantity > 0 else "Completed",
        "delivered_quantity": delivered_quantity,
        "backorder_quantity": backorder_quantity,
        "backorder_reason": backorder_reason
    }
    
    # Add the new line to the store
    if despatchId not in despatch_lines_store:
        despatch_lines_store[despatchId] = []
    despatch_lines_store[despatchId].append(new_line)
    
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Despatch line created successfully"})
    }
