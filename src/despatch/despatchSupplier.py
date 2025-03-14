import os
from src.mongodb import getOrderInfo, dbConnect
import copy


dirPath = os.path.abspath(os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..")))


# ==================================
# Purpose

# Arguments

# Returns
# ==================================


async def despatchSupplier(UUID: str):
    mongoClient, db = await dbConnect()
    orders = db["orders"]

    data = await getOrderInfo(UUID, orders)
    error = "Error: could not retrieve despatch supplier information."
    if not data:
        mongoClient.close()
        raise ValueError(error)

    # assumes that seller = despatch. Logic to be added
    # Recursive O(n) copy
    DespatchSupplierParty = copy.deepcopy(data["SellerSupplierParty"])

    mongoClient.close()
    return DespatchSupplierParty
