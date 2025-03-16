from src.mongodb import dbConnect, clearDb, addOrder
from src.despatch.deliveryCustomer import deliveryCustomer
import unittest
import json
import os

dirPath = os.path.abspath(os.path.join(
    os.path.dirname(__file__), ".."))

# Construct the full path to the JSON file in the 'public' folder.
filePath = os.path.join(
    dirPath,
    "public",
    "exampleOrderDoc.json"
)


class TestDeliveryCustomer(unittest.IsolatedAsyncioTestCase):

    # ============================================
    # These two funcs run before and after every test
    async def asyncSetUp(self):
        self.client, self.db = await dbConnect()
        self.orders = self.db["orders"]

    async def asyncTearDown(self):
        if self.client.close:
            await clearDb(self.db)
            self.client.close()
    # ============================================
    # ============================================

    # Test delivery customer and general order information.
    async def testDeliveryCustomerReturn(self):
        # Ensure a ValueError is raised for an invalid UUID.
        with self.assertRaises(ValueError):
            await deliveryCustomer("FAKE_UUID_KDBSKMWOBFU")

        data = {}
        with open(filePath, "r") as file:
            data = json.load(file)

        await addOrder(data, self.orders)
        order_info = await deliveryCustomer(
            "6E09886B-DC6E-439F-82D1-7CCAC7F4E3B1"
        )

        # Check if basic order details are present.
        self.assertIn("CustomerAssignedAccountID", order_info)
        self.assertIn("SupplierAssignedAccountID", order_info)

        # Ensure party details are in the order (more general check).
        self.assertIn("Party", order_info)
        party = order_info["Party"]
        self.assertIsInstance(party, dict)

        # General checks for nested Party details
        self.assertIn("PartyName", party)
        self.assertIn("PostalAddress", party)
        self.assertIn("PartyTaxScheme", party)
        self.assertIn("Contact", party)

        # Test that PostalAddress is a dictionary with expected fields.
        postal_add = party["PostalAddress"]
        self.assertIsInstance(postal_add, dict)
        self.assertIn("StreetName", postal_add)
        self.assertIn("BuildingName", postal_add)
        self.assertIn("BuildingNumber", postal_add)
        self.assertIn("CityName", postal_add)
        self.assertIn("PostalZone", postal_add)
        self.assertIn("CountrySubentity", postal_add)
        self.assertIn("AddressLine", postal_add)
        self.assertIn("Country", postal_add)

        # Test that AddressLine has a nested field.
        address_add = postal_add["AddressLine"]
        self.assertIsInstance(address_add, dict)
        self.assertIn("Line", address_add)

        # Test that Country has a nested field.
        country_add = postal_add["Country"]
        self.assertIsInstance(country_add, dict)
        self.assertIn("IdentificationCode", country_add)

        # If PartyTaxScheme exists, ensure it's properly structured.
        tax_scheme = party.get("PartyTaxScheme", {})
        self.assertIsInstance(tax_scheme, dict)
        if tax_scheme:
            self.assertIn("RegistrationName", tax_scheme)
            self.assertIn("CompanyID", tax_scheme)
            self.assertIn("ExemptionReason", tax_scheme)
            self.assertIn("TaxScheme", tax_scheme)

        # Test that TaxScheme has a nested field.
        tScheme_add = tax_scheme["TaxScheme"]
        self.assertIsInstance(tScheme_add, dict)
        self.assertIn("ID", tScheme_add)
        self.assertIn("TaxTypeCode", tScheme_add)

        # Test the Contact information.
        contact = party["Contact"]
        self.assertIsInstance(contact, dict)
        self.assertIn("Name", contact)
        self.assertIn("Telephone", contact)
        self.assertIn("ElectronicMail", contact)


if __name__ == '__main__':
    unittest.main()
