import datetime
import json
import uuid

from lxml import etree

from src.mongodb import (
    addOrder,
    dbConnect,
    deleteDocument,
    getOrderInfo,
    updateDocument,
)

async def addDespatchAdvice(data):
    """Add a despatch advice document to the database"""
    try:
        client, db = await dbConnect()
        result = await addOrder(data, db)
        client.close()
        return result
    except Exception as error:
        print(f"MongoDB request failed: {error}")
        return None


async def getDespatchAdvice(despatchId):
    """Get a despatch advice document by ID"""
    try:
        client, db = await dbConnect()
        result = await getOrderInfo(despatchId, db)
        client.close()
        return result
    except Exception as error:
        print(f"MongoDB fetch failed: {error}")
        return None


def generate_initial_xml(despatch_id, issue_date):
    """
    Generate initial XML template for Despatch Advice

    Args:
        despatch_id: The ID of the despatch advice
        issue_date: The issue date in ISO format

    Returns:
        str: XML string for the initial despatch advice
    """
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<DespatchAdvice xmlns="urn:oasis:names:specification:ubl:schema:xsd:DespatchAdvice-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
    <cbc:UBLVersionID>2.0</cbc:UBLVersionID>
    <cbc:CustomizationID>urn:oasis:names:specification:ubl:schema:xsd:DespatchAdvice-2.0:sbs-1.0-draft</cbc:CustomizationID>
    <cbc:ProfileID>bpid:oasis:names:draft:bpss:ubl-2-sbs-despatch-advice-notification-draft</cbc:ProfileID>
    <cbc:ID>{despatch_id}</cbc:ID>
    <cbc:CopyIndicator>false</cbc:CopyIndicator>
    <cbc:UUID>{uuid.uuid4()}</cbc:UUID>
    <cbc:IssueDate>{issue_date}</cbc:IssueDate>
    <cbc:DocumentStatusCode>NoStatus</cbc:DocumentStatusCode>
    <cbc:DespatchAdviceTypeCode>delivery</cbc:DespatchAdviceTypeCode>
    <cbc:Note>Generated by Despatch Advice Generator</cbc:Note>
