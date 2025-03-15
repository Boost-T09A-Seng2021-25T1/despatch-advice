import motor.motor_asyncio
import asyncio
import logging
from dotenv import load_dotenv
import os
from pymongo.server_api import ServerApi
from pymongo.errors import DuplicateKeyError

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../config/.env"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up MongoDB connection URI with a fallback to local DB
uri = os.getenv("MDB_URI") or os.getenv("MONGO_URI", "mongodb://localhost:27017/testdb")

# Establish connection to MongoDB
client = motor.motor_asyncio.AsyncIOMotorClient(uri, server_api=ServerApi("1"))
db = client["ubl_docs"]
shipments = db["shipments"]

# Ensure a unique index on shipment ID
async def setup_indexes():
    await shipments.create_index("ID", unique=True)

# Test the connection to MongoDB
async def test_connection():
    try:
        await client.admin.command("ping")  # Ping MongoDB server to check the connection
        logger.info("Successfully connected to MongoDB!")
    except Exception as error:
        logger.error(f"Connection failed: {error}")

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

        # Check if shipment already exists in the database using the shipment ID
        existing_shipment = await shipments.find_one({"ID": shipment_id})
        if existing_shipment:
            raise DuplicateKeyError("ShipmentId already exists in the database")

        # Insert the new shipment entry into the database
        result = await shipments.insert_one(data)
        return {"success": True, "inserted_id": str(result.inserted_id)}

    except ValueError as e:
        logger.error(f"ValueError: {e}")
        return {"success": False, "error": str(e)}
    except TypeError as e:
        logger.error(f"TypeError: {e}")
        return {"success": False, "error": str(e)}
    except DuplicateKeyError as e:
        logger.warning(f"DuplicateKeyError: {e}")
        return {"success": False, "error": "Shipment ID already exists"}
    except Exception as error:
        logger.error(f"MongoDB request failed: {error}")
        return {"success": False, "error": "Database operation failed"}

# Example usage
if __name__ == "__main__":
    asyncio.run(setup_indexes())  # Ensure index is set before testing
    asyncio.run(test_connection())
