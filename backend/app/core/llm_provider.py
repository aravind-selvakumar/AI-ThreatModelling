from langchain_community.llms import Ollama

from app.config import settings


def get_llm():
    provider = settings.llm_provider
    if provider == "groq":
        return _build_groq_llm()
    return _build_ollama_llm()


def _build_ollama_llm():
    return Ollama(
        model=settings.llm_model,
        base_url=settings.ollama_base_url,
        temperature=0.1,
        num_predict=4096,
    )


def _build_groq_llm():
    try:
        from langchain_groq import ChatGroq
    except ImportError:
        raise ImportError(
            "langchain-groq is required for Groq provider. "
            "Install it with: pip install langchain-groq"
        )
    return ChatGroq(
        model=settings.groq_model,
        api_key=settings.groq_api_key,
        temperature=0.1,
        max_tokens=4096,
    )
