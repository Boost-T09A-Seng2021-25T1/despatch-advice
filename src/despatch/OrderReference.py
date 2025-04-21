import motor.motor_asyncio
from dotenv import load_dotenv
import os
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(dotenv_path=os.path.join(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config")),
    ".env"
    )
)

# MongoDB configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv:"
                        "//ched:Archimedes24%3B@boostt09acluster."
                        "r4oz2.mongodb.net/?retryWrites=true&w="
                        "majority&appName=BoostT09ACluster")
DATABASE_NAME = "ubl_docs"


class OrderNotFoundError(Exception):
    """Raised when an order is not found in the database."""
    pass


class InvalidOrderReferenceError(Exception):
    """Raised when invalid arguments are provided."""
    pass


async def get_db_connection() -> tuple[motor.motor_asyncio.
                                       AsyncIOMotorClient, Any]:
    """Establish MongoDB connection."""
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    try:
        await client.admin.command('ping')
        logger.info("Connected to MongoDB")
        return client, db
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        raise


async def create_order_reference(
    order_id: str,
    sales_order_id: str,
    collection: motor.motor_asyncio.AsyncIOMotorCollection
) -> Dict[str, Any]:
    """
    Creates/updates an OrderReference and returns the complete document.

    Args:
        order_id: The order ID
        sales_order_id: The sales order ID
        collection: MongoDB collection instance

    Returns:
        The complete order reference document

    Raises:
        InvalidOrderReferenceError: If invalid arguments are provided
        OrderNotFoundError: If order doesn't exist
    """
    if not isinstance(order_id, str) or not isinstance(sales_order_id, str):
        raise InvalidOrderReferenceError("IDs must be strings")

    # Check if order exists
    existing_order = await collection.find_one({"OrderID": order_id})
    if not existing_order:
        raise OrderNotFoundError(f"Order {order_id} not found")

    # Create update document
    update_data = {
        "$set": {
            "ID": order_id,
            "SalesOrderID": sales_order_id,
            "UUID": existing_order.get("UUID", ""),
            "IssueDate": existing_order.get("IssueDate", "")
        }
    }

    # Perform upsert and return the document
    result = await collection.find_one_and_update(
        {"OrderID": order_id},
        update_data,
        upsert=True,
        return_document=True
    )

    return result
