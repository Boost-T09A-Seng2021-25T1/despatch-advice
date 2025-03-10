from typing import Union, Dict, List    
from fastapi import FastAPI, HTTPException
import uuid
from datetime import datetime
import requests
from pydantic import BaseModel

app = FastAPI()

# Simulated database
DATABASE = {1, 2, 3, 4, 5}  # Example shipment IDs

# Pydantic models
class Country(BaseModel):
    IdentificationCode: Union[str, None] = None

class DeliveryAddress(BaseModel):
    StreetName: Union[str, None] = None
    BuildingName: Union[str, None] = None
    BuildingNumber: Union[str, None] = None
    CityName: Union[str, None] = None
    PostalZone: Union[str, None] = None
    CountrySubentity: Union[str, None] = None
    AddressLine: Union[str, None] = None
    CountryDetails: Country = Country()

class RequestedDeliveryPeriod(BaseModel):
    StartDate: Union[str, None] = None
    StartTime: Union[str, None] = None
    EndDate: Union[str, None] = None
    EndTime: Union[str, None] = None

class Delivery(BaseModel):
    DeliveryAddress: DeliveryAddress
    RequestedDeliveryPeriod: RequestedDeliveryPeriod

class Consignment(BaseModel):
    ID: int

class Shipment(BaseModel):
    ID: int
    Consignment: Consignment
    Delivery: Delivery

class OrderReference(BaseModel):
    ID: int
    SalesOrderID: int
    UUID: Union[str, None] = None
    IssueDate: Union[str, None] = None

ORDERS_DB = {}
STOCK_DB = {"ITM-001": 100, "ITM-002": 50}
DESPATCH_DB = {}

class OrderItem(BaseModel):
    item_id: str
    quantity: int
    price: float

class Order(BaseModel):
    customer_id: str
    items: List[OrderItem]

class DespatchAdvice(BaseModel):
    order_id: str
    supplier: Dict[str, str]
    customer: Dict[str, str]

class PartyTaxScheme(BaseModel):
    RegistrationName: str
    CompanyId: str
    ExemptionReason: str
    TaxScheme: Dict[str, str]  # {"TaxId": str, "TaxTypeCode": str}

class ContactDetails(BaseModel):
    Name: str
    Telephone: str
    Telefax: str
    Email: str

class FinalizeRequest(BaseModel):
    external_api_url: str
    validate_before_finalizing: bool

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/shipment/{shipment_id}", response_model=Shipment)
def get_shipment(shipment_id: int):
    if shipment_id not in DATABASE:
        raise HTTPException(status_code=404, detail="Shipment ID not found")
    
    shipment = Shipment(
        ID=shipment_id,
        Consignment=Consignment(ID=shipment_id),
        Delivery=Delivery(
            DeliveryAddress=DeliveryAddress(CountryDetails=Country()), 
            RequestedDeliveryPeriod=RequestedDeliveryPeriod()
        )
    )
    
    return shipment

@app.get("/order_reference/{order_id}/{sales_order_id}", response_model=OrderReference)
def get_order_reference(order_id: int, sales_order_id: int):
    order_reference = create_order_reference(order_id, sales_order_id, DATABASE)

    if isinstance(order_reference, dict) and "error" in order_reference:
        raise HTTPException(status_code=400, detail=order_reference["error"])
    
    return order_reference

def create_order_reference(order_id: int, sales_order_id: int, database: set) -> Union[OrderReference, dict]:
    if not isinstance(order_id, int) or not isinstance(sales_order_id, int):
        return {"error": "400 - Invalid data types"}

    if order_id not in database or sales_order_id not in database:
        return {"error": "404 - Order ID or SalesOrderID not found"}

    order_reference = OrderReference(
        ID=order_id,
        SalesOrderID=sales_order_id,
        UUID=str(uuid.uuid4()),
        IssueDate=datetime.now().isoformat()
    )
    
    return order_reference

