# ================================================
# This file will store functions related to
# XML processing and conversion
# ================================================

import datetime
from lxml import etree
from src.utils.constants import cacSchema, cbcSchema


def xml_to_json(xml_string):
    """
    Convert XML string to JSON object

    Args:
        xml_string (str): XML document as a string

    Returns:
        dict: JSON representation of the XML document
    """
    if not xml_string:
        raise ValueError("Empty or null XML input")

    try:
        # Parse XML
        root = etree.fromstring(
            xml_string.encode("utf-8")
            if isinstance(xml_string, str)
            else xml_string
        )

        # Define namespaces for XPath
        namespaces = {"cbc": cbcSchema, "cac": cacSchema}

        # Extract key fields
        result = {}

        # Basic fields
        id_elem = root.find(".//cbc:ID", namespaces)
        if id_elem is not None:
            result["ID"] = id_elem.text

        uuid_elem = root.find(".//cbc:UUID", namespaces)
        if uuid_elem is not None:
            result["UUID"] = uuid_elem.text

        issue_date_elem = root.find(".//cbc:IssueDate", namespaces)
        if issue_date_elem is not None:
            result["IssueDate"] = issue_date_elem.text

        # CopyIndicator (boolean)
        copy_indicator_elem = root.find(".//cbc:CopyIndicator", namespaces)
        if copy_indicator_elem is not None:
            result["CopyIndicator"] = (
                copy_indicator_elem.text.lower() == "true"
            )

        # Status code
        status_code_elem = root.find(".//cbc:DocumentStatusCode", namespaces)
        if status_code_elem is not None:
            result["DocumentStatusCode"] = status_code_elem.text

        # Note
        note_elem = root.find(".//cbc:Note", namespaces)
        if note_elem is not None:
            result["Note"] = note_elem.text

        # Extract customer ID (assuming it's in BuyerReference)
        buyer_ref_elem = root.find(".//cbc:BuyerReference", namespaces)
        if buyer_ref_elem is not None:
            result["CustomerID"] = buyer_ref_elem.text

        # Extract items
        items = []
        line_items = root.findall(".//cac:OrderLine/cac:LineItem", namespaces)

        for i, line_item in enumerate(line_items):
            item = {}

            # Extract item ID
            item_id_path = ".//cac:Item/cac:SellersItemIdentification/cbc:ID"
            item_id_elem = line_item.find(item_id_path, namespaces)
            if item_id_elem is not None:
                item["item_id"] = item_id_elem.text

            # Extract quantity
            quantity_elem = line_item.find(".//cbc:Quantity", namespaces)
            if quantity_elem is not None:
                try:
                    item["quantity"] = float(quantity_elem.text)
                except ValueError:
                    item["quantity"] = 0

            # Extract price
            price_elem = line_item.find(
                ".//cac:Price/cbc:PriceAmount",
                namespaces
            )
            if price_elem is not None:
                try:
                    item["price"] = float(price_elem.text)
                except ValueError:
                    item["price"] = 0

            items.append(item)

        result["Items"] = items

        return result

    except Exception as e:
        raise ValueError(f"Failed to convert XML to JSON: {str(e)}")


def json_to_xml(json_obj, document_type):
    """
    Convert JSON object to XML string

    Args:
        json_obj (dict): JSON object to convert
        document_type (str): Type of document (Order or DespatchAdvice)

    Returns:
        str: XML representation of the JSON object
    """
    if document_type == "DespatchAdvice":
        return json_to_xml_despatch_advice(json_obj)
    elif document_type == "Order":
        return json_to_xml_order(json_obj)
    else:
        raise ValueError(f"Unsupported document type: {document_type}")


def json_to_xml_order(json_obj):
    """
    Convert JSON object to Order XML string

    Args:
        json_obj (dict): JSON object to convert

    Returns:
        str: XML representation of the Order
    """
    # Basic template for Order
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Order xmlns="urn:oasis:names:specification:ubl:schema:xsd:Order-2"
       xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
       xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
    <cbc:ID>{json_obj.get('ID', '')}</cbc:ID>
    <cbc:UUID>{json_obj.get('UUID', '')}</cbc:UUID>
    <cbc:IssueDate>{json_obj.get('IssueDate', '')}</cbc:IssueDate>
    <cbc:BuyerReference>{json_obj.get('CustomerID', '')}</cbc:BuyerReference>
    <cbc:CopyIndicator>{str(json_obj.get('CopyIndicator', False)).
                        lower()}</cbc:CopyIndicator>
    <cbc:DocumentStatusCode>{json_obj.get('DocumentStatusCode',
                                          'NoStatus')}</cbc:DocumentStatusCode>
    <cbc:Note>{json_obj.get('Note', '')}</cbc:Note>"""

    # Add OrderLine sections for each item
    items = json_obj.get("Items", [])
    for item in items:
        xml += f"""
    <cac:OrderLine>
        <cac:LineItem>
            <cbc:Quantity>{item.get('quantity', 0)}</cbc:Quantity>
            <cac:Item>
                <cac:SellersItemIdentification>
                    <cbc:ID>{item.get('item_id', '')}</cbc:ID>
                </cac:SellersItemIdentification>
            </cac:Item>
            <cac:Price>
                <cbc:PriceAmount>{item.get('price', 0)}</cbc:PriceAmount>
            </cac:Price>
        </cac:LineItem>
    </cac:OrderLine>"""

    # Close the root element
    xml += """
