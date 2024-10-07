from arxiv import Result
import argparse
from langchain_community.document_loaders import PyPDFLoader, OnlinePDFLoader, PyMuPDFLoader, UnstructuredHTMLLoader, UnstructuredURLLoader
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from loguru import logger
from sqlalchemy.exc import DataError
from uuid_extensions import uuid7
from openai import RateLimitError
from pypdf.errors import PdfReadError

from arxiv_chat.utils.documents import text_splitter
from arxiv_chat.utils.redis import client as redis_client

RETRY_LIMIT = 10

def _replace_non_utf8_character(sentence: str):
    return "".join(
        char if char.encode("utf-8", "ignore") else "\uFFFD" for char in sentence
    )


def add_documents_to_vector_store(
    vector_store: VectorStore, docs: list[Document], err_idx: int = 0
):
    if not docs:
        return

    try:
        ids = [doc.id for doc in docs]
        vector_store.add_documents(docs, ids=ids)
    except DataError as e:
        logger.error(f"{e.orig}")
        if err_idx >= RETRY_LIMIT:
            import ipdb

            ipdb.set_trace()
        for doc in docs:
            if "\x00" in doc.page_content:
                doc.page_content = doc.page_content.replace("\x00", "\uFFFD")
        add_documents_to_vector_store(vector_store, docs, err_idx=err_idx + 1)
    except UnicodeEncodeError as e:
        logger.error(f"{e.reason}")
        for doc in docs:
            doc.page_content = _replace_non_utf8_character(doc.page_content)
        add_documents_to_vector_store(vector_store, docs, err_idx=err_idx + 1)
    except RateLimitError as e:
        import time
        time.sleep(10*(err_idx + 1))
        add_documents_to_vector_store(vector_store, docs, err_idx=err_idx + 1)
    except Exception as e:
        logger.error(f"{' '.join(e.args)}")
        import ipdb

        ipdb.set_trace()
        1

def _read_pdf_url_as_html(pdf_url: str):
    documents = UnstructuredURLLoader(urls=[pdf_url.replace("pdf", "html")]).load() 
    return [document for document in documents if document.page_content not in ["Web Accessibility Assistance", "We gratefully acknowledge support from the Simons Foundation and member institutions."]]

def parse_and_upload_result(result: Result, vector_store: VectorStore) -> None:
    arxiv_id = result.entry_id.split("/")[-1].split("v")[0]
    if redis_client.smembers(arxiv_id):
        return

    try:
        documents = PyPDFLoader(str(result.pdf_url)).load()
    except ValueError as e:
        logger.error(f"{' '.join(e.args)} for {result.pdf_url}")
        return
    except PdfReadError as e:
        logger.error(f"Error reading {result.pdf_url} to give error\n{' '.join(e.args)}")
        logger.info(f"Trying to read as HTML instead...")
        documents = _read_pdf_url_as_html(str(result.pdf_url))
        if len(documents) <= 1:
            logger.error(f"Failed to read from html")
            return
        import ipdb; ipdb.set_trace()
        logger.info(f"Success!")
    except Exception as e:
        import ipdb

        ipdb.set_trace()
        return


    for document in documents:
        document.metadata.update(
            {
                "title": result.title,
                "authors": [str(author) for author in result.authors],
                "categories": result.categories,
                "comment": result.comment,
                "journal_ref": result.journal_ref,
                "published": result.published.strftime("%Y-%m-%d"),
                "updated": result.updated.strftime("%Y-%m-%d"),
            }
        )

    docs = text_splitter.split_documents(documents)
    for doc in docs:
        _uuid = str(uuid7(ns=int(result.published.timestamp() * 1e9)))
        doc.id = _uuid
        redis_client.sadd(arxiv_id, _uuid)

    add_documents_to_vector_store(vector_store, docs, err_idx=0)

def add_parser_args(parser: argparse.ArgumentParser):
    parser.add_argument("-sc", "--sort-criterion", default="Relevance", choices=["Relevance", "LastUpdatedDate", "SubmittedDate"])
    parser.add_argument("-so", "--sort-order", default="Descending", choices=["Ascending", "Descending"])
