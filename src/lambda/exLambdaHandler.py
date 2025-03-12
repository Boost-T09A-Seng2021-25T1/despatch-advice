import json
from src.mongodb import collection
from src.utils.constants import STATUS_SUCCESS, STATUS_BAD_REQ


# this handles AWS Gateway API reqs
def handler(event):

    # draft post method
    if event["httpMethod"] == "POST":
        body = json.loads(event["body"])

        # save data
        collection.insert(body)

        return {
            "statusCode": STATUS_SUCCESS,
            "body": json.dumps(
                {
                    "temp": "TEMP DATA INSERTED"
                }
            )
        }

    # draft get method
    elif event["httpMethod"] == "GET":
        data = list(collection.find(
            {},
            # example, except id.
            {"_id": 0}
        ))

        return {
            "statusCode": STATUS_SUCCESS,
            "body": json.dumps(data)
        }

    # draft everything else to be implemented
    return {
        "statusCode": STATUS_BAD_REQ,
        "body": json.dumps({
            "error": "invalid request"
        })
    }
