import logging

import backoff
from habanero import Crossref, RequestError

logger = logging.getLogger(__name__)


@backoff.on_exception(backoff.expo, RequestError, max_tries=5)
def fetch_doi_registration_date(doi):
    cr = Crossref()
    try:
        response = cr.works(ids=doi)
        registration_date = response["message"]["created"]["date-time"]
        return registration_date.split("T")[0]
    except Exception as e:
        logger.error("Failed to fetch DOI registration date for %s: %s", doi, str(e))
        return None
