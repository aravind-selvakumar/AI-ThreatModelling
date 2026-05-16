from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def get_splitter(chunk_size: int = 1000, chunk_overlap: int = 200):
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )


def split_documents(documents: list[Document], chunk_size: int = 1000, chunk_overlap: int = 200) -> list[Document]:
    splitter = get_splitter(chunk_size, chunk_overlap)
    return splitter.split_documents(documents)
