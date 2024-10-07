import arxiv
from arxiv import SortCriterion, SortOrder
from langchain_postgres.vectorstores import PGVector
from tqdm import tqdm

from arxiv_chat.models.embedding import EmbeddingModel
from arxiv_chat.utils import arxiv as arxiv_utils
from arxiv_chat.utils import vectorstore

from .common import add_parser_args, parse_and_upload_result


def generate_search_queries(
    category: str="",
    sort_criterion: str="Relevance",
    sort_order: str="Descending",
    search: str="",
    num_retries: int = 10,
    offset: int = 0,
    page_size: int = 1000,
):
    client = arxiv.Client(num_retries=num_retries, page_size=page_size)
    query = (
        f"cat:{category}"
        if category
        else " OR ".join([f"cat:{_tx}" for _tx in arxiv_utils.cs_taxonomy])
    )
    return client.results(
        arxiv.Search(
            query=f"{search} {query}",
            sort_by=getattr(SortCriterion, sort_criterion),
            sort_order=getattr(SortOrder, sort_order),
        ),
        offset=offset,
    )


def start_search(
    category: str,
    vector_store: PGVector,
    search: str="",
    sort_criterion: str="Relevance",
    sort_order: str="Descending",
    num_retries: int = 10,
    offset: int = 0,
    page_size: int = 1000,
):
    queries = generate_search_queries(
        category=category,
        num_retries=num_retries,
        offset=offset,
        page_size=page_size,
        sort_criterion=sort_criterion,
        sort_order=sort_order,
        search=search,
    )
    try:
        for result in tqdm(queries, desc="Loading documents"):
            parse_and_upload_result(result, vector_store)
    except arxiv.UnexpectedEmptyPageError as e:
        start_search(
            category,
            vector_store,
            search=search,
            num_retries=num_retries,
            offset=int(e.raw_feed.feed.get("opensearch_startindex", 0)),
            page_size=page_size,
            sort_criterion=sort_criterion,
            sort_order=sort_order,
        )


def main(category: str, page_size: int, sort_criterion: str, sort_order: str, search: str):
    embedding_model = EmbeddingModel()
    vector_store = vectorstore.create(embedding_model.embedding_model)
    start_search(
        category,
        vector_store,
        search=search,
        page_size=page_size,
        sort_criterion=sort_criterion,
        sort_order=sort_order,
    )


def cli():
    import argparse

    parser = argparse.ArgumentParser(description="Initial pipeline")
    parser.add_argument("-c", "--category", default="")
    parser.add_argument("-ps", "--page-size", type=int, default=1000)
    parser.add_argument("-s", "--search", type=str)
    add_parser_args(parser)
    args = parser.parse_args()

    main(
        category=args.category,
        page_size=args.page_size,
        sort_criterion=args.sort_criterion,
        sort_order=args.sort_order,
        search=args.search
    )


if __name__ == "__main__":
    cli()
