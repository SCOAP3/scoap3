import xml.etree.ElementTree as ET
from datetime import datetime


def parse_marcxml(xml_string):
    ns = {"marc": "http://www.loc.gov/MARC21/slim"}
    root = ET.fromstring(xml_string)

    record_data = {
        "dois": [],
        "page_nr": [""],
        "arxiv_eprints": [],
        "authors": [],
        "license": [],
        "publication_info": [],
        "abstracts": [],
        "acquisition_source": {
            "source": "Jagiellonian University",
            "method": "API Upload",
            "date": datetime.utcnow().isoformat(),
        },
        "copyright": [],
        "imprints": [],
        "record_creation_date": datetime.utcnow().isoformat(),
        "titles": [],
        "files": {},
    }

    for record in root.findall("marc:record", ns):
        for field in record.findall("marc:datafield", ns):
            tag = field.attrib.get("tag")
            subfields = {
                sf.attrib["code"]: sf.text for sf in field.findall("marc:subfield", ns)
            }

            if tag == "024" and subfields.get("2") == "DOI":
                record_data["dois"].append({"value": subfields["a"]})

            elif tag == "037" and subfields.get("9") == "arXiv":
                record_data["arxiv_eprints"].append(
                    {"value": subfields["a"], "categories": []}
                )

            elif tag == "100" or tag == "700":
                author = {
                    "full_name": subfields.get("a", ""),
                    "given_names": subfields.get("a", "").split(", ")[-1]
                    if ", " in subfields.get("a", "")
                    else "",
                    "surname": subfields.get("a", "").split(", ")[0]
                    if ", " in subfields.get("a", "")
                    else subfields.get("a", ""),
                    "affiliations": [
                        {
                            "value": subfields.get("u", ""),
                            "organization": subfields.get("u", ""),
                            "country": subfields.get("u", "").split(",")[-1].strip()
                            if subfields.get("u")
                            else "",
                        }
                    ]
                    if "u" in subfields
                    else [],
                }
                record_data["authors"].append(author)

            elif tag == "540":
                record_data["license"].append(
                    {
                        "url": subfields.get("u", ""),
                        "license": subfields.get("a", ""),
                    }
                )

            elif tag == "773":
                record_data["publication_info"].append(
                    {
                        "journal_title": subfields.get("p", ""),
                        "journal_volume": subfields.get("v", ""),
                        "year": int(subfields.get("y", 0))
                        if subfields.get("y")
                        else None,
                        "journal_issue": subfields.get("n", ""),
                        "material": "article",
                    }
                )

            elif tag == "520":
                record_data["abstracts"].append(
                    {
                        "value": f"<p>{subfields.get('a', '')}</p>",
                        "source": "Jagiellonian University",
                    }
                )

            elif tag == "245":
                record_data["titles"].append(
                    {
                        "title": subfields.get("a", ""),
                        "source": "Jagiellonian University",
                    }
                )

            elif tag == "260":
                record_data["imprints"].append(
                    {
                        "date": subfields.get("c", ""),
                        "publisher": "Jagiellonian University",
                    }
                )

            elif tag == "FFT":
                file_url = subfields.get("a", "")
                if file_url.endswith(".pdf"):
                    record_data["files"]["pdf"] = file_url

    return record_data
