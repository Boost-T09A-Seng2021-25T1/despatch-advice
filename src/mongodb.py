from pymongo.mongo_client import MongoClient
import os

uri3 = "&w=majority&appName=BoostT09ACluster"
uri2 = ".r4oz2.mongodb.net/?retryWrites=true"
uri = "mongodb+srv://ched:Archimedes24;@boostt09acluster" + uri2 + uri3

# Create a new client and connect to the server
MDBURI = os.getenv("MDBURI", uri)
client = MongoClient(MDBURI)

try:
    client.admin.command('Connecting to mongodb...')
    print("Successfully connected to MongoDB!")

    db = client["database"]
    collection = db["collection"]

except Exception as error:
    print(error)