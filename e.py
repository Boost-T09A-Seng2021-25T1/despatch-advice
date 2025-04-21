{"_id":{
    "$oid":"680633cc6c027caf17df13dc"
    },
    "OrderID":"ORD-3E828263",
    "UUID":"c8c24658-b71c-473f-b36d-5f94eb8d2a27",
    "CustomerID":"CUST-1",
    "Items":[{
        "item_id":"ITEM-001",
        "quantity":{"$numberDouble":"2.0"},
        "price":{"$numberDouble":"10.0"}
    }],
    "Status":"Created",
    "CreationDate":"2025-04-21T22:02:20.951636",
    "LastModified":"2025-04-21T22:02:20.951636",
    "ID":"ORD-2EE5E842",
    "IssueDate":"",
    "SalesOrderID":"",
    "SellerSupplierParty": {
    "CustomerAssignedAccountID": "SUPP-123",
    "SupplierAssignedAccountID": "SUPP-456",
        "Party": {
            "PartyName": "Test Supplier",
            "PostalAddress": {
            "StreetName": "123 Supply Rd",
            "BuildingName": "Supply House",
            "BuildingNumber": "1",
            "CityName": "Supplyville",
            "PostalZone": "12345",
            "CountrySubentity": "NSW",
            "AddressLine": {
                "Line": "Suite 3, Level 2"
            },
            "Country": {
                "IdentificationCode": "AU"
            }
            },
            "PartyTaxScheme": {
            "RegistrationName": "Test Pty Ltd",
            "CompanyID": "A1234567B",
            "ExemptionReason": "None",
            "TaxScheme": {
                "ID": "GST",
                "TaxTypeCode": "GST"
            }
            },
            "Contact": {
            "Name": "John Supplier",
            "Telephone": "+61 400 123 456",
            "Telefax": "+61 400 654 321",
            "ElectronicMail": "supplier@example.com"
            }
        }
    }
}