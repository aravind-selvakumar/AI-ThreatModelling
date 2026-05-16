import os
import tempfile
from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.documents import Document


TEXT_EXTENSIONS = {".md", ".txt"}
SUPPORTED = {".pdf"} | TEXT_EXTENSIONS


def load_document(file_path: str, doc_type: str | None = None) -> list[Document]:
    ext = (doc_type or Path(file_path).suffix or Path(file_path).name).lower()
    if not ext.startswith("."):
        ext = f".{ext}"

    if ext not in SUPPORTED:
        raise ValueError(f"Unsupported document type: {ext}")

    if ext == ".pdf":
        from langchain_community.document_loaders import PyMuPDFLoader
        loader = PyMuPDFLoader(file_path)
    else:
        loader = TextLoader(file_path, encoding="utf-8")

    docs = loader.load()
    for doc in docs:
        doc.metadata["source"] = Path(file_path).name
        doc.metadata["doc_type"] = ext.lstrip(".")
    return docs


def load_bytes(content: bytes, filename: str) -> list[Document]:
    ext = Path(filename).suffix.lower() or ".txt"
    if ext not in SUPPORTED:
        ext = ".txt"
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    try:
        return load_document(tmp_path, doc_type=ext)
    finally:
        os.unlink(tmp_path)
