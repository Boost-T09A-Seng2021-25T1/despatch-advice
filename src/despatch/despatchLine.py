import os
import sys
from datetime import datetime
from src.mongodb import dbConnect, getOrderInfo
import asyncio


# ================================================
# This file will handle sending the final
# despatch line section.
# ================================================

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")))


def despatchLine(despatchLine: dict, UUID: str):
    """
    Create a despatch line object with validation.

    Args:
        despatchLine (dict): Dictionary containing despatch line information
        UUID (str): UUID of the corresponding order

    Returns:
        dict: Formatted despatch line object

    Raises:
        ValueError: If required information is missing or invalid
    """
    if despatchLine is None:
        raise ValueError("Error: insufficient information entered.")

    neededKeys = [
        "DeliveredQuantity",
        "BackOrderQuantity",
        "ID",
        "Note",
        "BackOrderReason",
        "LotNumber",
        "ExpiryDate",
    ]

    for key in neededKeys:
        if key not in despatchLine:
            raise ValueError("Error: insufficient information entered.")

    deliveredAmount = backOrderAmount = 0
    iD = note = backOrderReason = date = ""
    lotNum = 0

    try:
        # type validations
        deliveredAmount = int(float(despatchLine["DeliveredQuantity"]))
        backOrderAmount = int(float(despatchLine["BackOrderQuantity"]))

        # Handle LotNumber that might be a string with non-numeric characters
        if isinstance(despatchLine["LotNumber"], str):
            # Extract only digits if the string contains non-numeric characters
            digits = "".join(filter(str.isdigit, despatchLine["LotNumber"]))
            if digits:
                lotNum = int(digits)
            else:
                raise ValueError("Invalid lot number format")
        else:
            lotNum = int(despatchLine["LotNumber"])

        iD = str(despatchLine["ID"])
        date = datetime.strptime(str(despatchLine["ExpiryDate"]), "%Y-%m-%d")
        note = str(despatchLine["Note"])
        backOrderReason = str(despatchLine["BackOrderReason"])
    except (ValueError, TypeError):
        # future fix here - change the string or refactor code
        raise ValueError("Please re-enter an amount for quantity.")

    # recursive call to apiEndpoint to restart the despatch creation
    # with the backorder amounts
    # if backOrderAmount > 0:
    # future issue to be fixed - this will require another
    # user arg/input for updated delivery date instead of recursion

    try:
        mongoClient, db = asyncio.run(dbConnect())
        orders = db["orders"]

        data = asyncio.run(getOrderInfo(UUID, orders))
        error = "Error: could not retrieve despatch supplier information."
        if not data:
            raise ValueError(error)
    except Exception as e:
        raise ValueError(f"Database error: {str(e)}")
    finally:
        if "mongoClient" in locals():
            mongoClient.close()

    item = data["OrderLine"]["LineItem"]["Item"]

    return {
        "DespatchLine": {
            "ID": iD,
            "Note": note,
            # another future fix here.add linestatuscode to body args
            "LineStatusCode": "NoStatus",
            # another future fix here - add metric to body args
            # metric is missing "=KGM"
            "DeliveredQuantity unitCode": deliveredAmount,
            "BackOrderQuantity unitCode": backOrderAmount,
            "BackOrderReason": backOrderReason,
            "OrderLineReference": {
                # another fix needed here
                "LineID": 1,
                # Another fix/issue
                "SalesOrderLineID": "A",
                "OrderReference": {
                    "ID": data["ID"],
                    "SalesOrderID": data["SalesOrderID"],
                    "UUID": data["UUID"],
                    "IssueDate": data["IssueDate"],
                },
            },
            "Item": {
                "Description": item["Description"],
                "Name": item["Name"],
                "BuyersItemIdentification": {
                    "ID": item["BuyersItemIdentification"]["ID"],
                },
                "SellersItemIdentification": {
                    "ID": item["SellersItemIdentification"]["ID"],
                },
                "ItemInstance": {
                    "LotIdentification": {
                        "LotNumberID": lotNum,
                        "ExpiryDate": date,
                    }
                },
            },
        }
    }
