import re
from datetime import datetime

import fitz

from scoap3.articles.models import ArticleIdentifierType


def get_first_doi(article_document):
    for identifier in article_document.article_identifiers:
        if identifier.identifier_type == ArticleIdentifierType.DOI.value:
            return identifier.identifier_value
    return None


def get_first_arxiv(article_document):
    for identifier in article_document.article_identifiers:
        if identifier.identifier_type == ArticleIdentifierType.ARXIV.value:
            return identifier.identifier_value
    return None


def get_arxiv_primary_category(article_document):
    for arxiv_category in article_document.article_arxiv_category:
        if arxiv_category.primary:
            return arxiv_category.category


def parse_string_to_date_object(date_string):
    return datetime.fromisoformat(date_string.replace("Z", "+00:00"))


def is_string_in_pdf(article_file, search_string):
    try:
        with article_file.file.open(mode="rb") as f:
            data = f.read()

        filetype = "pdf" if article_file.file.name.lower().endswith(".pdf") else "txt"
        doc = fitz.open(stream=data, filetype=filetype)

        for page in doc:
            hits = page.search_for(search_string)
            if hits:
                doc.close()
                return True

        full_text = ""
        for page in doc:
            full_text += page.get_text()
        search_string_normalized = re.sub(r"\s+", "", search_string.lower())
        full_text_normalized = re.sub(r"\s+", "", full_text.lower())
        doc.close()
        return search_string_normalized in full_text_normalized

    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {article_file}")
    except Exception as e:
        raise Exception(f"An error occurred while reading the PDF: {str(e)}")
