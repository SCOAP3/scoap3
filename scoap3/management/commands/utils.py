import logging
from datetime import datetime


def get_query(action, gte, time_unit):
    return {
        "query": {
            "range": {
                f"{action}": {
                    "gte": f"now-{gte}{time_unit}/{time_unit}",
                    # "lt": f"now/{time_unit}",
                }
            }
        }
    }


def get_timestamp_str():
    current_date = datetime.now().date()
    current_date_str = current_date.strftime("%Y-%m-%d %H:%M:%S")
    return current_date_str


def check_time_unit(time_unit):
    if time_unit not in ("h", "d", "w", "m", "y"):
        raise Exception(
            "The value of option --time-units possible options are: h, d, w, m, y"
        )
    else:
        return time_unit


def get_path_value(doc, path):
    keys = path.split(".")
    temp = doc
    for key in keys:
        if "[" in key and "]" in key:
            key, idx = key[:-1].split("[")
            temp = temp[key][int(idx)]
        else:
            temp = temp[key]
    return temp


def get_results(es, response, path, scroll="30s"):
    all_items = []
    scroll_id = response["_scroll_id"]
    total_docs = response["hits"]["total"]["value"]
    logging.info(f"Found {total_docs} records.")
    processed = 0
    while processed < total_docs:
        documents = response["hits"]["hits"]
        items = [get_path_value(doc, path) for doc in documents]
        processed += len(items)
        all_items = all_items + items
        response = es.scroll(scroll_id=scroll_id, scroll=scroll)
    es.clear_scroll(scroll_id=scroll_id)
    return all_items


def get_dois_from_response_legacy(es, response, scroll="30s"):
    all_dois = get_results(
        es=es, response=response, scroll=scroll, path="_source.dois[0].value"
    )
    return all_dois


def get_countries_from_authors(all_authors):
    all_affiliations = []
    for authors_in_one_record in all_authors:
        for one_author in authors_in_one_record:
            if "affiliations" in one_author:
                all_affiliations.append(one_author["affiliations"])
            else:
                logging.error("Author has no country!")
    countries = []
    for one_author_affiliations in all_affiliations:
        for affiliation in one_author_affiliations:
            if "country" in affiliation:
                countries.append(affiliation["country"])
            else:
                logging.error("Affiliation has no country!")
    return countries


def get_countries_from_response_legacy(es, response, scroll="30s"):
    all_authors = get_results(
        es=es, response=response, scroll=scroll, path="_source.authors"
    )
    countries = get_countries_from_authors(all_authors)
    countries_set = set(countries)
    return countries_set


def get_dois_from_response(es, response, scroll="30s"):
    all_dois = get_results(es=es, response=response, scroll=scroll, path="_source.doi")
    return all_dois


def get_countries_from_response(es, response, scroll="30s"):
    all_authors = get_results(
        es=es, response=response, scroll=scroll, path="_source.authors"
    )
    countries = get_countries_from_authors(all_authors)
    country_names = [country["name"] for country in countries]
    countries_set = set(country_names)
    return countries_set


def get_record_files_urls_new(record_files):
    urls = []
    for record_file in record_files:
        file_type = record_file["file"].rsplit(".", 1).pop()
        urls.append({file_type: record_file["file"]})
    return urls


def get_record_files_urls_legacy(record_files):
    urls = []
    for record_file in record_files:
        url = f"https://repo.scoap3.org/api/files/{record_file['bucket']}/{record_file['key']}"
        urls.append({record_file["filetype"]: url})
    return urls


def get_mapped_dois_and_files_legacy(es, response, scroll="30s"):
    all_items = []
    scroll_id = response["_scroll_id"]
    total_docs = response["hits"]["total"]["value"]
    logging.info(f"Found {total_docs} records.")
    processed = 0
    while processed < total_docs:
        documents = response["hits"]["hits"]
        items = [
            {
                get_path_value(
                    doc, "_source.dois[0].value"
                ): get_record_files_urls_legacy(get_path_value(doc, "_source._files"))
            }
            for doc in documents
        ]
        processed += len(items)
        all_items = all_items + items
        response = es.scroll(scroll_id=scroll_id, scroll=scroll)
    es.clear_scroll(scroll_id=scroll_id)
    return all_items