@app.put("/create_customer_party/{despatch_id}/{customer_assigned_account_id}/{supplier_assigned_account_id}")
def create_customer_party(despatch_id: str, customer_assigned_account_id: str, supplier_assigned_account_id: str):
    data = {
        "CustomerAssignedAccountID": customer_assigned_account_id,
        "SupplierAssignedAccountID": supplier_assigned_account_id,
        "Party": {
            "PartyName": "",
            "PostalAddress": "",
            "PartyTaxScheme": "",
            "Contacts": ""
        }
    }

    url = f'https://api.example.com/v1/despatch/{despatch_id}/createCustomerParty'
    
    try:
        response = requests.put(url, json=data)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(status_code=response.status_code, detail=f"HTTP Error: {http_err}")
    except requests.exceptions.RequestException as req_err:
        raise HTTPException(status_code=500, detail=f"Request Error: {req_err}")

    return {"message": "Customer party created successfully."}

@app.post("/v1/despatch/{despatch_id}/createSupplierSection")
def create_supplier_section(despatch_id: str, sales_order_id: int):
    if sales_order_id not in DATABASE:
        raise HTTPException(status_code=404, detail="404 - SalesOrderID does not exist in database")
    
    data = {
        "CustomerAssignedAccountID": "",  # Needs to be fetched from order functions
        "Party": {
            "PartyName": "",
            "PostalAddress": "",
            "PartyTaxScheme": "",
            "Contacts": ""
        }
    }

    url = f'https://api.example.com/v1/despatch/{despatch_id}/createSupplierSection'
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(status_code=response.status_code, detail=f"HTTP Error: {http_err}")
    except requests.exceptions.RequestException as req_err:
        raise HTTPException(status_code=500, detail=f"Request Error: {req_err}")

    return {"message": "Despatch Supplier Party created successfully."}

@app.put("/v1/despatch/{despatch_id}/createDespatchLine")
def create_despatch_line(despatch_id: str, delivered_quantity: int, quantity: int):
    backorder_quantity = quantity - delivered_quantity
    line_status_code = "Completed" if backorder_quantity == 0 else "Revised"
    backorder_reason = "" if backorder_quantity == 0 else "User-specified reason"

    data = {
        "Note": "",
        "LineStatusCode": line_status_code,
        "BackorderReason": backorder_reason,
        "OrderLineReference": "",
        "Item": "",
        "DeliveredQuantity": delivered_quantity,
        "BackorderQuantity": backorder_quantity
    }
    
    return {"message": "Despatch Line created successfully.", "data": data}
@app.post("/v1/order/create")
def create_order(order: Order):
    order_id = str(uuid.uuid4())[:8]  # Simulated order ID
    ORDERS_DB[order_id] = order.dict()
    return {"order_id": order_id, "status": "Order Created"}

@app.get("/v1/order/validate/{order_id}")
def validate_order(order_id: str):
    if order_id not in ORDERS_DB:
        raise HTTPException(status_code=404, detail="Order does not exist.")
    return {"order_id": order_id, "validation_status": "Valid"}

@app.get("/v1/stock/check/{order_id}")
def check_stock(order_id: str):
    if order_id not in ORDERS_DB:
        raise HTTPException(status_code=404, detail="Stock data missing.")
    order = ORDERS_DB[order_id]
    stock_status = []
    for item in order["items"]:
        available_quantity = STOCK_DB.get(item["item_id"], 0)
        status = "Available" if item["quantity"] <= available_quantity else "Insufficient Stock"
        stock_status.append({
            "item_id": item["item_id"],
            "requested_quantity": item["quantity"],
            "available_quantity": available_quantity,
            "unit": "pcs",
            "status": status
        })
    return {"order_id": order_id, "stock_status": stock_status}

