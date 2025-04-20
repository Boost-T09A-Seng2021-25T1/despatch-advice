import json
import os
from datetime import datetime, timedelta
from pymongo import MongoClient
from src.despatch.authUtils import verify_google_token, create_access_token


def get_db():
    uri = os.getenv("MDB_URI")
    db_name = os.getenv("MONGO_DB_NAME", "ubl_docs")
    client = MongoClient(uri)
    return client, client[db_name]


def init_user_collection(db):
    users = db["users"]
    try:
        users.create_index("google_id", unique=True)
    except Exception as e:
        print(f"Index creation skipped or failed: {e}")
    return users


def register_user(google_user, users):
    try:
        users.insert_one({
            "google_id": google_user["sub"],
            "name": google_user["name"],
            "email": google_user["email"],
            "picture": google_user.get("picture"),
            "created_at": datetime.utcnow(),
        })
    except Exception as e:
        print(f"User may already exist or error occurred: {e}")


def lambda_handler(event, context):
    # OPTIONS request (preflight)
    if event.get('httpMethod') == 'OPTIONS':
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "https://boostxchange.d3og0cttbeqb7q.amplifyapp.com",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
                "Access-Control-Allow-Methods": "POST,OPTIONS",
            },
            "body": ""
        }

    # POST logic
    try:
        body = json.loads(event["body"])
        id_token = body.get("idToken")

        if not id_token:
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "https://boostxchange.d3og0cttbeqb7q.amplifyapp.com",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "POST, OPTIONS",
                },
                "body": json.dumps({"error": "Missing idToken"})
            }

        google_user = verify_google_token(id_token)
        email = google_user.get("email")
        name = google_user.get("name")
        picture = google_user.get("picture")

        client, db = get_db()
        users = init_user_collection(db)

        existing = users.find_one({"google_id": google_user["sub"]})
        if not existing:
            register_user(google_user, users)

        jwt_token = create_access_token(
            {"email": email, "name": name},
            expires_delta=timedelta(hours=1)
        )

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "https://boostxchange.d3og0cttbeqb7q.amplifyapp.com",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
            },
            "body": json.dumps({
                "token": jwt_token,
                "user": {
                    "email": email,
                    "name": name,
                    "picture": picture
                }
            })
        }

    except ValueError as ve:
        return {
            "statusCode": 401,
            "headers": {
                "Access-Control-Allow-Origin": "https://boostxchange.d3og0cttbeqb7q.amplifyapp.com",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
            },
            "body": json.dumps({"error": str(ve)})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "https://boostxchange.d3og0cttbeqb7q.amplifyapp.com",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
            },
            "body": json.dumps({"error": f"Internal server error: {str(e)}"})
        }
