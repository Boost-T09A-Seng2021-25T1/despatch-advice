from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
from pymongo.server_api import ServerApi
import os

# Load environment variables from the .env file
load_dotenv(
    dotenv_path=os.path.join(
        os.path.dirname(__file__), "../config/.env"
    )
)

# Set up MongoDB connection URI with a fallback to local DB if not found in the environment variables
uri = next(filter(None, [os.getenv("MDB_URI") or os.getenv("MONGO_URI", "mongodb://localhost:27017/testdb")]))

# Establish connection to MongoDB
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["ubl_docs"]
shipments = db["shipments"]

# Test the connection to MongoDB
def test_connection():
    try:
        client.admin.command('ping')  # Ping MongoDB server to check the connection
        print("Successfully connected to MongoDB!")
    except Exception as error:
        print(f"Connection failed: {error}")

# Database function to create a shipment entry
def create_shipment(shipment_id, data):
    try:
        # Validate required fields: ID, Consignment, Delivery
        required_fields = ["ID", "Consignment", "Delivery"]
        if not all(field in data for field in required_fields):
            raise ValueError("Missing required fields: ID, Consignment, or Delivery")

        # Ensure that "ID" and "Consignment ID" are both strings
        if not isinstance(data["ID"], str) or not isinstance(data["Consignment"]["ID"], str):
            raise TypeError("ID and Consignment ID must be strings")

        # Check if shipment already exists in the database using the shipment ID
        if shipments.find_one({"ID": shipment_id}):
            raise ValueError("ShipmentId already exists in the database")

        # Insert the new shipment entry into the database
        result = shipments.insert_one(data)
        return result.inserted_id  # Return the inserted shipment's ID

    except ValueError as e:
        # Handle specific error (e.g., missing fields, shipment already exists)
        print(f"ValueError: {e}")
        return None
    except TypeError as e:
        # Handle type errors (e.g., invalid data types for ID or Consignment ID)
        print(f"TypeError: {e}")
        return None
    except Exception as error:
        # Catch any other errors and print the message
        print(f"MongoDB request failed: {error}")
        return None
