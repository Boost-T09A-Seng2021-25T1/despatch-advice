from pymongo import MongoClient
import os



def dbConnect():
    """
    Create a connection to MongoDB
    
    Returns:
        tuple: (client, db) - MongoDB client and database objects
    """
    # Get MongoDB connection details from environment variables or use defaults
    mongo_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017')
    db_name = os.environ.get('MONGODB_DBNAME', 'UBLdb')
    
    # Create a MongoDB client and connect to the database
    client = MongoClient(mongo_uri)
    db = client[db_name]
    
    return client, db

def addOrder(order_data, db):
    """
    Add an order to the database
    
    Args:
        order_data (dict): Order data to insert
        db: MongoDB database connection
    
    Returns:
        str: ID of the inserted document
    """
    try:
        # Determine the collection based on presence of DespatchID or OrderID
        if "DespatchID" in order_data:
            collection = db["despatches"]
            record_id = order_data["DespatchID"]
        else:
            collection = db["orders"]
            record_id = order_data["OrderID"]
        
        # Insert the document
        result = collection.insert_one(order_data)
        
        return str(result.inserted_id) if result.acknowledged else None
    
    except Exception as e:
        print(f"Error inserting document: {str(e)}")
        return None

def getOrderInfo(record_id, db):
    """
    Get order or despatch info from the database
    
    Args:
        record_id (str): ID of the record to retrieve
        db: MongoDB database connection
    
    Returns:
        dict: Document data if found, None otherwise
    """
    try:
        # Check the orders collection first
        order = db["orders"].find_one({"OrderID": record_id})
        if order:
            return order
        
        # If not found in orders, check the despatches collection
        despatch = db["despatches"].find_one({"DespatchID": record_id})
        if despatch:
            return despatch
        
        return None
    
    except Exception as e:
        print(f"Error retrieving document: {str(e)}")
        return None

def updateDocument(record_id, update_data, db):
    """
    Update an existing document
    
    Args:
        record_id (str): ID of the record to update
        update_data (dict): Data to update
        db: MongoDB database connection
    
    Returns:
        bool: True if updated successfully, False otherwise
    """
    try:
        # Determine if this is an order or despatch update
        if record_id.startswith("ORD-"):
            result = db["orders"].update_one(
                {"OrderID": record_id},
                {"$set": update_data}
            )
        else:  # Assume it's a despatch ID
            result = db["despatches"].update_one(
                {"DespatchID": record_id},
                {"$set": update_data}
            )
        
        return result.modified_count > 0
    
    except Exception as e:
        print(f"Error updating document: {str(e)}")
        return False

def deleteDocument(record_id, db):
    """
    Delete a document from the database
    
    Args:
        record_id (str): ID of the record to delete
        db: MongoDB database connection
    
    Returns:
        bool: True if deleted successfully, False otherwise
    """
    try:
        # Determine if this is an order or despatch deletion
        if record_id.startswith("ORD-"):
            result = db["orders"].delete_one({"OrderID": record_id})
        else:  # Assume it's a despatch ID
            result = db["despatches"].delete_one({"DespatchID": record_id})
        
        return result.deleted_count > 0
    
    except Exception as e:
        print(f"Error deleting document: {str(e)}")
        return False