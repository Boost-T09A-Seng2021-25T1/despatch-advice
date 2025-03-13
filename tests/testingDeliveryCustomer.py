import unittest
from src.despatch.deliveryCustomer import deliveryCustomer

# Testing the delivery customer section
class TestDeliveryCustomer(unittest.TestCase):

    def testCorrectProperties(self):
        # Expected structure based function's return structure
        expectedOuterKeys = {"CustomerID", "SupplierID", "Party"}
        expectedPartyKeys = {
            "PartyName",
            "PostalAddress",
            "PartyTaxScheme",
            "Contact"
        }
        
        # Expected nested structure keys
        expectedPostalAddressKeys = {
            "StreetName", "BuildingName", "BuildingNumber", "CityName",
            "PostalZone", "CountrySubentity", "AddressLine", "Country"
        }
        
        expectedPartyTaxSchemeKeys = {
            "RegistrationName", "CompanyID", "ExemptionReason", "TaxScheme"
        }
        
        expectedContactKeys = {
            "Name", "Telephone", "Telefax", "ElectronicMail"
        }

        # Call the function with a despatchID that exists in your test database
        functionOutput = deliveryCustomer("565899")

        # Test for correct outer keys
        self.assertEqual(
            set(functionOutput.keys()), 
            expectedOuterKeys, 
            "Error: incorrect outer dict properties"
        )
        
        # Test for correct Party keys
        self.assertEqual(
            set(functionOutput["Party"].keys()), 
            expectedPartyKeys, 
            "Error: incorrect Party dict properties"
        )
        
        # Test for correct PostalAddress keys
        self.assertEqual(
            set(functionOutput["Party"]["PostalAddress"].keys()), 
            expectedPostalAddressKeys, 
            "Error: incorrect PostalAddress dict properties"
        )
        
        # Test for correct PartyTaxScheme keys
        self.assertEqual(
            set(functionOutput["Party"]["PartyTaxScheme"].keys()), 
            expectedPartyTaxSchemeKeys, 
            "Error: incorrect PartyTaxScheme dict properties"
        )
        
        # Test for correct Contact keys
        self.assertEqual(
            set(functionOutput["Party"]["Contact"].keys()), 
            expectedContactKeys, 
            "Error: incorrect Contact dict properties"
        )