</DespatchAdvice>"""


async def create_despatch_advice(event_body):
    """
    Create a new despatch advice document

    Args:
        event_body (dict): The JSON body of the request containing order_id, supplier, and customer

    Returns:
        dict: Response containing despatch_id, status, and xml_link
    """
    try:
        body = event_body

        if "order_id" not in body:
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {"error": "Invalid request format: missing order_id"}
                ),
            }

        order_id = body["order_id"]

        client, db = await dbConnect()
        try:
            order = await getOrderInfo(order_id, db)

            if not order:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "Order does not exist"}),
                }

            despatch_id = f"D-{uuid.uuid4().hex[:8].upper()}"
            despatch_uuid = str(uuid.uuid4())
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            xml_content = generate_initial_xml(despatch_id, current_date)

            supplier_info = body.get("supplier", {})
            customer_info = body.get("customer", {})

            despatch_data = {
                "DespatchID": despatch_id,
                "UUID": despatch_uuid,
                "OrderID": order_id,
                "Status": "Initiated",
                "SupplierInfo": supplier_info,
                "CustomerInfo": customer_info,
                "CreationDate": current_date,
                "XMLData": xml_content,
                "LastModified": datetime.datetime.now().isoformat(),
            }

            # We should use a specific function for despatch collection when available
            inserted_id = await addDespatchAdvice(despatch_data)

            if not inserted_id:
                return {
                    "statusCode": 500,
                    "body": json.dumps(
                        {"error": "Failed to create despatch advice"}
                    ),
                }

            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "despatch_id": despatch_id,
                        "status": "Initiated",
                        "xml_link": f"/v1/despatch/{despatch_id}",
                    }
                ),
            }
        finally:
            client.close()

    except Exception as e:
        print(f"Error creating despatch advice: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Server error: {str(e)}"}),
        }


async def validate_despatch_advice(despatch_id):
    """
    Validate a despatch advice document

    Args:
        despatch_id (str): The ID of the despatch advice to validate

    Returns:
        dict: Response containing validation status
    """
    try:
        despatch = await getDespatchAdvice(despatch_id)

        if not despatch:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Despatch Advice not found"}),
            }

        xml_data = despatch.get("XMLData", "")

        validation_issues = []

        try:
            root = etree.fromstring(xml_data.encode("utf-8"))

            required_elements = [".//cbc:ID", ".//cbc:IssueDate"]

            recommended_elements = [
                ".//cac:DespatchSupplierParty",
                ".//cac:DeliveryCustomerParty",
                ".//cac:Shipment",
            ]

            namespaces = {
                "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
                "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
            }

            for xpath in required_elements:
                if not root.findall(xpath, namespaces):
                    element_name = xpath.split(":")[-1]
                    validation_issues.append(
                        f"Missing required element: {element_name}"
                    )

            warnings = []
            for xpath in recommended_elements:
                if not root.findall(xpath, namespaces):
                    element_name = xpath.split(":")[-1]
                    warnings.append(
                        f"Missing recommended element: {element_name}"
                    )

        except etree.XMLSyntaxError as e:
            validation_issues.append(f"XML syntax error: {str(e)}")

        response = {
            "despatch_id": despatch.get("DespatchID"),
            "validation_status": "Invalid" if validation_issues else "Valid",
        }

        if validation_issues:
            response["issues"] = validation_issues

        if warnings and not validation_issues:
            response["warnings"] = warnings

        return {"statusCode": 200, "body": json.dumps(response)}

    except Exception as e:
        print(f"Error validating despatch advice: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Server error: {str(e)}"}),
        }


async def get_despatch_xml(despatch_id):
    """
    Retrieve the generated Despatch Advice XML

    Args:
        despatch_id (str): The ID of the despatch advice to retrieve

    Returns:
        dict: Response containing XML content
    """
    try:
        despatch = await getDespatchAdvice(despatch_id)

        if not despatch:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Despatch Advice not found"}),
            }

        xml_data = despatch.get("XMLData", "")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/xml"},
            "body": xml_data,
        }

    except Exception as e:
        print(f"Error retrieving despatch XML: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Server error: {str(e)}"}),
        }


async def update_despatch_advice(despatch_id, event_body):
    """
    Update a despatch advice document

    Args:
        despatch_id (str): The ID of the despatch advice to update
        event_body (dict): The JSON body of the request containing XML updates

    Returns:
        dict: Response containing update status
    """
    try:
        body = event_body

        if "xml" not in body:
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {"error": "Invalid request format: missing xml field"}
                ),
            }

        client, db = await dbConnect()

        try:
            # Get the existing despatch
            despatch = await getOrderInfo(despatch_id, db.despatches)

            if not despatch:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "Despatch Advice not found"}),
                }

            # Validate the XML
            try:
                etree.fromstring(body["xml"].encode("utf-8"))
            except etree.XMLSyntaxError as e:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": f"Invalid XML: {str(e)}"}),
                }

            # Update the despatch document with the new XML data
            update_data = {
                "XMLData": body["xml"],
                "LastModified": datetime.datetime.now().isoformat(),
            }

            # If status is provided, update it too
            if "status" in body:
                update_data["Status"] = body["status"]

            # Perform the update operation in the database
            updated = await updateDocument(despatch_id, update_data, db)

            if not updated:
                return {
                    "statusCode": 500,
                    "body": json.dumps(
                        {"error": "Failed to update despatch advice"}
                    ),
                }

            return {
                "statusCode": 200,
                "body": json.dumps(
                    {"despatch_id": despatch_id, "status": "Updated"}
                ),
            }

        finally:
            client.close()

    except Exception as e:
        print(f"Error updating despatch advice: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Server error: {str(e)}"}),
        }


async def delete_despatch_advice(despatch_id):
    """
    Delete a despatch advice document

    Args:
        despatch_id (str): The ID of the despatch advice to delete

    Returns:
        dict: Response containing deletion status
    """
    try:
        client, db = await dbConnect()

        try:
            # Get the existing despatch to verify it exists
            despatch = await getOrderInfo(despatch_id, db.despatches)

            if not despatch:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "Despatch Advice not found"}),
                }

            # Perform the delete operation in the database
            deleted = await deleteDocument(despatch_id, db)

            if not deleted:
                return {
                    "statusCode": 500,
                    "body": json.dumps(
                        {"error": "Failed to delete despatch advice"}
                    ),
                }

            return {
                "statusCode": 200,
                "body": json.dumps(
                    {"despatch_id": despatch_id, "status": "Deleted"}
                ),
            }

        finally:
            client.close()

    except Exception as e:
        print(f"Error deleting despatch advice: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Server error: {str(e)}"}),
        }
