import datetime
from src.mongodb import dbConnect
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================================
# Purpose: Ensure a unique index on the shipment ID field.
# Arguments: None
# Returns:
#   - dict: Contains success status and index creation details
# ==================================


async def setup_indexes():
    """Ensure a unique index on the shipment ID field."""
    mongoClient, db = await dbConnect()
    shipments = db["shipments"]

    try:
        # Create a unique index on the "ID" field and get the result
        result = await shipments.create_index("ID", unique=True)
        logger.info(f"Created unique index on 'ID' field. Result: {result}")
        return {
            "success": True,
            "index_name": "ID",
            "operation_result": result,
            "message": "Successfully created unique index on 'ID' field"
        }
    except Exception as e:
        logger.error(f"Failed to create index: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create index"
        }
    finally:
        # Close the MongoDB connection
        mongoClient.close()


# ==================================
# Purpose: Create a shipment entry in the MongoDB database.
# Arguments:
#   - shipment_id (str): The unique ID of the shipment.
#   - data (dict): The shipment data to be inserted.
# Returns:
#   - dict: Contains success status, inserted document
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
        raise ValueError(f"Missing required fields:\
                         {', '.join(missing_fields)}")

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
            return {
                "success": False,
                "error": "Duplicate shipment ID",
                "existing_document": existing_shipment,
                "attempted_data": data
            }

        # Create the new shipment entry
        result = await shipments.insert_one(data)

        # Get the full inserted document
        inserted_document = await shipments.find_one(
             {"_id": result.inserted_id})

        logger.info(f"Inserted shipment with ID: {result.inserted_id}")
        return {
            "success": True,
            "inserted_id": str(result.inserted_id),
            "document": inserted_document,
            "operation_details": {
                "acknowledged": result.acknowledged,
                "operation_time": getattr(result, 'operation_time', None)
            }
        }

    except Exception as e:
        logger.error(f"An error occurred while creating shipment: {e}")
        return {
            "success": False,
            "error": str(e),
            "attempted_data": data
        }
    finally:
        # Close the MongoDB connection
        mongoClient.close()


async def generate_shipment_qr_code(shipment_id, additional_info=None):
    """
    Generate a QR code for a shipment

    Args:
        shipment_id (str): ID of the shipment
        additional_info (dict, optional): Additional information to encode

    Returns:
        dict: Result with base64-encoded QR code image
    """
    from src.utils.qr_generator import generate_qr_code_base64

    try:
        # Get shipment details
        mongoClient, db = await dbConnect()
        shipments = db["shipments"]

        try:
            shipment = await shipments.find_one({"ID": shipment_id})

            if not shipment:
                return {
                    "success": False,
                    "error": f"Shipment with ID '{shipment_id}' not found"
                }

            # Create data for QR code
            qr_data = {
                "shipment_id": shipment_id,
                "tracking_url": (
                    f"https://boostxchange.com/track/{shipment_id}"
                ),
                "created_at": datetime.datetime.now().isoformat()
            }

            # Add delivery information if available
            if "Delivery" in shipment:
                delivery = shipment["Delivery"]
                if "DeliveryAddress" in delivery:
                    address = delivery["DeliveryAddress"]
                    qr_data["delivery_location"] = {
                        "city": address.get("CityName", ""),
                        "country": address.get("Country", {}).get(
                            "IdentificationCode", ""
                        ),
                    }

                if "RequestedDeliveryPeriod" in delivery:
                    period = delivery["RequestedDeliveryPeriod"]
                    qr_data["delivery_date"] = period.get("StartDate", "")

            # Add consignment information if available
            if "Consignment" in shipment:
                qr_data["consignment_id"] = shipment["Consignment"].get(
                    "ID", ""
                )

            # Add additional info if provided
            if additional_info and isinstance(additional_info, dict):
                qr_data.update(additional_info)

            # Generate QR code
            qr_code = generate_qr_code_base64(qr_data)

            return {
                "success": True,
                "shipment_id": shipment_id,
                "qr_code": qr_code,
                "qr_data": qr_data
            }

        finally:
            mongoClient.close()

    except Exception as e:
        logger.error(f"Error generating shipment QR code: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
