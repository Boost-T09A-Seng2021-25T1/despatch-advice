import unittest
import os
import sys
import json
from unittest.mock import patch, AsyncMock, MagicMock
import copy

# Add the project root to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.despatch.OrderReference import (
    OrderNotFoundError,
    InvalidOrderReferenceError,
    createOrderReference,
    dbConnect,
    connectToMongo
)

# Construct the full path to the JSON file in the 'public' folder
dirPath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
filePath = os.path.join(dirPath, "public", "exampleOrderReference.json")


class TestOrderReferenceAdditional(unittest.IsolatedAsyncioTestCase):
    
    async def asyncSetUp(self):
        """Setup test data and mock database connection."""
        # Load test data from JSON file
        with open(filePath, "r") as file:
            self.test_data = json.load(file)

        self.valid_order_id = self.test_data["valid_order_id"]
        self.valid_sales_order_id = self.test_data["valid_sales_order_id"]
        
        # Setup mock database and collection
        self.mock_client = MagicMock()
        self.mock_db = MagicMock()
        self.mock_orders = MagicMock()
        self.mock_orders.find_one = AsyncMock()
        self.mock_orders.update_one = AsyncMock()
        
        # Setup default behavior
        self.mock_orders.find_one.return_value = {
            "ID": self.valid_order_id,
            "SalesOrderID": self.valid_sales_order_id,
            "UUID": "",
            "IssueDate": "",
            "additional_field": "value"  # Add an extra field to test deepcopy
        }
    
    # Test the actual deepcopy operation
    @patch('src.despatch.OrderReference.copy.deepcopy')
    async def test_order_reference_uses_deepcopy(self, mock_deepcopy):
        """Test that createOrderReference uses copy.deepcopy."""
        existing_order = {
            "ID": self.valid_order_id,
            "SalesOrderID": self.valid_sales_order_id,
            "UUID": "old-uuid",
            "IssueDate": "old-date",
            "additional_field": "value"
        }
        
        # Mock the deepcopy to return a real copy
        mock_deepcopy.side_effect = lambda x: copy.deepcopy(x)
        
        self.mock_orders.find_one.return_value = existing_order
        
        await createOrderReference(self.valid_order_id, self.valid_sales_order_id, self.mock_orders)
        
        # Verify deepcopy was called with the existing order
        mock_deepcopy.assert_called_once_with(existing_order)
        
        # Verify update_one was called with the right data
        self.mock_orders.update_one.assert_called_once()
        call_args = self.mock_orders.update_one.call_args[0]
        
        # Check the filter
        self.assertEqual(call_args[0], {"ID": self.valid_order_id})
        
        # Check that the set operation contains the correct fields
        set_operation = call_args[1]["$set"]
        self.assertEqual(set_operation["ID"], self.valid_order_id)
        self.assertEqual(set_operation["SalesOrderID"], self.valid_sales_order_id)
        self.assertEqual(set_operation["UUID"], "")
        self.assertEqual(set_operation["IssueDate"], "")
        self.assertEqual(set_operation["additional_field"], "value")  # Additional field preserved
    
    # Test the update operation
    async def test_update_operation_with_upsert(self):
        """Test that update_one is called with upsert=True."""
        await createOrderReference(self.valid_order_id, self.valid_sales_order_id, self.mock_orders)
        
        # Verify update_one was called with upsert=True
        self.mock_orders.update_one.assert_called_once()
        call_args = self.mock_orders.update_one.call_args
        self.assertTrue(call_args[1].get('upsert', False))
    
    # Test error handling for invalid argument types
    async def test_string_empty_arguments(self):
        """Test with empty string arguments."""
        # Empty strings should be valid as they are still strings
        await createOrderReference("", "", self.mock_orders)
        
        # Verify update_one was called 
        self.mock_orders.update_one.assert_called_once()
    
    async def test_none_collection(self):
        """Test error when collection is None."""
        with self.assertRaises(AttributeError):
            await createOrderReference(self.valid_order_id, self.valid_sales_order_id, None)
    
    # Test the database connection functions
    @patch('src.despatch.OrderReference.motor.motor_asyncio.AsyncIOMotorClient')
    async def test_db_connect(self, mock_motor_client):
        """Test dbConnect function."""
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        mock_motor_client.return_value = mock_client
        
        client, db = await dbConnect()
        
        self.assertEqual(client, mock_client)
        self.assertEqual(db, mock_db)
        mock_motor_client.assert_called_once()
    
    @patch('src.despatch.OrderReference.db.admin.command')
    async def test_connect_to_mongo_success(self, mock_command):
        """Test connectToMongo success case."""
        mock_db = MagicMock()
        mock_db.admin.command = AsyncMock()
        
        await connectToMongo(mock_db)
        
        mock_db.admin.command.assert_called_once_with('ping')
    
    @patch('src.despatch.OrderReference.db.admin.command')
    async def test_connect_to_mongo_failure(self, mock_command):
        """Test connectToMongo failure case."""
        mock_db = MagicMock()
        mock_db.admin.command = AsyncMock(side_effect=Exception("Connection error"))
        
        # This should not raise an exception as the function catches it
        await connectToMongo(mock_db)
        
        mock_db.admin.command.assert_called_once_with('ping')


if __name__ == '__main__':
    unittest.main()