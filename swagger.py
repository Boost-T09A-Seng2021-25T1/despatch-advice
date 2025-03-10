from typing import Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid

app = FastAPI()

# To check it within local web browser, type "uvicorn swagger:app --reload",
# then copy the link and add "/docs" at the end of it.

# Add the root route here
@app.get("/")
def read_root():
    return {"message": "To get swagger file, add '/docs' at the end of the url"}

# Data Models
class DeliveryAddress(BaseModel):
    street_name: str = ""
    building_name: str = ""
    building_number: str = ""
    city_name: str = ""
    postal_zone: str = ""
    country_subentity: str = ""
    address_line: str = ""
    country: str = ""

class RequestedDeliveryPeriod(BaseModel):
    start_date: Union[str, None] = None
    start_time: Union[str, None] = None
    end_date: Union[str, None] = None
    end_time: Union[str, None] = None

class Consignment(BaseModel):
    id: str

class Shipment(BaseModel):
    id: str
    consignment: Consignment
    delivery: dict  # Empty delivery structure

# In-memory storage for shipments (simulating a database)
shipments_db = {}

@app.put("/v1/shipment/{shipmentId}/createShipment")
def create_shipment(shipmentId: str):
    # Check if shipment already exists
    if shipmentId in shipments_db:
        raise HTTPException(status_code=400, detail="Shipment already exists")

    # Generate unique consignment ID
    consignment_id = str(uuid.uuid4())

    # Create Shipment object
    shipment = Shipment(
        id=shipmentId,
        consignment=Consignment(id=consignment_id),
        delivery={
            "delivery_address": DeliveryAddress(),
            "requested_delivery_period": RequestedDeliveryPeriod(),
        }
    )

    # Store shipment
    shipments_db[shipmentId] = shipment

    return {"message": "Shipment created successfully"}


    q