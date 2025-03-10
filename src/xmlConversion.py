# ================================================
# This file will store functions related to 
# creating the final despatch advice.

# ================================================

from lxml import etree
from utils.constants import cacSchema, cbcSchema, despatchSchema

def xmlConvert():

    xmlns = { 'cac': cacSchema, 'cbc': cbcSchema }
    root = etree.Element(f"{despatchSchema}")

    # etree.SubElement()
    print(etree.tostring(root, pretty_print=True).decode())


# def main():
#     xmlConvert()


# if __name__ == '__main__':
#     main()