@app.get("/v1/order/{order_id}")
def fetch_order(order_id: str):
    if order_id not in ORDERS_DB:
        raise HTTPException(status_code=404, detail="Order does not exist.")
    return {"order_id": order_id, **ORDERS_DB[order_id]}

@app.post("/v1/despatch")
def create_despatch_advice(despatch: DespatchAdvice):
    despatch_id = f"D-{str(uuid.uuid4())[:6]}"
    if despatch.order_id in DESPATCH_DB:
        raise HTTPException(status_code=409, detail="Despatch Advice already exists.")
    DESPATCH_DB[despatch_id] = despatch.dict()
    return {"despatch_id": despatch_id, "status": "Initiated", "xml_link": f"/despatch/{despatch_id}"}

@app.get("/v1/despatch/validate/{despatchId}")
def validate_despatch(despatchId: str):
    if despatchId not in DESPATCH_DB:
        raise HTTPException(status_code=404, detail="No Despatch Advice found.")
    return {"despatch_id": despatchId, "validation_status": "Valid"}

@app.get("/v1/despatch/{despatchId}")
def retrieve_despatch_xml(despatchId: str):
    if despatchId not in DESPATCH_DB:
        raise HTTPException(status_code=404, detail="No Despatch Advice found.")
    return f"""<DespatchAdvice><cbc:ID>{despatchId}</cbc:ID><cbc:IssueDate>{datetime.now().date()}</cbc:IssueDate></DespatchAdvice>"""

@app.put("/v1/despatch/{despatchId}")
def update_despatch(despatchId: str, update_data: Dict[str, str]):
    if despatchId not in DESPATCH_DB:
        raise HTTPException(status_code=404, detail="No Despatch Advice found.")
    DESPATCH_DB[despatchId].update(update_data)
    return {"despatch_id": despatchId, "status": "Updated"}

@app.delete("/v1/despatch/{despatchId}")
def delete_despatch(despatchId: str):
    if despatchId not in DESPATCH_DB:
        raise HTTPException(status_code=404, detail="No Despatch Advice found.")
    del DESPATCH_DB[despatchId]
    return {"despatch_id": despatchId, "status": "Deleted"}

@app.put("/v1/despatch/{despatchId}/supplierParty/postalAddress")
def update_postal_address(despatchId: int, salesOrderId: int, address: DeliveryAddress):
    if despatchId not in DATABASE or salesOrderId not in DATABASE:
        raise HTTPException(status_code=404, detail="SalesOrderId or DespatchId invalid")
    return {"despatch_id": despatchId, "status": "Postal Address Updated"}

@app.put("/v1/despatch/{despatchId}/supplierParty/partytaxScheme")
def update_party_tax_scheme(despatchId: int, salesOrderId: int, tax_scheme: PartyTaxScheme):
    if despatchId not in DATABASE or salesOrderId not in DATABASE:
        raise HTTPException(status_code=404, detail="SalesOrderId or DespatchId invalid")
    return {"despatch_id": despatchId, "status": "Party Tax Scheme Updated"}

@app.put("/v1/despatch/{despatchId}/supplierParty/contacts")
def update_contact_details(despatchId: int, salesOrderId: int, contacts: ContactDetails):
    if despatchId not in DATABASE or salesOrderId not in DATABASE:
        raise HTTPException(status_code=404, detail="SalesOrderId or DespatchId invalid")
    return {"despatch_id": despatchId, "status": "Contact Details Updated"}

@app.put("/v1/despatch/{despatchId}/customerParty/postalAddress")
def update_customer_postal_address(despatchId: int, address: DeliveryAddress):
    if despatchId not in DATABASE:
        raise HTTPException(status_code=404, detail="DespatchId invalid")
    return {"despatch_id": despatchId, "status": "Customer Postal Address Updated"}

@app.put("/v1/despatch/{despatchId}/customerParty/partytaxScheme")
def update_customer_party_tax_scheme(despatchId: int, tax_scheme: PartyTaxScheme):
    if despatchId not in DATABASE:
        raise HTTPException(status_code=404, detail="DespatchId invalid")
    return {"despatch_id": despatchId, "status": "Customer Party Tax Scheme Updated"}

