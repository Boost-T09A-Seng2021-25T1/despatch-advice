from src.mongodb import dbConnect, clearDb, addOrder
from src.despatch.deliveryCustomer import deliveryCustomer
import unittest
import json
import os

dirPath = os.path.abspath(os.path.join(
    os.path.dirname(__file__), ".."))

# Construct the full path to the JSON file in the 'public' folder
filePath = os.path.join(
    dirPath,
    "public",
    "exampleOrderDoc.json"
)


class testDeliveryCustomer(unittest.IsolatedAsyncioTestCase):

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

    # this func was not refactored because the db
    # will be wiped after every test
    async def testDeliveryCustomerReturn(self):
        with self.assertRaises(ValueError):
            await deliveryCustomer("FAKE_UUID_KDBSKMWOBFU")

        data = {}
        with open(filePath, "r") as file:
            data = json.load(file)

        await addOrder(data, self.orders)
        res = await deliveryCustomer(
            "6E09886B-DC6E-439F-82D1-7CCAC7F4E3B1"
        )

        self.assertIn("CustomerAssignedAccountID", res)
        self.assertIn("Party", res)

        # Testing nested properties in party object
        party = res["Party"]
        self.assertIn("PartyName", party)
        self.assertIn("PostalAddress", party)
        self.assertIn("PartyTaxScheme", party)
        self.assertIn("Contact", party)

        # testing nested properties in postal address
        postalAdd = party["PostalAddress"]
        self.assertIn("StreetName", postalAdd)
        self.assertIn("BuildingName", postalAdd)
        self.assertIn("BuildingNumber", postalAdd)
        self.assertIn("CityName", postalAdd)
        self.assertIn("PostalZone", postalAdd)
        self.assertIn("CountrySubentity", postalAdd)
        self.assertIn("AddressLine", postalAdd)
        self.assertIn("Country", postalAdd)

        self.assertIn("Line", postalAdd["AddressLine"])
        self.assertIn("IdentificationCode", postalAdd["Country"])

        # testing for nested properties in partytaxscheme
        taxScheme = party["PartyTaxScheme"]
        self.assertIn("RegistrationName", taxScheme)
        self.assertIn("CompanyID", taxScheme)
        self.assertIn("ExemptionReason", taxScheme)
        self.assertIn("TaxScheme", taxScheme)
        self.assertIn("ID", taxScheme["TaxScheme"])
        self.assertIn("TaxTypeCode", taxScheme["TaxScheme"])

        # testing for nested objs in Contact
        contact = party["Contact"]
        self.assertIn("Name", contact)
        self.assertIn("Telephone", contact)
        self.assertIn("Telefax", contact)
        self.assertIn("ElectronicMail", contact)


if __name__ == '__main__':
    unittest.main()