</Order>"""

    return xml


def json_to_xml_despatch_advice(json_obj):
    """
    Convert JSON object to DespatchAdvice XML string

    Args:
        json_obj (dict): JSON object to convert

    Returns:
        str: XML representation of the DespatchAdvice
    """
    order_reference = json_obj.get("OrderReference", {})
    supplier_party = json_obj.get("DespatchSupplierParty", {})
    customer_party = json_obj.get("DeliveryCustomerParty", {})

    # Basic template with header information
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<DespatchAdvice
    xmlns="urn:oasis:names:specification:ubl:schema:xsd:DespatchAdvice-2"
                xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
                xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
    <cbc:UBLVersionID>2.0</cbc:UBLVersionID>
    <cbc:CustomizationID>
        urn:oasis:names:specification:ubl:schema:xsd:DespatchAdvice-2.0:sbs-1.0-draft
    </cbc:CustomizationID>
    <cbc:ProfileID>
        bpid:urn:oasis:names:draft:bpss:ubl-2-sbs-despatch-advice-notification-draft
    </cbc:ProfileID>
    <cbc:ID>{json_obj.get('ID', '')}</cbc:ID>
    <cbc:CopyIndicator>{str(json_obj.get('CopyIndicator', False)).
                        lower()}</cbc:CopyIndicator>
    <cbc:UUID>{json_obj.get('UUID', '')}</cbc:UUID>
    <cbc:IssueDate>{json_obj.get('IssueDate', '')}</cbc:IssueDate>
    <cbc:DocumentStatusCode>{json_obj.get('DocumentStatusCode',
                                          'NoStatus')}</cbc:DocumentStatusCode>
    <cbc:DespatchAdviceTypeCode>delivery</cbc:DespatchAdviceTypeCode>
    <cbc:Note>{json_obj.get('Note', '')}</cbc:Note>"""

    # Add OrderReference if available
    if order_reference:
        xml += f"""
    <cac:OrderReference>
        <cbc:ID>{order_reference.get('ID', '')}</cbc:ID>
        <cbc:UUID>{order_reference.get('UUID', '')}</cbc:UUID>
        <cbc:IssueDate>{order_reference.get('IssueDate', '')}</cbc:IssueDate>
    </cac:OrderReference>"""

    # Add DespatchSupplierParty if available
    if supplier_party:
        sp_party = supplier_party.get("Party", {})
        sp_postal = sp_party.get("PostalAddress", {})
        sp_tax = sp_party.get("PartyTaxScheme", {})
        sp_contact = sp_party.get("Contact", {})

        xml += f"""
    <cac:DespatchSupplierParty>
        <cbc:CustomerAssignedAccountID>
            {supplier_party.get('CustomerAssignedAccountID', '')}
        </cbc:CustomerAssignedAccountID>
        <cbc:SupplierAssignedAccountID>
            {supplier_party.get('SupplierAssignedAccountID', '')}
        </cbc:SupplierAssignedAccountID>
        <cac:Party>
            <cbc:PartyName>{sp_party.get('PartyName', '')}</cbc:PartyName>
            <cac:PostalAddress>
                <cbc:StreetName>{sp_postal.
                                 get('StreetName', '')}</cbc:StreetName>
                <cbc:BuildingName>{sp_postal.get('BuildingName',
                                                 '')}</cbc:BuildingName>
                <cbc:BuildingNumber>
                    {sp_postal.get('BuildingNumber', '')}
                </cbc:BuildingNumber>
                <cbc:CityName>{sp_postal.get('CityName', '')}</cbc:CityName>
                "<cbc:PostalZone>"
                f"{sp_postal.get('PostalZone', '')}"
                "</cbc:PostalZone>"
                <cbc:CountrySubentity>
                    {sp_postal.get('CountrySubentity', '')}
                </cbc:CountrySubentity>
                <cac:AddressLine>
                    <cbc:Line>{sp_postal.get('AddressLine', {}).
                               get('Line', '')}</cbc:Line>
                </cac:AddressLine>
                <cac:Country>
                    <cbc:IdentificationCode>
                        {sp_postal.get('Country', {}).
                         get('IdentificationCode', '')}
                    </cbc:IdentificationCode>
                </cac:Country>
            </cac:PostalAddress>
            <cac:PartyTaxScheme>
                <cbc:RegistrationName>
                    {sp_tax.get('RegistrationName', '')}
                </cbc:RegistrationName>
                <cbc:CompanyID>{sp_tax.get('CompanyID', '')}</cbc:CompanyID>
                <cbc:ExemptionReason>
                    {sp_tax.get('ExemptionReason', '')}
                </cbc:ExemptionReason>
                <cac:TaxScheme>
                    <cbc:ID>{sp_tax.get('TaxScheme',
                                        {}).get('ID', '')}</cbc:ID>
                    <cbc:TaxTypeCode>
                        {sp_tax.get('TaxScheme', {}).get('TaxTypeCode', '')}
                    </cbc:TaxTypeCode>
                </cac:TaxScheme>
            </cac:PartyTaxScheme>
            <cac:Contact>
                <cbc:Name>{sp_contact.get('Name', '')}</cbc:Name>
                <cbc:Telephone>{sp_contact.get('Telephone',
                                               '')}</cbc:Telephone>
                <cbc:Telefax>{sp_contact.get('Telefax', '')}</cbc:Telefax>
                <cbc:ElectronicMail>
                    {sp_contact.get('ElectronicMail', '')}
                </cbc:ElectronicMail>
            </cac:Contact>
        </cac:Party>
    </cac:DespatchSupplierParty>"""

    # Add DeliveryCustomerParty if available
    if customer_party:
        cp_party = customer_party.get("Party", {})
        cp_postal = cp_party.get("PostalAddress", {})
        cp_tax = cp_party.get("PartyTaxScheme", {})
        cp_contact = cp_party.get("Contact", {})

        xml += f"""
    <cac:DeliveryCustomerParty>
        <cbc:CustomerAssignedAccountID>
            {customer_party.get('CustomerAssignedAccountID', '')}
        </cbc:CustomerAssignedAccountID>
        <cbc:SupplierAssignedAccountID>
            {customer_party.get('SupplierAssignedAccountID', '')}
        </cbc:SupplierAssignedAccountID>
        <cac:Party>
            <cbc:PartyName>{cp_party.get('PartyName', '')}</cbc:PartyName>
            <cac:PostalAddress>
                <cbc:StreetName>{cp_postal.get('StreetName',
                                               '')}</cbc:StreetName>
                <cbc:BuildingName>{cp_postal.
                                   get('BuildingName', '')}</cbc:BuildingName>
                <cbc:BuildingNumber>
                    {cp_postal.get('BuildingNumber', '')}
                </cbc:BuildingNumber>
                <cbc:CityName>{cp_postal.get('CityName', '')}</cbc:CityName>
                <cbc:PostalZone>{cp_postal.
                                 get('PostalZone', '')}</cbc:PostalZone>
                <cbc:CountrySubentity>
                    {cp_postal.get('CountrySubentity', '')}
                </cbc:CountrySubentity>
                <cac:AddressLine>
                    <cbc:Line>{cp_postal.get('AddressLine', {}).
                               get('Line', '')}</cbc:Line>
                </cac:AddressLine>
                <cac:Country>
                    <cbc:IdentificationCode>
                        {cp_postal.get('Country', {}).
                         get('IdentificationCode', '')}
                    </cbc:IdentificationCode>
                </cac:Country>
            </cac:PostalAddress>
            <cac:PartyTaxScheme>
                <cbc:RegistrationName>
                    {cp_tax.get('RegistrationName', '')}
                </cbc:RegistrationName>
                <cbc:CompanyID>{cp_tax.get('CompanyID', '')}</cbc:CompanyID>
                <cbc:ExemptionReason>
                    {cp_tax.get('ExemptionReason', '')}
                </cbc:ExemptionReason>
                <cac:TaxScheme>
                    <cbc:ID>{cp_tax.get('TaxScheme', {}).
                             get('ID', '')}</cbc:ID>
                    <cbc:TaxTypeCode>
                        {cp_tax.get('TaxScheme', {}).get('TaxTypeCode', '')}
                    </cbc:TaxTypeCode>
                </cac:TaxScheme>
            </cac:PartyTaxScheme>
            <cac:Contact>
                <cbc:Name>{cp_contact.get('Name', '')}</cbc:Name>
                <cbc:Telephone>{cp_contact.get('Telephone',
                                               '')}</cbc:Telephone>
                <cbc:Telefax>{cp_contact.get('Telefax', '')}</cbc:Telefax>
                <cbc:ElectronicMail>
                    {cp_contact.get('ElectronicMail', '')}
                </cbc:ElectronicMail>
            </cac:Contact>
        </cac:Party>
    </cac:DeliveryCustomerParty>"""

    # Add Shipment section if available
    shipment = json_obj.get("Shipment", {})
    if shipment:
        xml += f"""
    <cac:Shipment>
        <cbc:ID>{shipment.get('ID', '')}</cbc:ID>
        <cbc:HandlingCode>{shipment.get('HandlingCode', '')}</cbc:HandlingCode>
        <cbc:GrossWeightMeasure unitCode="{
            shipment.get('GrossWeightMeasure', {}).get('unitCode', '')
        }">{
            shipment.get('GrossWeightMeasure', {}).get('value', '')
        }</cbc:GrossWeightMeasure>
        <cbc:TotalTransportHandlingUnitQuantity>
            {shipment.get('TotalTransportHandlingUnitQuantity', '')}
        </cbc:TotalTransportHandlingUnitQuantity>
    </cac:Shipment>"""

    # Add DespatchLine sections if available
    despatch_lines = json_obj.get("DespatchLine", [])
    for line in despatch_lines:
        item = line.get("Item", {})
        xml += f"""
    <cac:DespatchLine>
        <cbc:ID>{line.get('ID', '')}</cbc:ID>
        <cbc:DeliveredQuantity unitCode="{
            line.get('DeliveredQuantity', {}).get('unitCode', '')
        }">{
            line.get('DeliveredQuantity', {}).get('value', '')
        }</cbc:DeliveredQuantity>
        <cac:OrderLineReference>
            "<cbc:LineID>"
            f"{line.get('OrderLineReference', {}).get('LineID', '')}"
            "</cbc:LineID>"
        </cac:OrderLineReference>
        <cac:Item>
            <cbc:Name>{item.get('Name', '')}</cbc:Name>
            <cac:SellersItemIdentification>
                <cbc:ID>
                    {item.get('SellersItemIdentification', {}).get('ID', '')}
                </cbc:ID>
            </cac:SellersItemIdentification>
        </cac:Item>
    </cac:DespatchLine>"""

    # Close the root element
    xml += """
</DespatchAdvice>"""

    return xml


