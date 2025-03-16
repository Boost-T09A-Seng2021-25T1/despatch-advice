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
    os.path.join(os.path.dirname(__file__), "..", "..")
))


def despatchLine(despatchLine: dict, UUID: str):
    if despatchLine is None:
        raise ValueError("Error: insufficient information entered.")

    neededKeys = [
        "DeliveredQuantity",
        "BackOrderQuantity",
        "ID",
        "Note",
        "BackOrderReason",
        "LotNumber",
        "ExpiryDate"
    ]

    for key in neededKeys:
        if key not in despatchLine:
            raise ValueError("Error: insufficient information entered.")

    deliveredAmount = backOrderAmount = lotnum = 0
    iD = note = backOrderReason = date = ""

    try:
        # type validations
        deliveredAmount = int(despatchLine["DeliveredQuantity"])
        backOrderAmount = int(despatchLine["BackOrderQuantity"])
        lotNum = int(despatchLine["LotNumber"])
        iD = str(despatchLine["ID"])
        date = datetime.strptime(
			str(despatchLine["ExpiryDate"]),
			"%Y-%m-%d"
		)
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
	
    mongoClient, db = asyncio.run(dbConnect())
    orders = db["orders"]

    data = asyncio.run(getOrderInfo(UUID, orders))
    error = "Error: could not retrieve despatch supplier information."
    if not data:
        mongoClient.close()
        raise ValueError(error)
    
    item = data["OrderLine"]["LineItem"]["Item"]

    return {
        "DespatchLine": {
			"ID": iD,
			"Note": note,
			# another future fix here.add linestatuscode to body args
			"LineStatusCode": "NoStatus",
			# another future fix here - add metric to body args
			# metric is missing "="KGM""
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
                }
            }
        }
    }
