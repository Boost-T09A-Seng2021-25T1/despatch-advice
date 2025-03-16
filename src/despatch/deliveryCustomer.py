import os
from src.mongodb import getOrderInfo, dbConnect

dirPath = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)


async def deliveryCustomer(UUID):
    try:
        mongoClient, db = await dbConnect()
    except Exception as e:
        raise ValueError(f"Database connection error: {e}")

    try:
        orders = db["orders"]

        # Retrieve the order document.
        data = await getOrderInfo(UUID, orders)

        # is "DeliveryCustomerParty" present; otherwise,
        # assume the returned document is already the delivery data.
        delivery_data = data.get("DeliveryCustomerParty", data)

        # Build default structure.
        OrderInformation = {
            "CustomerAssignedAccountID": delivery_data.get(
                "CustomerAssignedAccountID", ""
            ),
            "SupplierAssignedAccountID": delivery_data.get(
                "SupplierAssignedAccountID", ""
            ),
            "Party": {
                "PartyName": "",
                "PostalAddress": {
                    "StreetName": "",
                    "BuildingName": "",
                    "BuildingNumber": "",
                    "CityName": "",
                    "PostalZone": "",
                    "CountrySubentity": "",
                    "AddressLine": {"Line": ""},
                    "Country": {"IdentificationCode": ""},
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
                    "ElectronicMail": "",
                },
            },
        }

        # Party if present.
        party = delivery_data.get("Party", {})
        OrderInformation["Party"]["PartyName"] = party.get("PartyName", "")

        # PostalAddress.
        postal = party.get("PostalAddress", {})
        for key in OrderInformation["Party"]["PostalAddress"]:
            if key == "Country":
                OrderInformation["Party"][
                "PostalAddress"][
                "Country"][
                    "IdentificationCode"
                ] = (
                    postal.get("Country", {})
                    .get("IdentificationCode", "")
                )
            elif key == "AddressLine":
                OrderInformation["Party"][
                    "PostalAddress"][
                    "AddressLine"][
                    "Line"
                ] = (
                    postal.get("AddressLine", {})
                    .get("Line", "")
                )
            else:
                OrderInformation["Party"]["PostalAddress"][key] = postal.get(
                    key, ""
                )

        # PartyTaxScheme.
        tax_scheme = party.get("PartyTaxScheme", {})
        for key in OrderInformation["Party"]["PartyTaxScheme"]:
            if key == "TaxScheme":
                ts = tax_scheme.get("TaxScheme", {})
                OrderInformation["Party"]["PartyTaxScheme"]["TaxScheme"][
                    "ID"
                ] = ts.get("ID", "")
                OrderInformation["Party"]["PartyTaxScheme"]["TaxScheme"][
                    "TaxTypeCode"
                ] = ts.get("TaxTypeCode", "")
            else:
                OrderInformation["Party"]["PartyTaxScheme"][key] = tax_scheme.get(
                    key, ""
                )

        # Contact if present.
        contact = party.get("Contact", {})
        for key in OrderInformation["Party"]["Contact"]:
            OrderInformation["Party"]["Contact"][key] = contact.get(key, "")

        return OrderInformation

    except Exception as e:
        raise ValueError(f"Database connection error: {e}")
    finally:
        mongoClient.close()
