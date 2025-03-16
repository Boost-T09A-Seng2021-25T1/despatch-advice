import os
from src.mongodb import getOrderInfo, dbConnect
import copy

dirPath = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

async def deliveryCustomer(despatchID):
    mongoClient, db = await dbConnect()
    orders = db["orders"]

    data = await getOrderInfo(despatchID, orders)
    error = "Error: could not retrieve despatch supplier information."
    if not data:
        mongoClient.close()
        raise ValueError(error)

    OrderInformation = {
        "CustomerAssignedAccountID": "",  # Fixed key naming
        "SupplierAssignedAccountID": "",  # Fixed key naming
        "Party": {
            "PartyName": "",  # Fixed assignment location
            "PostalAddress": {
                "StreetName": "",
                "BuildingName": "",
                "BuildingNumber": "",
                "CityName": "",
                "PostalZone": "",
                "CountrySubentity": "",
                "AddressLine": {
                    "Line": ""  # Fixed AddressLine structure
                },
                "Country": {
                    "IdentificationCode": ""
                },
            },
            "PartyTaxScheme": {
                "RegistrationName": "",
                "CompanyID": "",
                "ExemptionReason": "",
                "TaxScheme": {
                    "ID": "",
                    "TaxTypeCode": ""
                },
            },
            "Contact": {
                "Name": "",
                "Telephone": "",
                "Telefax": "",
                "ElectronicMail": ""
            }
        }
    }

    try:
        result = await orders.find_one(
            {"_id.ID": despatchID},
            {"DeliveryCustomerParty": 1, "_id": 0}
        )

        if result and "DeliveryCustomerParty" in result:
            delivery_party = result["DeliveryCustomerParty"]

            OrderInformation["CustomerAssignedAccountID"] = delivery_party.get("CustomerAssignedAccountID", "")
            OrderInformation["SupplierAssignedAccountID"] = delivery_party.get("SupplierAssignedAccountID", "")

            if "Party" in delivery_party:
                party = delivery_party["Party"]
                OrderInformation["Party"]["PartyName"] = party.get("PartyName", "")

                if "PostalAddress" in party:
                    postal = party["PostalAddress"]
                    for key in OrderInformation["Party"]["PostalAddress"]:
                        if key == "Country":
                            OrderInformation["Party"]["PostalAddress"]["Country"]["IdentificationCode"] = postal.get("Country", {}).get("IdentificationCode", "")
                        elif key == "AddressLine":
                            OrderInformation["Party"]["PostalAddress"]["AddressLine"]["Line"] = postal.get("AddressLine", {}).get("Line", "")  # Fixed AddressLine
                        else:
                            OrderInformation["Party"]["PostalAddress"][key] = postal.get(key, "")

                if "PartyTaxScheme" in party:
                    tax_scheme = party["PartyTaxScheme"]
                    for key in OrderInformation["Party"]["PartyTaxScheme"]:
                        if key == "TaxScheme":
                            ts = tax_scheme.get("TaxScheme", {})
                            OrderInformation["Party"]["PartyTaxScheme"]["TaxScheme"]["ID"] = ts.get("ID", "")
                            OrderInformation["Party"]["PartyTaxScheme"]["TaxScheme"]["TaxTypeCode"] = ts.get("TaxTypeCode", "")
                        else:
                            OrderInformation["Party"]["PartyTaxScheme"][key] = tax_scheme.get(key, "")

                if "Contact" in party:
                    contact = party["Contact"]
                    if contact:  # Added check to avoid errors
                        for key in OrderInformation["Party"]["Contact"]:
                            OrderInformation["Party"]["Contact"][key] = contact.get(key, "")

    except Exception as e:
        print(f"Database connection error: {e}")
    finally:
        if mongoClient:
            mongoClient.close()

    return OrderInformation
