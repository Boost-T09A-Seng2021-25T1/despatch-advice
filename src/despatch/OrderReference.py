import motor.motor_asyncio
import asyncio
from dotenv import load_dotenv
import os
import copy

# Construct the absolute path for environment variable loading
dirPath = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "config"
))

# Load environment variables
load_dotenv(
    dotenv_path=os.path.join(dirPath, ".env")
)

# MongoDB URI
uri = os.getenv("MDB_URI") or os.getenv("MONGO_URI",
                                        "mongodb+srv://ched:Archimedes24%3B@boostt09acluster.r4oz2.\
                                            mongodb.net/?retryWrites=true&w="
                                        "majority&appName=\
                                                     BoostT09ACluster")

# ==================================
# Database Connection and Utilities
# ==================================


async def connectToMongo(db):
    """
    Test the MongoDB connection by pinging the database.
    """
    try:
        await db.admin.command('ping')
        print("Successfully connected to MongoDB!")
    except Exception as error:
        print(f"Connection failed: {error}")


async def dbConnect():
    """
    Connect to the MongoDB database and return the client and database objects.
    """
    client = motor.motor_asyncio.AsyncIOMotorClient(uri)
    db = client["ubl_docs"]
    return client, db

# ==================================
# Custom Exceptions
# ==================================


class OrderNotFoundError(Exception):
    """Raised when an order is not found in the database."""
    pass


class InvalidOrderReferenceError(Exception):
    """Raised when invalid arguments are
        provided for creating an OrderReference."""
    pass

# ==================================
# Business Logic
# ==================================


async def createOrderReference(orderId: str, salesOrderId: str, orders):
    """
    Creates an OrderReference stub object in the database.
    Initializes UUID and IssueDate as empty and assigns ID and SalesOrderID.

    Args:
        orderId (str): The ID of the order.
        salesOrderId (str): The ID of the sales order.
        orders: The MongoDB collection for orders.

    Returns:
        None

    Raises:
        InvalidOrderReferenceError: If the arguments are of invalid types.
        OrderNotFoundError: If the order is not found in the database.
    """
    if not isinstance(orderId, str) or not isinstance(salesOrderId, str):
        raise InvalidOrderReferenceError("Invalid argument types")

    existing_order = await orders.find_one({"ID": orderId})

    if not existing_order:
        raise OrderNotFoundError("Order not found")

    # Create a deep copy of the existing order (if needed)
    order_reference = copy.deepcopy(existing_order)
    order_reference.update({
        "ID": orderId,
        "SalesOrderID": salesOrderId,
        "UUID": "",
        "IssueDate": ""
    })

    await orders.update_one({"ID": orderId},
                            {"$set": order_reference}, upsert=True)
    return None

# ==================================
# Main Execution
# ==================================

if __name__ == "__main__":
    # Connect to the database
    client, db = asyncio.run(dbConnect())

    # Test the connection
    asyncio.run(connectToMongo(db))
