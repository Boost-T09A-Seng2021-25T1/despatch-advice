# ================================================
# This file will handle sending the final
# despatch line section.

# ================================================
from flask import Flask, request, jsonify
import uuid
import os
import sys

app = Flask(__name__)

despatch_advice_store = {}
despatch_lines_store = {}

@app.route("/v1/despatch/<string:despatchId>/createDespatchLine", methods=["PUT"])
def create_despatch_line(despatchId):
    if despatchId not in despatch_advice_store:
        return jsonify({"message": "Despatch ID not found"}), 404
        
    data = request.get_json()
    if not data:
        return jsonify({"message": "Missing JSON data"}), 400
    
    delivered_quantity = data.get("delivered_quantity")
    if delivered_quantity is None:
        return jsonify({"message": "delivered_quantity is required"}), 400
    
    if not isinstance(delivered_quantity, (int, float)) or delivered_quantity < 0:
        return jsonify({"message": "delivered_quantity must be a non-negative number"}), 400
    
    remaining_quantity = sum(line["backorder_quantity"] for line in despatch_lines_store.get(despatchId, [])) \
        if despatch_lines_store.get(despatchId) else despatch_advice_store[despatchId]
    
    backorder_quantity = remaining_quantity - delivered_quantity
    if backorder_quantity < 0:
        return jsonify({"message": "Delivered quantity exceeds order quantity"}), 400
    
    backorder_reason = None
    if backorder_quantity > 0:
        backorder_reason = data.get("backorder_reason")
        if not backorder_reason:
            return jsonify({"message": "Backorder reason is required when backorder quantity is positive"}), 400
    
    new_line = {
        "line_id": str(uuid.uuid4()),
        "status": "Revised" if backorder_quantity > 0 else "Completed",
        "delivered_quantity": delivered_quantity,
        "backorder_quantity": backorder_quantity,
        "backorder_reason": backorder_reason
    }
    
    if despatchId not in despatch_lines_store:
        despatch_lines_store[despatchId] = []
    despatch_lines_store[despatchId].append(new_line)
    
    return jsonify({"message": "Despatch line created successfully"}), 200

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
))