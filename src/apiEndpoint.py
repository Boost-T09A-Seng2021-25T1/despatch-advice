# import os
# from src.mongodb import getOrderInfo, dbConnect
# import copy

def endpointFunc(
    xmlDoc: str,
    shipment: dict,
    despatch: dict,
    supplier: dict
):

    if xmlDoc is None or not isinstance(xmlDoc, str):
        raise TypeError("Error: document is invalid.")

    if any(key is None or not isinstance(key, dict) for key in [
            shipment, despatch, supplier
    ]):
        raise TypeError(
            "Error: invalid shipment or despatch information"
        )

    # call Arnav's func here for xml to json

    # assign return, and call arnav's func to save to db

    # call Yousef's func and pass in deliverPeriodReq info

    # call Edward's func and pass in Backordering info

    # call my func to determine if seller == supplier
