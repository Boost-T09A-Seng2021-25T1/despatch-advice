from lxml import etree
import json
from src.utils.constants import cacSchema, cbcSchema
import os

# ================================================
# This file will store functions related to
# creating the final despatch advice.
# ================================================


dirPath = os.path.abspath(os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..")))


def xml_to_json(xml_string):
    """
    Convert XML string to JSON object
    Args:
        xml_string (str): XML document as a string
    
    Returns:
        dict: JSON representation of the XML document
    """
    try:
        # Parse XML
        root = etree.fromstring(xml_string.encode('utf-8') if isinstance(xml_string, str) else xml_string)
        
        # Define namespaces for XPath
        namespaces = {
            'cbc': cbcSchema,
            'cac': cacSchema
        }
        
        # Extract key fields
        result = {}
        
        # Basic fields
        id_elem = root.find('.//cbc:ID', namespaces)
        if id_elem is not None:
            result['ID'] = id_elem.text
        
        uuid_elem = root.find('.//cbc:UUID', namespaces)
        if uuid_elem is not None:
            result['UUID'] = uuid_elem.text
        
        issue_date_elem = root.find('.//cbc:IssueDate', namespaces)
        if issue_date_elem is not None:
            result['IssueDate'] = issue_date_elem.text
        
        # CopyIndicator (boolean)
        copy_indicator_elem = root.find('.//cbc:CopyIndicator', namespaces)
        if copy_indicator_elem is not None:
            result['CopyIndicator'] = copy_indicator_elem.text.lower() == 'true'
        
        # Status code
        status_code_elem = root.find('.//cbc:DocumentStatusCode', namespaces)
        if status_code_elem is not None:
            result['DocumentStatusCode'] = status_code_elem.text
        
        # Note
        note_elem = root.find('.//cbc:Note', namespaces)
        if note_elem is not None:
            result['Note'] = note_elem.text
        
        # Extract customer ID (assuming it's in BuyerReference)
        buyer_ref_elem = root.find('.//cbc:BuyerReference', namespaces)
        if buyer_ref_elem is not None:
            result['CustomerID'] = buyer_ref_elem.text
        
        # Extract items
        items = []
        line_items = root.findall('.//cac:OrderLine/cac:LineItem', namespaces)
        
        for i, line_item in enumerate(line_items):
            item = {}
            
            # Extract item ID
            item_id_elem = line_item.find('.//cac:Item/cac:SellersItemIdentification/cbc:ID', namespaces)
            if item_id_elem is not None:
                item['item_id'] = item_id_elem.text
            
            # Extract quantity
            quantity_elem = line_item.find('.//cbc:Quantity', namespaces)
            if quantity_elem is not None:
                try:
                    item['quantity'] = float(quantity_elem.text)
                except ValueError:
                    item['quantity'] = 0
            
            # Extract price
            price_elem = line_item.find('.//cac:Price/cbc:PriceAmount', namespaces)
            if price_elem is not None:
                try:
                    item['price'] = float(price_elem.text)
                except ValueError:
                    item['price'] = 0
            
            items.append(item)
        
        result['Items'] = items
        
        return result
        
    except Exception as e:
        raise ValueError(f"Failed to convert XML to JSON: {str(e)}")

def json_to_xml(json_obj, document_type="Order"):
    """
    Convert JSON object to XML string
    
    Args:
        json_obj (dict): JSON object
        document_type (str): Type of UBL document ("Order" or "DespatchAdvice")
    
    Returns:
        str: XML representation of the JSON object
    """
    # This is a placeholder for the reverse conversion
    # In a real implementation, you would build the XML structure based on the JSON data
    # This is a complex task that would require detailed mapping of all fields
    
    if document_type == "Order":
        # Sample Order XML template
        xml_template = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Order xmlns="urn:oasis:names:specification:ubl:schema:xsd:Order-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
        <cbc:UBLVersionID>2.0</cbc:UBLVersionID>
        <cbc:CustomizationID>urn:oasis:names:specification:ubl:xpath:Order-2.0:sbs-1.0-draft</cbc:CustomizationID>
        <cbc:ProfileID>bpid:urn:oasis:names:draft:bpss:ubl-2-sbs-order-with-simple-response-draft</cbc:ProfileID>
        <cbc:ID>{json_obj.get('ID', '')}</cbc:ID>
        <cbc:CopyIndicator>{str(json_obj.get('CopyIndicator', False)).lower()}</cbc:CopyIndicator>
        <cbc:UUID>{json_obj.get('UUID', '')}</cbc:UUID>
        <cbc:IssueDate>{json_obj.get('IssueDate', '')}</cbc:IssueDate>
        <cbc:Note>{json_obj.get('Note', '')}</cbc:Note>
    </Order>"""
        return xml_template
    
    elif document_type == "DespatchAdvice":
        # Sample DespatchAdvice XML template
        xml_template = f"""<?xml version="1.0" encoding="UTF-8"?>
    <DespatchAdvice xmlns="urn:oasis:names:specification:ubl:schema:xsd:DespatchAdvice-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
        <cbc:UBLVersionID>2.0</cbc:UBLVersionID>
        <cbc:CustomizationID>urn:oasis:names:specification:ubl:xpath:DespatchAdvice-2.0:sbs-1.0-draft</cbc:CustomizationID>
        <cbc:ProfileID>bpid:urn:oasis:names:draft:bpss:ubl-2-sbs-despatch-advice-notification-draft</cbc:ProfileID>
        <cbc:ID>{json_obj.get('ID', '')}</cbc:ID>
        <cbc:CopyIndicator>{str(json_obj.get('CopyIndicator', False)).lower()}</cbc:CopyIndicator>
        <cbc:UUID>{json_obj.get('UUID', '')}</cbc:UUID>
        <cbc:IssueDate>{json_obj.get('IssueDate', '')}</cbc:IssueDate>
        <cbc:DocumentStatusCode>{json_obj.get('DocumentStatusCode', 'NoStatus')}</cbc:DocumentStatusCode>
        <cbc:DespatchAdviceTypeCode>delivery</cbc:DespatchAdviceTypeCode>
        <cbc:Note>{json_obj.get('Note', '')}</cbc:Note>
    </DespatchAdvice>"""
        return xml_template
    
    else:
        raise ValueError(f"Unsupported document type: {document_type}")
