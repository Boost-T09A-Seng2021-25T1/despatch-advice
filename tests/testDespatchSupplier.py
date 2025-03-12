import unittest
from src.mongodb import getOrderInfo
from src.despatch.despatchSupplier import despatchSupplier

# Testing the despatch supplier section
class testDespatchSupplier(unittest.Testcase):

    # test that the output contains all req subsection
    def testCorrectProperties(self):
        expectedOuterKeys = { "CustomerAssignedAccountID", "Party", }
        expectedPartyKeys = {
            "PartyName",
            "PostalAddress",
            "PartyTaxScheme",
            "Contact"
        }

        functionOutput = despatchSupplier()

        # test for correct outer objects and properties
        self.assertDictEqual(
            functionOutput, 
            expectedOuterKeys, 
            "Error: incorrect dict properties"
        )