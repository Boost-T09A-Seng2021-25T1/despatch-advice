from src.mongodb import dbConnect
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================================
# Purpose: Ensure a unique index on the shipment ID field.
# Arguments: None
# Returns: None
# ==================================


async def setup_indexes():
    """Ensure a unique index on the shipment ID field."""
    mongoClient, db = await dbConnect()
    shipments = db["shipments"]

    try:
        # Create a unique index on the "ID" field
        await shipments.create_index("ID", unique=True)
        logger.info("Created unique index on 'ID' field.")
    except Exception as e:
        logger.error(f"Failed to create index: {e}")
    finally:
        # Close the MongoDB connection
        mongoClient.close()


# ==================================
# Purpose: Create a shipment entry in the MongoDB database.
# Arguments:
#   - shipment_id (str): The unique ID of the shipment.
#   - data (dict): The shipment data to be inserted.
# Returns:
#   - dict: A dictionary containing the success status and inserted ID.
# ==================================

async def create_shipment(shipment_id: str, data: dict):
    # Validate types of shipment_id and data
    if not isinstance(shipment_id, str):
        raise TypeError("Shipment ID must be a string")

    # Validate shipment ID format using regex
    if not re.match(r"^SHIP-\d{6}$", shipment_id):
        raise ValueError("Invalid shipment ID format'.")

    if not isinstance(data, dict):
        raise TypeError("Shipment data must be a dictionary")

    # Validate required fields: ID, Consignment, Delivery
    required_fields = ["ID", "Consignment", "Delivery"]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValueError
    (f"Missing required fields: {', '.join(missing_fields)}")

    # Ensure "ID" and "Consignment ID" are both strings
    if not isinstance(data["ID"], str):
        raise TypeError("Shipment data 'ID' must be a string")
    if ("Consignment" in data
            and not isinstance(data["Consignment"].get("ID"), str)):
        raise TypeError("Consignment 'ID' must be a string")

    # Connect to MongoDB
    mongoClient, db = await dbConnect()
    shipments = db["shipments"]

    try:
        # Check if a shipment with the same ID already exists
        existing_shipment = await shipments.find_one({"ID": shipment_id})
        if existing_shipment:
            logger.error(f"Duplicate shipment ID: {shipment_id}")
            return {"success": False, "error": "Duplicate shipment ID"}

        # Create the new shipment entry
        result = await shipments.insert_one(data)
        logger.info(f"Inserted shipment with ID: {result.inserted_id}")
        return {"success": True, "inserted_id": str(result.inserted_id)}

    except Exception as e:
        logger.error(f"An error occurred while creating shipment: {e}")
        return {"success": False, "error": str(e)}
    finally:
        # Close the MongoDB connection
        mongoClient.close()
