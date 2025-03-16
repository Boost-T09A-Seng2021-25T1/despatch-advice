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


uri = next(
    filter(
        None,
        [
            os.getenv("MDB_URI")
            or os.getenv("MONGO_URI", "mongodb://localhost:27017/testdb")
        ],
    )
)


# Connection test on startup
async def connectToMongo(db):
    try:
        await db.admin.command("ping")
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

    # Ensure the client is properly closed when done
    try:
        return client, db
    except Exception as e:
        client.close()
        raise e


# ===========================================
# Purpose: Database function to import.
# Add order to db.The data MUST HAVE A UUID STRING KEY

# Argument: object, preferably in the order ubl structure

# Return: added order ID
# ============================================
async def addOrder(data: dict, db: AsyncIOMotorCollection):
    try:
        response = await db.orders.insert_one(data)
        return response.inserted_id

    except pymongo.errors.DuplicateKeyError as error:
        raise error


# ===========================================
# Purpose: Database function to import. Fetch order doc.
# Argument: order UUID string

# Return: fetched order object
# ============================================
async def getOrderInfo(orderUUID: str, db: AsyncIOMotorCollection):
    try:
        res = await db.orders.find_one({"UUID": orderUUID})
        if not res:
            # Try looking up by OrderID too, as some tests might be using this
            res = await db.orders.find_one({"OrderID": orderUUID})
            if not res:
                raise ValueError(f"{orderUUID} not found.")
        return res
    except Exception as e:
        print(f"Error retrieving order: {str(e)}")
        return None


# ===========================================
# Purpose: Database function to import. Deletes order
# Argument: order UUID string

# Return: true if item deleted
# ============================================
async def deleteOrder(orderUUID, db: AsyncIOMotorCollection):
    response = await db.orders.delete_many({"UUID": orderUUID})
    return response.deleted_count > 0


# ===========================================
# Purpose: function for testing only/ Clears db
# Argument: the database itself, not the collection

# Return: nil
# ============================================
async def clearDb(mongoDb: AsyncIOMotorClient):
    await mongoDb.orders.delete_many({})


async def updateDocument(document_id, update_data, db):
    """
    Update a document in the database

    Args:
        document_id (str): ID of the document to update
        update_data (dict): Data to update
        db: Database connection

    Returns:
        bool: True if updated successfully, False otherwise
    """
    try:
        # Try to update in orders collection first
        if document_id.startswith("ORD-"):
            result = await db.orders.update_one(
                {"OrderID": document_id}, {"$set": update_data}
            )
        # Otherwise try in despatches collection
        else:
            result = await db.despatches.update_one(
                {"DespatchID": document_id}, {"$set": update_data}
            )

        # Check if the update was successful
        return result.modified_count > 0

    except Exception as e:
        print(f"Error updating document: {str(e)}")
        return False


async def deleteDocument(document_id, db):
    """
    Delete a document from the database

    Args:
        document_id (str): ID of the document to delete
        db: Database connection

    Returns:
        bool: True if deleted successfully, False otherwise
    """
    try:
        # Try to delete from orders collection first
        if document_id.startswith("ORD-"):
            result = await db.orders.delete_one({"OrderID": document_id})
        # Otherwise try in despatches collection
        else:
            result = await db.despatches.delete_one({"DespatchID":
                                                     document_id})

        # Check if the deletion was successful
        return result.deleted_count > 0

    except Exception as e:
        print(f"Error deleting document: {str(e)}")
        return False


# Only run this if called directly
if __name__ == "__main__":

    async def main():
        client, db = await dbConnect()
        try:
            await connectToMongo(db)
        finally:
            client.close()

    asyncio.run(main())
