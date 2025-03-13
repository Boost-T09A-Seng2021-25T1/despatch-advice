import unittest
import json
from src.despatch.shipment import create_shipment

class TestCreateShipment(unittest.TestCase):
    
    def setUp(self):
        self.valid_shipment_id = "SHIP-123456"
        self.invalid_shipment_id = "SHIP-INVALID"
        
        self.valid_payload = {
            "ID": "SHIP-123456",
            "Consignment": {"ID": "CON-789012"},
            "Delivery": {
                "DeliveryAddress": {
                    "StreetName": "Main Street",
                    "BuildingName": "Building A",
                    "BuildingNumber": "10",
                    "CityName": "Sample City",
                    "PostalZone": "12345",
                    "CountrySubentity": "Region X",
                    "AddressLine": "Address details",
                    "Country": {"IdentificationCode": "US"}
                },
                "RequestedDeliveryPeriod": {
                    "StartDate": "2025-06-01",
                    "StartTime": "08:00",
                    "EndDate": "2025-06-05",
                    "EndTime": "18:00"
                }
            }
        }
        
    # --- SUCCESS CASES ---
    def test_create_valid_shipment(self):
        response = create_shipment(self.valid_shipment_id, self.valid_payload)
        self.assertEqual(response, None)  # Assuming successful execution returns None

    def test_create_shipment_with_minimum_fields(self):
        minimal_payload = {"ID": "SHIP-654321", "Consignment": {"ID": "CON-456789"}, "Delivery": {}}
        response = create_shipment("SHIP-654321", minimal_payload)
        self.assertEqual(response, None)
        
    def test_create_shipment_with_extra_fields(self):
        extra_payload = self.valid_payload.copy()
        extra_payload["ExtraField"] = "Extra Value"
        response = create_shipment(self.valid_shipment_id, extra_payload)
        self.assertEqual(response, None)
        
    def test_create_shipment_with_different_id_format(self):
        response = create_shipment("123-NEW-SHIPMENT", self.valid_payload)
        self.assertEqual(response, None)
        
    # --- FAILURE CASES ---
    def test_create_shipment_missing_fields(self):
        invalid_payload = {}  # Completely missing required fields
        with self.assertRaises(ValueError):
            create_shipment(self.valid_shipment_id, invalid_payload)
        
    def test_create_shipment_invalid_field_types(self):
        invalid_payload = self.valid_payload.copy()
        invalid_payload["ID"] = 123456  # Should be a string
        with self.assertRaises(TypeError):
            create_shipment(self.valid_shipment_id, invalid_payload)

    def test_create_shipment_invalid_shipment_id(self):
        with self.assertRaises(ValueError):
            create_shipment(self.invalid_shipment_id, self.valid_payload)
        
    def test_create_shipment_nonexistent_shipment_id(self):
        nonexistent_shipment_id = "SHIP-NOTFOUND"
        with self.assertRaises(FileNotFoundError):
            create_shipment(nonexistent_shipment_id, self.valid_payload)
        
if __name__ == "__main__":
    unittest.main()