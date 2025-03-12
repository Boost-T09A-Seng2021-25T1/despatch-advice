# from pymongo.mongo_client import MongoClient
import motor.motor_asyncio
import asyncio
from dotenv import load_dotenv
# from pymongo.server_api import ServerApi
import os


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
db = client["ubl_docs"]
# name of the collection inside the mongodb
orders = db["orders"]


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

    except Exception as error:
        print(f"MongoDB request failed: {error}")


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
        print(f"MongoDB fetch failed: {error}")


# ===========================================
# Purpose: Database function to import. Deletes order
# Argument: order UUID string

# Return: true if item deleted
# ============================================


async def deleteOrder(orderUUID):
    try:
        await orders.delete_one({"UUID": orderUUID})
        return True

    except Exception as error:
        print(f"MongoDB delete failed: {error}")
        return False


if __name__ == "__main__":
    asyncio.run(connectToMongo())
