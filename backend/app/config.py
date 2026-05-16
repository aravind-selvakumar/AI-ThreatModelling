from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://tme:tme_secret@localhost:5432/threatmod"
    database_url_sync: str = "postgresql+psycopg2://tme:tme_secret@localhost:5432/threatmod"
    pgvector_connection_string: str = "postgresql+psycopg2://tme:tme_secret@localhost:5432/threatmod"
    ollama_base_url: str = "http://localhost:11434"
    embedding_model: str = "nomic-embed-text"
    llm_model: str = "llama3.2:3b"

    llm_provider: str = "ollama"
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

    class Config:
        env_file = ".env"


settings = Settings()
