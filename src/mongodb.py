from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
uri = os.getenv("MDB_URI")
client = MongoClient(uri)

# Connection test
try:
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")

    db = client["database"]
    collection = db["collection"]

except Exception as error:
    print(error)
