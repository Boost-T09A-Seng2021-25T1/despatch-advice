from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
from pymongo.server_api import ServerApi
import os


load_dotenv(
    dotenv_path=os.path.join(
        os.path.dirname(__file__),
        "../config/.env"
    )
)

uri = os.getenv("MDB_URI")
client = MongoClient(uri, server_api=ServerApi('1'))

# name of the mongodb database
db = client["ubl_docs"]
# name of the collection inside the mongodb
orders = db["orders"]

# Connection test on startup
try:
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")

except Exception as error:
    print(f"Connection failed: {error}")


# ===========================================
# Purpose: Database function to import.
# Add order to db.The data MUST HAVE A UUID STRING KEY

# Argument: object, preferably in the order ubl structure

# Return: added order ID
# ============================================


def addOrder(data):
    try:
        return orders.insert_one(data).inserted_id

    except Exception as error:
        print(f"MongoDB request failed: {error}")


# ===========================================
# Purpose: Database function to import. Fetch order doc.
# Argument: order UUID string

# Return: fetched order object
# ============================================


def getOrderInfo(orderUUID):
    try:
        return orders.find_one({"UUID": orderUUID})

    except Exception as error:
        print(f"MongoDB fetch failed: {error}")


# ===========================================
# Purpose: Database function to import. Deletes order
# Argument: order UUID string

# Return: true if item deleted
# ============================================


def deleteOrder(orderUUID):
    try:
        orders.delete_one({"UUID": orderUUID})
        return True

    except Exception as error:
        print(f"MongoDB delete failed: {error}")
