import xml.etree.ElementTree as ET
from datetime import datetime
from inspire_dojson import marcxml2record


def parse_marcxml(xml_string):
    xml_string = xml_string.replace('<?xml version="1.0" encoding="UTF-8"?>', '')
    record_data = marcxml2record(xml_string)

    return record_data