async def xml_to_pdf(xml_string, file_path=None):
    """
    Convert XML string to PDF document

    Args:
        xml_string (str): XML document as a string
        file_path (str, optional): Path to save the PDF file

    Returns:
        bytes: PDF document as bytes
    """
    from weasyprint import HTML
    import tempfile
    from src.utils.html_formatter import xml_string_to_formatted_html

    # Create an HTML version with nice formatting
    html_content = f"""
    <!DOCTYPE html>
    <html>
        <head>
            <meta charset="UTF-8">
            <title>Despatch Advice Document</title>
            <style>
                @page {{ size: A4; margin: 2cm; }}
                body {{
                    font-family: Arial, sans-serif; margin: 0; padding: 0;
                }}
                .header {{
                    padding: 10px; background-color: #f0f0f0;
                    border-bottom: 1px solid #ddd; margin-bottom: 20px;
                }}
                .header h1 {{ color: #333366; margin: 0; font-size: 24px; }}
                .content {{ padding: 0 20px; }}
                .footer {{
                    padding: 10px; font-size: 10px; text-align: center;
                    margin-top: 30px; border-top: 1px solid #ddd;
                }}
                .xml-code {{ font-family: monospace; white-space: pre-wrap;
                font-size: 11px; overflow-x: auto; }}
                .xml-tag {{ color: #0066aa; }}
                table {{ border-collapse: collapse; width: 100%;
                margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding:
                8px; text-align: left; }}
                th {{ background-color: #f2f2f2; font-weight: bold; }}
                .document-info {{ margin-bottom: 20px; }}
                .document-info p {{ margin: 5px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Despatch Advice</h1>
            </div>
            <div class="content">
                <div class="document-info">
                    <p><strong>Date Generated:</strong>
                        {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    </p>
                    <p><strong>Document Format:</strong>
                        Universal Business Language (UBL)
                    </p>
                </div>
                <div class="xml-content">
                    {xml_string_to_formatted_html(xml_string)}
                </div>
            </div>
            <div class="footer">
                <p>This document was automatically generated.
                    Page <span class="page"></span>
                    of <span class="topage"></span>
                </p>
            </div>
        </body>
    </html>
    """

    # Convert to PDF
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as temp:
        temp_path = temp.name
        temp.write(html_content.encode('utf-8'))
        temp.flush()

    try:
        pdf_document = HTML(temp_path).write_pdf()

        # Save to file if path is provided
        if file_path:
            with open(file_path, 'wb') as f:
                f.write(pdf_document)

        return pdf_document
    finally:
        # Clean up temporary file
        import os
        os.unlink(temp_path)
