import os
from src.mongodb import dbConnect
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

    data = await orders.find_one(
        {"UUID": UUID}) or await orders.find_one({"OrderID": UUID}
    )
    error = "Error: could not retrieve despatch supplier information."
    if not data:
        mongoClient.close()
        raise ValueError(error)

    # assumes that seller = despatch. Logic to be added
    # Recursive O(n) copy
    print("MongoDB Document:", data)
    seller_info = data.get("SellerSupplierParty")


    seller_info = data.get("SellerSupplierParty")
    if not seller_info:
        mongoClient.close()
        raise ValueError("Missing SellerSupplierParty in order document.")

    DespatchSupplierParty = copy.deepcopy(seller_info)

    mongoClient.close()
    return DespatchSupplierParty
