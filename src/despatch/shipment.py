from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(
    dotenv_path=os.path.join(
        os.path.dirname(__file__), "../config/.env"
    )
)

# Set up MongoDB connection URI with a fallback to local DB
uri = os.getenv("MDB_URI") or os.getenv("MONGO_URI", "mongodb://localhost:27017/testdb")

# Establish async connection to MongoDB
client = AsyncIOMotorClient(uri)
db = client["ubl_docs"]
shipments = db["shipments"]

# Test the connection to MongoDB
async def test_connection():
    try:
        await client.admin.command('ping')  # Ping MongoDB server to check the connection
        print("Successfully connected to MongoDB!")
    except Exception as error:
        print(f"Connection failed: {error}")

# Database function to create a shipment entry
async def create_shipment(shipment_id: str, data: dict):
    try:
        # Validate required fields: ID, Consignment, Delivery
        required_fields = ["ID", "Consignment", "Delivery"]
        if not all(field in data for field in required_fields):
            raise ValueError("Missing required fields: ID, Consignment, or Delivery")

        # Ensure that "ID" and "Consignment ID" are both strings
        if not isinstance(data["ID"], str) or not isinstance(data["Consignment"]["ID"], str):
            raise TypeError("ID and Consignment ID must be strings")

        # Check if shipment already exists in the database
        existing_shipment = await shipments.find_one({"ID": shipment_id})
        if existing_shipment:
            raise ValueError("ShipmentId already exists in the database")

        # Insert the new shipment entry into the database
        result = await shipments.insert_one(data)
        return result.inserted_id  # Return the inserted shipment's ID

    except ValueError as e:
        print(f"ValueError: {e}")
        return None
    except TypeError as e:
        print(f"TypeError: {e}")
        return None
    except Exception as error:
        print(f"MongoDB request failed: {error}")
        return None