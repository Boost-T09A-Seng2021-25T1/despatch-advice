import motor.motor_asyncio
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

client = motor.motor_asyncio.AsyncIOMotorClient(uri)

# name of the mongodb database
mongoDb = client["ubl_docs"]
# name of the collection inside the mongodb
orders = mongoDb["orders"]


# Connection test on startup
async def connectToMongo():
    try:
        await client.admin.command('ping')
        print("Successfully connected to MongoDB!")

    except Exception as error:
        print(f"Connection failed: {error}")


# ===========================================
# Purpose: Database function to import.
# Add order to db.The data MUST HAVE A UUID STRING KEY

# Argument: object, preferably in the order ubl structure

# Return: added order ID
# ============================================


async def addOrder(data):
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


async def getOrderInfo(orderUUID):
    try:
        res = await orders.find_one({"UUID": orderUUID})
        return res

    except Exception as error:
        raise error


# ===========================================
# Purpose: Database function to import. Deletes order
# Argument: order UUID string

# Return: true if item deleted
# ============================================


async def deleteOrder(orderUUID):
    try:
        await orders.delete_many({"UUID": orderUUID})
        return True

    except Exception as error:
        raise error


# ===========================================
# Purpose: function for testing only/ Clears db
# Argument: nil

# Return: nil
# ============================================


async def clearDb():
    for eachCollection in await mongoDb.list_collection_names():
        await mongoDb[eachCollection].delete_many({})


if __name__ == "__main__":
    asyncio.run(connectToMongo())