def get_mapped_dois_and_files_new(es, response, scroll="30s"):
    all_items = []
    scroll_id = response["_scroll_id"]
    total_docs = response["hits"]["total"]["value"]
    logging.info(f"Found {total_docs} records.")
    processed = 0
    while processed < total_docs:
        documents = response["hits"]["hits"]
        items = [
            {
                get_path_value(doc, "_source.doi"): get_record_files_urls_new(
                    get_path_value(doc, "_source.related_files")
                )
            }
            for doc in documents
        ]
        processed += len(items)
        all_items = all_items + items
        response = es.scroll(scroll_id=scroll_id, scroll=scroll)
    es.clear_scroll(scroll_id=scroll_id)
    return all_items


def get_added_new_files(updated_at_record_date, files):
    updated_files = []
    updated_at_date = datetime.fromisoformat(updated_at_record_date).replace(
        second=0, microsecond=0
    )
    for one_file in files:
        created_at_date = datetime.fromisoformat(one_file["created"]).replace(
            second=0, microsecond=0
        )
        if created_at_date == updated_at_date:
            updated_files.append(one_file)
    return get_record_files_urls_new(updated_files)


def get_new_added_files_new_scoap3(es, response, scroll="30s"):
    all_items = []
    scroll_id = response["_scroll_id"]
    total_docs = response["hits"]["total"]["value"]
    logging.info(f"Found {total_docs} records.")
    processed = 0
    while processed < total_docs:
        documents = response["hits"]["hits"]
        items = [
            {
                get_path_value(doc, "_source.doi"): get_added_new_files(
                    get_path_value(doc, "_source._updated_at"),
                    get_path_value(doc, "_source.related_files"),
                )
            }
            for doc in documents
        ]
        processed += len(items)
        clean_items = [item for item in items for doi in item if len(item[doi]) > 0]
        all_items = all_items + clean_items
        response = es.scroll(scroll_id=scroll_id, scroll=scroll)
    es.clear_scroll(scroll_id=scroll_id)
    return all_items


def get_publishers_and_dois(es, path_pub, path_doi, response, scroll="30s"):
    all_items = []
    scroll_id = response["_scroll_id"]
    total_docs = response["hits"]["total"]["value"]
    logging.info(f"Found {total_docs} records.")
    processed = 0
    while processed < total_docs:
        documents = response["hits"]["hits"]
        items = [
            {
                get_path_value(doc, path_doi): {
                    "publishers": get_path_value(doc, path_pub)
                }
            }
            for doc in documents
        ]
        processed += len(items)
        clean_items = [item for item in items for doi in item if len(item[doi]) > 0]
        all_items = all_items + clean_items
        response = es.scroll(scroll_id=scroll_id, scroll=scroll)
    es.clear_scroll(scroll_id=scroll_id)
    return all_items


def get_publishers_from_response_legacy(es, response, scroll="30s"):
    all_publishers = get_publishers_and_dois(
        es=es,
        response=response,
        scroll=scroll,
        path_pub="_source.imprints[0].publisher",
        path_doi="_source.dois[0].value",
    )
    return all_publishers


def get_publishers_from_response(es, response, scroll="30s"):
    result = {}
    all_records_publication_info = get_publishers_and_dois(
        es=es,
        response=response,
        scroll=scroll,
        path_pub="_source.publication_info",
        path_doi="_source.doi",
    )
    for record in all_records_publication_info:
        publishers = []
        doi = list(record.keys()).pop()
        result[doi] = {}
        if "publishers" not in record[doi]:
            logging.error("Record has no publisher!")
            publishers.append("NO_PUBLISHER_FOUND")
        for publication_info in record[doi]["publishers"]:
            publishers.append(publication_info["publisher"])
        if len(set(publishers)) > 1:
            logging.error("Record has more than one publisher!")
            result[doi]["ERROR"] = "RECORD HAS MORE THAN ONE PUBLISHER"
        result[doi]["publishers"] = publishers

    return result
