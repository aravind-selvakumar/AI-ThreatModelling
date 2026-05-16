from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama

from app.config import settings
from app.ingestion.vectorstore import get_retriever


def get_llm():
    return Ollama(
        model=settings.llm_model,
        base_url=settings.ollama_base_url,
        temperature=0.1,
        num_predict=2048,
    )


def build_rag_chain(session_context: str = ""):
    llm = get_llm()
    retriever = get_retriever(k=5)

    context_hint = ""
    if session_context:
        context_hint = (
            "Additional context provided by the user for this session:\n"
            f"{session_context}\n\n"
        )

    prompt_template = (
        "You are a threat modeling assistant. Use the following pieces of "
        "retrieved context from the organization's security standards to answer "
        "the question at the end.\n\n"
        f"{context_hint}"
        "Retrieved context:\n{context}\n\n"
        "Question: {question}\n\n"
        "If the retrieved context does not contain enough information to answer, "
        "state that clearly. Always cite the source document name when referencing "
        "specific standards."
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={
            "prompt": None,
        },
    )

    return qa_chain, prompt_template


def query_rag(query: str, session_context: str = "") -> dict:
    qa_chain, prompt_template = build_rag_chain(session_context)
    qa_chain.combine_documents_chain.llm_chain.prompt.template = prompt_template

    result = qa_chain.invoke({"query": query})
    return {
        "query": query,
        "answer": result["result"],
        "source_documents": [
            {
                "content": doc.page_content[:300],
                "source": doc.metadata.get("source", "unknown"),
                "doc_type": doc.metadata.get("doc_type", ""),
            }
            for doc in result.get("source_documents", [])
        ],
    }
