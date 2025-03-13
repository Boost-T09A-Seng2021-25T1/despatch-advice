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

uri = next(filter(None, [os.getenv("MDB_URI") or os.getenv(
            "MONGO_URI", "mongodb://localhost:27017/testdb")]))

client = MongoClient(uri, server_api=ServerApi('1'))

# name of the mongodb database
db = client["ubl_docs"]
# name of the collection inside the mongodb
orders = db["orders"]
shipments = db["shipments"]

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

# ===========================================
# Purpose: Database function to create a shipment entry.
# Argument: shipmentId (string), data (dictionary)
# Return: inserted shipment ID
# ============================================


def createShipment(shipmentId, data):
    try:
        # Validate required fields
        required_fields = ["ID", "Consignment", "Delivery"]
        if not all(field in data for field in required_fields):
            raise ValueError("Missing required fields: ID, Consignment, or Delivery")

        # Ensure ID and Consignment ID are strings
        if not isinstance(data["ID"], str) or not isinstance(data["Consignment"]["ID"], str):
            raise TypeError("ID and Consignment ID must be strings")

        # Check if shipment already exists
        if shipments.find_one({"ID": shipmentId}):
            raise ValueError("ShipmentId already exists")

        # Insert shipment into MongoDB
        result = shipments.insert_one(data)
        return result.inserted_id

    except Exception as error:
        print(f"MongoDB request failed: {error}")
        return None