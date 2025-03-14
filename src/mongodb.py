import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorCollection
import asyncio
from dotenv import load_dotenv
import os
import pymongo.errors


load_dotenv(
    dotenv_path=os.path.join(
        os.path.dirname(__file__),
        "../config/.env"
    )
)


uri = next(filter(None, [os.getenv("MDB_URI") or os.getenv(
            "MONGO_URI", "mongodb://localhost:27017/testdb")]))


# Connection test on startup
async def connectToMongo(db):
    try:
        await db.admin.command('ping')
        print("Successfully connected to MongoDB!")

    except Exception as error:
        print(f"Connection failed: {error}")


# ===========================================
# Purpose: Database function to import.
# Creates a new instance of a db connection

# Argument: nil

# Return: db (dictionary) containing all data
# ============================================
async def dbConnect():
    client = motor.motor_asyncio.AsyncIOMotorClient(uri)

    # name of the collection inside the mongodb
    db = client["ubl_docs"]

    return client, db


# ===========================================
# Purpose: Database function to import.
# Add order to db.The data MUST HAVE A UUID STRING KEY

# Argument: object, preferably in the order ubl structure

# Return: added order ID
# ============================================


async def addOrder(data: dict, orders: AsyncIOMotorCollection):
    try:
        response = await orders.insert_one(data)
        return response.inserted_id

    except pymongo.errors.DuplicateKeyError as error:
        raise error


# ===========================================
# Purpose: Database function to import. Fetch order doc.
# Argument: order UUID string

# Return: fetched order object
# ============================================


async def getOrderInfo(orderUUID: str, orders: AsyncIOMotorCollection):
    res = await orders.find_one({"UUID": orderUUID})
    if not res:
        raise ValueError(f"{orderUUID} not found.")
    return res


# ===========================================
# Purpose: Database function to import. Deletes order
# Argument: order UUID string

# Return: true if item deleted
# ============================================


async def deleteOrder(orderUUID, orders: AsyncIOMotorCollection):
    response = await orders.delete_many({"UUID": orderUUID})
    return response.deleted_count > 0


# ===========================================
# Purpose: function for testing only/ Clears db
# Argument: the database itself, not the collection

# Return: nil
# ============================================


async def clearDb(mongoDb: AsyncIOMotorClient):
    await mongoDb.orders.delete_many({})


if __name__ == "__main__":
    orders, db = dbConnect()
    asyncio.run(connectToMongo())
