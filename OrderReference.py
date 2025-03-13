import motor.motor_asyncio
import asyncio
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(
    dotenv_path=os.path.join(
        os.path.dirname(__file__), "../config/.env"
    )
)

# MongoDB URI
uri = os.getenv("MDB_URI") or os.getenv("MONGO_URI", "mongodb://localhost:27017/testdb")

# Connection test on startup
async def connectToMongo(db):
    try:
        await db.admin.command('ping')
        print("Successfully connected to MongoDB!")
    except Exception as error:
        print(f"Connection failed: {error}")

# Database connection
async def dbConnect():
    client = motor.motor_asyncio.AsyncIOMotorClient(uri)
    db = client["ubl_docs"]
    return client, db

# Custom Exceptions
class OrderNotFoundError(Exception):
    pass

class InvalidOrderReferenceError(Exception):
    pass

# Function to create an OrderReference
async def createOrderReference(orderId: str, salesOrderId: str, orders):
    """
    Creates an OrderReference stub object in the database.
    Initializes UUID and IssueDate as empty and assigns ID and SalesOrderID.
    """
    
    if not isinstance(orderId, str) or not isinstance(salesOrderId, str):
        raise InvalidOrderReferenceError("Invalid argument types")

    existing_order = await orders.find_one({"ID": orderId})
    
    if not existing_order:
        raise OrderNotFoundError("Order not found")
    
    order_reference = {
        "ID": orderId,
        "SalesOrderID": salesOrderId,
        "UUID": "",
        "IssueDate": ""
    }
    
    await orders.update_one({"ID": orderId}, {"$set": order_reference}, upsert=True)
    return None

if __name__ == "__main__":
    client, db = asyncio.run(dbConnect())
    asyncio.run(connectToMongo(db))