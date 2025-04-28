import json
from xml.dom.minidom import parseString
import xml.etree.ElementTree as ET


# certain parts of this file were written with ai assistance

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
    "Access-Control-Allow-Headers": "Content-Type"
}


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        order_xml = body.get("xmlDoc", "")

        if not order_xml:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Missing 'xmlDoc' in request"})
            }

        return convert_order_to_despatch(order_xml)

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": f"Server error: {str(e)}"})
        }


def convert_order_to_despatch(order_xml: str) -> dict:
    try:
        root = ET.fromstring(order_xml)

        ns = {
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            '': 'urn:oasis:names:specification:ubl:schema:xsd:Order-2'
        }

        def find_text(xpath):
            elem = root.find(xpath, ns)
            return elem.text.strip() if elem is not None and elem.text else ""

        def find_nested_text(base_elem, xpath):
            if base_elem is None:
                return ""
            elem = base_elem.find(xpath, ns)
            return elem.text.strip() if elem is not None and elem.text else ""

        # Extract top level Order fields
        order_id = find_text('.//cbc:ID')
        sales_order_id = find_text('.//cbc:SalesOrderID') or "CON-DEFAULT"
        uuid = find_text('.//cbc:UUID') or "UUID-GENERATED"
        issue_date = find_text('.//cbc:IssueDate')
        note = find_text('.//cbc:Note') or "Auto-generated Despatch"
        buyer_reference = find_text('.//cbc:BuyerReference')

        # Extract Supplier and Customer Info
        supplier_party = root.find('.//cac:SellerSupplierParty/cac:Party', ns)
        customer_party = root.find('.//cac:BuyerCustomerParty/cac:Party', ns)

        def extract_party(party_elem, fallback_name):
            if party_elem is None:
                return {
                    "name": fallback_name,
                    "street": "Unknown Street",
                    "building_name": "",
                    "building_number": "",
                    "city": "Unknown City",
                    "postal_zone": "0000",
                    "subentity": "",
                    "country_code": "US"
                }

            postal = party_elem.find('.//cac:PostalAddress', ns)
            return {
                "name": find_nested_text(party_elem, './/cac:PartyName/cbc:Name') or fallback_name,
                "street": find_nested_text(postal, './/cbc:StreetName') or "Unknown Street",
                "building_name": find_nested_text(postal, './/cbc:BuildingName') or "",
                "building_number": find_nested_text(postal, './/cbc:BuildingNumber') or "",
                "city": find_nested_text(postal, './/cbc:CityName') or "Unknown City",
                "postal_zone": find_nested_text(postal, './/cbc:PostalZone') or "0000",
                "subentity": find_nested_text(postal, './/cbc:CountrySubentity') or "",
                "country_code": find_nested_text(postal, './/cac:Country/cbc:IdentificationCode') or "US"
            }

        supplier_info = extract_party(supplier_party, "Supplier")
        customer_info = extract_party(customer_party, "Customer")

        despatch_lines = ""

        line_items = root.findall('.//cac:OrderLine', ns)
        for idx, item in enumerate(line_items, start=1):
            item_name = find_nested_text(item, './/cac:Item/cbc:Name') or f"Item {idx}"
            sellers_item_id = find_nested_text(item, './/cac:Item/cac:SellersItemIdentification/cbc:ID') or f"S-{idx}"
            buyers_item_id = find_nested_text(item, './/cac:Item/cac:BuyersItemIdentification/cbc:ID') or f"B-{idx}"
            quantity = find_nested_text(item, './/cac:LineItem/cbc:Quantity') or "1"

            despatch_lines += f"""
    <cac:DespatchLine>
      <cbc:ID>{idx}</cbc:ID>
      <cbc:Note>Auto-generated note</cbc:Note>
      <cbc:LineStatusCode>NoStatus</cbc:LineStatusCode>
      <cbc:DeliveredQuantity unitCode="KGM">{quantity}</cbc:DeliveredQuantity>
      <cbc:BackorderQuantity unitCode="KGM">0</cbc:BackorderQuantity>
      <cbc:BackorderReason>None</cbc:BackorderReason>
      <cac:OrderLineReference>
        <cbc:LineID>{idx}</cbc:LineID>
        <cbc:SalesOrderLineID>A</cbc:SalesOrderLineID>
        <cac:OrderReference>
          <cbc:ID>{order_id}</cbc:ID>
          <cbc:SalesOrderID>{sales_order_id}</cbc:SalesOrderID>
          <cbc:UUID>{uuid}</cbc:UUID>
          <cbc:IssueDate>{issue_date}</cbc:IssueDate>
        </cac:OrderReference>
      </cac:OrderLineReference>
      <cac:Item>
        <cbc:Description>Auto-generated Description</cbc:Description>
        <cbc:Name>{item_name}</cbc:Name>
        <cac:BuyersItemIdentification>
          <cbc:ID>{buyers_item_id}</cbc:ID>
        </cac:BuyersItemIdentification>
        <cac:SellersItemIdentification>
          <cbc:ID>{sellers_item_id}</cbc:ID>
        </cac:SellersItemIdentification>
      </cac:Item>
    </cac:DespatchLine>"""

        despatch_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<DespatchAdvice xmlns="urn:oasis:names:specification:ubl:schema:xsd:DespatchAdvice-2"
                xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
                xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
  <cbc:ID>{order_id}</cbc:ID>
  <cbc:UUID>{uuid}</cbc:UUID>
  <cbc:IssueDate>{issue_date}</cbc:IssueDate>
  <cbc:Note>{note}</cbc:Note>

  <cac:OrderReference>
    <cbc:ID>{order_id}</cbc:ID>
    <cbc:SalesOrderID>{sales_order_id}</cbc:SalesOrderID>
    <cbc:UUID>{uuid}</cbc:UUID>
    <cbc:IssueDate>{issue_date}</cbc:IssueDate>
  </cac:OrderReference>

  <cac:DespatchSupplierParty>
    <cbc:CustomerAssignedAccountID>SUPP-001</cbc:CustomerAssignedAccountID>
    <cac:Party>
      <cac:PartyName><cbc:Name>{supplier_info["name"]}</cbc:Name></cac:PartyName>
      <cac:PostalAddress>
        <cbc:StreetName>{supplier_info["street"]}</cbc:StreetName>
        <cbc:BuildingName>{supplier_info["building_name"]}</cbc:BuildingName>
        <cbc:BuildingNumber>{supplier_info["building_number"]}</cbc:BuildingNumber>
        <cbc:CityName>{supplier_info["city"]}</cbc:CityName>
        <cbc:PostalZone>{supplier_info["postal_zone"]}</cbc:PostalZone>
        <cbc:CountrySubentity>{supplier_info["subentity"]}</cbc:CountrySubentity>
        <cac:AddressLine><cbc:Line>Main Office</cbc:Line></cac:AddressLine>
        <cac:Country><cbc:IdentificationCode>{supplier_info["country_code"]}</cbc:IdentificationCode></cac:Country>
      </cac:PostalAddress>
    </cac:Party>
  </cac:DespatchSupplierParty>

  <cac:DeliveryCustomerParty>
    <cbc:CustomerAssignedAccountID>CUST-001</cbc:CustomerAssignedAccountID>
    <cbc:SupplierAssignedAccountID>SUP-001</cbc:SupplierAssignedAccountID>
    <cac:Party>
      <cac:PartyName><cbc:Name>{customer_info["name"]}</cbc:Name></cac:PartyName>
      <cac:PostalAddress>
        <cbc:StreetName>{customer_info["street"]}</cbc:StreetName>
        <cbc:BuildingName>{customer_info["building_name"]}</cbc:BuildingName>
        <cbc:BuildingNumber>{customer_info["building_number"]}</cbc:BuildingNumber>
        <cbc:CityName>{customer_info["city"]}</cbc:CityName>
        <cbc:PostalZone>{customer_info["postal_zone"]}</cbc:PostalZone>
        <cbc:CountrySubentity>{customer_info["subentity"]}</cbc:CountrySubentity>
        <cac:AddressLine><cbc:Line>Main Office</cbc:Line></cac:AddressLine>
        <cac:Country><cbc:IdentificationCode>{customer_info["country_code"]}</cbc:IdentificationCode></cac:Country>
      </cac:PostalAddress>
    </cac:Party>
  </cac:DeliveryCustomerParty>

  <cac:Shipment>
    <cbc:ID>1</cbc:ID>
    <cac:Consignment><cbc:ID>1</cbc:ID></cac:Consignment>
    <cac:Delivery>
      <cac:DeliveryAddress>
        <cbc:StreetName>{customer_info["street"]}</cbc:StreetName>
        <cbc:BuildingName>{customer_info["building_name"]}</cbc:BuildingName>
        <cbc:BuildingNumber>{customer_info["building_number"]}</cbc:BuildingNumber>
        <cbc:CityName>{customer_info["city"]}</cbc:CityName>
        <cbc:PostalZone>{customer_info["postal_zone"]}</cbc:PostalZone>
        <cbc:CountrySubentity>{customer_info["subentity"]}</cbc:CountrySubentity>
        <cac:AddressLine><cbc:Line>Main Office</cbc:Line></cac:AddressLine>
        <cac:Country><cbc:IdentificationCode>{customer_info["country_code"]}</cbc:IdentificationCode></cac:Country>
      </cac:DeliveryAddress>
      <cac:RequestedDeliveryPeriod>
        <cbc:StartDate>{issue_date}</cbc:StartDate>
        <cbc:StartTime>09:00:00Z</cbc:StartTime>
        <cbc:EndDate>{issue_date}</cbc:EndDate>
        <cbc:EndTime>17:00:00Z</cbc:EndTime>
      </cac:RequestedDeliveryPeriod>
    </cac:Delivery>
  </cac:Shipment>

  {despatch_lines}
</DespatchAdvice>"""

        pretty_xml = parseString(despatch_xml).toprettyxml(indent="  ")

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "despatch_xml": pretty_xml,
                "summary": {
                    "ID": order_id,
                    "UUID": uuid,
                    "IssueDate": issue_date,
                    "Note": note,
                    "CustomerID": buyer_reference
                }
            })
        }

    except Exception as e:
        return {
            "statusCode": 400,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": f"Invalid XML or conversion failed: {str(e)}"})
        }
