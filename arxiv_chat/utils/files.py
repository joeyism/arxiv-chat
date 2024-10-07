from pathlib import Path
from typing import List, Optional, Union

import pypandoc
from langchain_community.document_loaders import (PyPDFLoader, TextLoader,
                                                  UnstructuredPowerPointLoader)
from langchain_core.documents import Document
from tqdm import tqdm


def load_document_from_filename(
    filename: str, filetypes_to_ignore: List[str] = [".exe"]
) -> List[Document]:
    if filename.endswith(".pdf"):
        loader = PyPDFLoader(filename)
        return loader.load_and_split()
    elif filename.endswith(".doc") or filename.endswith(".docx"):
        txt_filename = f"{filename}.txt"
        if Path(txt_filename).exists():
            return []
        txt_filename = convert_docx_to(filename, txt_filename, filetype="txt")
        return TextLoader(txt_filename, autodetect_encoding=True).load()
    elif filename.endswith(".ppt") or filename.endswith(".pptx"):
        loader = UnstructuredPowerPointLoader(filename)
        return loader.load()
    elif any(filename.endswith(_filetype) for _filetype in filetypes_to_ignore):
        return []
    return TextLoader(filename, autodetect_encoding=True).load()


def convert_docx_to(
    filename: str, output_filename: Optional[str] = None, filetype: str = "pdf"
) -> str:
    output_filename = output_filename or f"{filename}.{filetype}"
    output = pypandoc.convert_file(
        filename, "plain" if filetype == "txt" else filetype, outputfile=output_filename
    )
    if output:
        raise Exception(output)
    return output_filename


def load_documents_from_folder(folder: Union[str, Path]) -> List[Document]:
    folder = Path(folder)
    return [
        document
        for filepath in tqdm(
            folder.glob("**/*.*"), desc=f"Loading documents from {folder.name}"
        )
        for document in load_document_from_filename(filepath.as_posix())
    ]
