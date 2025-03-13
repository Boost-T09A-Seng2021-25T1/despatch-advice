import unittest
import asyncio
from src.mongodb import createOrderReference, getOrderInfo
from src.despatch.testingOrderReference import OrderNotFoundError, InvalidOrderReferenceError

class TestCreateOrderReference(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        """Setup valid test data"""
        self.valid_order_id = "ORDER-12345"
        self.valid_sales_order_id = "SALES-98765"
        
        # Ensure the test order exists in the database
        self.existing_order = {
            "ID": self.valid_order_id,
            "SalesOrderID": self.valid_sales_order_id,
        }
        await createOrderReference(self.valid_order_id, self.valid_sales_order_id)
    
    async def test_create_order_reference_success(self):
        """Test successful creation of OrderReference"""
        result = await createOrderReference(self.valid_order_id, self.valid_sales_order_id)
        self.assertIsNone(result)
    
    async def test_order_reference_fields_initialized_correctly(self):
        """Ensure UUID and IssueDate are empty after creation"""
        order_ref = await getOrderInfo(self.valid_order_id)
        self.assertEqual(order_ref["UUID"], "")
        self.assertEqual(order_ref["IssueDate"], "")
    
    async def test_id_and_sales_order_id_persisted(self):
        """Ensure ID and SalesOrderID are correctly set"""
        order_ref = await getOrderInfo(self.valid_order_id)
        self.assertEqual(order_ref["ID"], self.valid_order_id)
        self.assertEqual(order_ref["SalesOrderID"], self.valid_sales_order_id)
    
    async def test_create_multiple_order_references(self):
        """Test creating multiple order references doesn't override existing ones"""
        new_order_id = "ORDER-54321"
        new_sales_order_id = "SALES-67890"
        await createOrderReference(new_order_id, new_sales_order_id)
        new_order_ref = await getOrderInfo(new_order_id)
        self.assertEqual(new_order_ref["ID"], new_order_id)
        self.assertEqual(new_order_ref["SalesOrderID"], new_sales_order_id)
    
    # Failing Tests
    
    async def test_create_order_reference_missing_id(self):
        """Test error when OrderId is missing"""
        with self.assertRaises(InvalidOrderReferenceError):
            await createOrderReference(None, self.valid_sales_order_id)
    
    async def test_create_order_reference_missing_sales_order_id(self):
        """Test error when SalesOrderID is missing"""
        with self.assertRaises(InvalidOrderReferenceError):
            await createOrderReference(self.valid_order_id, None)
    
    async def test_create_order_reference_nonexistent_order(self):
        """Test 404 error when order does not exist"""
        nonexistent_order_id = "ORDER-00000"
        nonexistent_sales_order_id = "SALES-00000"
        with self.assertRaises(OrderNotFoundError):
            await createOrderReference(nonexistent_order_id, nonexistent_sales_order_id)
    
    async def test_create_order_reference_invalid_types(self):
        """Test 400 error when incorrect types are provided"""
        with self.assertRaises(InvalidOrderReferenceError):
            await createOrderReference(12345, ["invalid-list"])

if __name__ == '__main__':
    unittest.main()
