import arxiv
import requests
from rss_parser import AtomParser
from tqdm import tqdm

from arxiv_chat.models.embedding import EmbeddingModel
from arxiv_chat.utils import vectorstore

from .common import parse_and_upload_result


def main(category: str):
    atom_url = f"https://rss.arxiv.org/atom/{category}"
    response = requests.get(atom_url)
    atom = AtomParser.parse(response.text)
    embedding_model = EmbeddingModel()
    vector_store = vectorstore.create(embedding_model.embedding_model)
    for entry in tqdm(atom.feed.content.entries, desc="Loading entries"):
        result = next(
            arxiv.Client().results(
                arxiv.Search(id_list=[entry.id.content.split(":")[-1]])
            )
        )
        parse_and_upload_result(result, vector_store)

def cli():
    import argparse
    parser = argparse.ArgumentParser(description="Initial pipeline")
    parser.add_argument("-c", "--category", default="cs")
    args = parser.parse_args()

    main(category=args.category)


if __name__ == "__main__":
    cli()