@app.put("/v1/despatch/{despatchId}/customerParty/contacts")
def update_customer_contact_details(despatchId: int, contacts: ContactDetails):
    if despatchId not in DATABASE:
        raise HTTPException(status_code=404, detail="DespatchId invalid")
    return {"despatch_id": despatchId, "status": "Customer Contact Details Updated"}

@app.put("/v1/despatch/{despatchId}/DespatchLine/OrderLineReference")
def update_order_line_reference(despatchId: int):
    if despatchId not in DATABASE:
        raise HTTPException(status_code=404, detail="DespatchId invalid")
    return {"despatch_id": despatchId, "status": "Order Line Reference Updated"}

@app.put("/v1/despatch/{despatchId}/DespatchLine/Item")
def update_item_details(despatchId: int):
    if despatchId not in DATABASE:
        raise HTTPException(status_code=404, detail="DespatchId invalid")
    return {"despatch_id": despatchId, "status": "Item Details Updated"}

@app.delete("/v1/despatch/{despatchId}/DespatchLine/{Id}")
def delete_despatch_line(despatchId: int, Id: int):
    if despatchId not in DATABASE:
        raise HTTPException(status_code=404, detail="DespatchId invalid")
    return {"despatch_id": despatchId, "despatch_line_id": Id, "status": "Despatch Line Deleted"}

@app.put("/v1/despatch/{despatchId}/DespatchLine/{Id}")
def update_despatch_line(despatchId: int, Id: int):
    if despatchId not in DATABASE:
        raise HTTPException(status_code=404, detail="DespatchId invalid")
    return {"despatch_id": despatchId, "despatch_line_id": Id, "status": "Despatch Line Updated"}

@app.get("/v1/despatch/{despatchId}/DespatchLine")
def get_all_despatch_lines(despatchId: int):
    if despatchId not in DATABASE:
        raise HTTPException(status_code=404, detail="DespatchId invalid")
    return {"despatch_id": despatchId, "status": "Despatch Lines Retrieved"}

@app.get("/v1/despatch/{despatchId}/DespatchLine/{Id}")
def get_despatch_line(despatchId: int, Id: int):
    if despatchId not in DATABASE:
        raise HTTPException(status_code=404, detail="DespatchId invalid")
    return {"despatch_id": despatchId, "despatch_line_id": Id, "status": "Despatch Line Retrieved"}

@app.get("/v1/despatch/{despatchId}/createPdf")
def generate_pdf(despatchId: int):
    if despatchId not in DATABASE:
        raise HTTPException(status_code=404, detail="DespatchId invalid")
    return {"despatch_id": despatchId, "status": "PDF Generated"}

@app.post("/v1/despatch/{despatchId}/finalize")
def finalize_despatch(despatchId: int, request: FinalizeRequest):
    if despatchId not in DATABASE:
        raise HTTPException(status_code=404, detail="No Despatch Advice found with the given ID")
    return {"despatch_id": despatchId, "status": "Finalized", "final_xml_link": f"/despatch/{despatchId}/final"}

@app.post("/v1/despatch/{despatchId}/generatePDF")
def generate_pdf(despatchId: int):
    if despatchId not in DATABASE:
        raise HTTPException(status_code=404, detail="No finalized Despatch Advice found")
    return {"despatch_id": despatchId, "pdf_download_link": f"/despatch/{despatchId}/pdf"}

@app.get("/v1/despatch/{despatchId}/sendDocuments")
def send_documents(despatchId: int):
    if despatchId not in DATABASE:
        raise HTTPException(status_code=404, detail="No finalized Despatch Advice found")
    return {"despatch_id": despatchId, "emailStatus": "STATUS_SUCCESS(200)"}