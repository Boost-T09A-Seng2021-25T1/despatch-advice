# ================================================
# This file will handle the delivery Customer section

# ================================================
<<<<<<< HEAD
from pymongo import MongoClient
import os
from dotenv import load_dotenv

def deliveryCustomer(despatchID):

    load_dotenv()

    MDB_URI = os.getenv("MDB_URI")

    OrderInformation = {
        "CustomerID": "", 
        "SupplierID": "",
        "Party": {
            "PartyName": "",
            "PostalAddress": {
                "StreetName":"",
                "BuildingName":"",
                "BuildingNumber":"",
                "CityName":"",
                "PostalZone":"",
                "CountrySubentity":"",
                "AddressLine":"",
                "Country": {
                    "IdentificationCode":""
                },
            },
            "PartyTaxScheme": {
                "RegistrationName":"",
                "CompanyID":"",
                "ExemptionReason":"",
                "TaxScheme": {
                    "ID":"",
                    "TaxTypeCode":""
                },
            },
            "Contact": {
                "Name":"",
                "Telephone":"",
                "Telefax":"",
                "ElectronicMail":""
            } 
        }
    }

    try:
        client = MongoClient(MDB_URI)
        db = client["ubl_docs"]
        collection = db["orders"]

        result = collection.find_one(
            {"_id.ID": despatchID},
            {"DeliveryCustomerParty": 1, "_id": 0}
        )
        
        if result and "DeliveryCustomerParty" in result:
            delivery_party = result["DeliveryCustomerParty"]
            
            # Extract CustomerID and SupplierID
            OrderInformation["CustomerID"] = delivery_party.get("CustomerAssignedAccountID", "")
            OrderInformation["SupplierID"] = delivery_party.get("SupplierAssignedAccountID", "")
            
            # Extract Party information
            if "Party" in delivery_party:
                party = delivery_party["Party"]
                
                # PartyName
                if "PartyName" in party:
                    OrderInformation["Party"]["PartyName"] = party["PartyName"]
                
                # PostalAddress
                if "PostalAddress" in party:
                    postal = party["PostalAddress"]
                    for key in OrderInformation["Party"]["PostalAddress"]:
                        if key == "Country":
                            if "Country" in postal and "IdentificationCode" in postal["Country"]:
                                OrderInformation["Party"]["PostalAddress"]["Country"]["IdentificationCode"] = postal["Country"]["IdentificationCode"]
                        elif key in postal:
                            OrderInformation["Party"]["PostalAddress"][key] = postal[key]
                
                # PartyTaxScheme
                if "PartyTaxScheme" in party:
                    tax_scheme = party["PartyTaxScheme"]
                    for key in OrderInformation["Party"]["PartyTaxScheme"]:
                        if key == "TaxScheme":
                            if "TaxScheme" in tax_scheme:
                                ts = tax_scheme["TaxScheme"]
                                if "ID" in ts:
                                    OrderInformation["Party"]["PartyTaxScheme"]["TaxScheme"]["ID"] = ts["ID"]
                                if "TaxTypeCode" in ts:
                                    OrderInformation["Party"]["PartyTaxScheme"]["TaxScheme"]["TaxTypeCode"] = ts["TaxTypeCode"]
                        elif key in tax_scheme:
                            OrderInformation["Party"]["PartyTaxScheme"][key] = tax_scheme[key]
                
                # Contact
                if "Contact" in party:
                    contact = party["Contact"]
                    for key in OrderInformation["Party"]["Contact"]:
                        if key in contact:
                            OrderInformation["Party"]["Contact"][key] = contact[key]
        
    except Exception as e:
        print(f"Database connection error: {e}")
    finally:
        if client:
            client.close()
            
    return OrderInformation
=======


import sys
import os


sys.path.append(os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), "..", ".."
    )
))
>>>>>>> origin/main
