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
        pdf_file = article_file.file.read()
        document = fitz.open(stream=pdf_file)
        search_string_lower = search_string.lower()

        for page_num in range(document.page_count):
            page = document[page_num]
            page_text = page.get_text().lower()
            if search_string_lower in page_text:
                document.close()
                return True

        document.close()
        return False
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {article_file}")
    except Exception as e:
        raise Exception(f"An error occurred while reading the PDF: {str(e)}")
