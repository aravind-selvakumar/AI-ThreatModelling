import os

import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def _headers(token: str | None = None) -> dict:
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def health_check() -> bool:
    try:
        r = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return r.status_code == 200
    except requests.RequestException:
        return False


def login(username: str, password: str) -> dict | None:
    r = requests.post(
        f"{API_BASE_URL}/auth/login",
        json={"username": username, "password": password},
    )
    if r.status_code == 200:
        return r.json()
    return None


def guest_login() -> dict | None:
    r = requests.post(f"{API_BASE_URL}/auth/guest")
    if r.status_code == 200:
        return r.json()
    return None


def get_me(token: str) -> dict | None:
    r = requests.get(f"{API_BASE_URL}/auth/me", headers=_headers(token))
    return r.json() if r.status_code == 200 else None


def list_threat_models(token: str) -> list:
    r = requests.get(f"{API_BASE_URL}/threat-models", headers=_headers(token))
    return r.json() if r.status_code == 200 else []


def create_threat_model(token: str, name: str, description: str = "") -> dict | None:
    r = requests.post(
        f"{API_BASE_URL}/threat-models",
        json={"name": name, "description": description},
        headers=_headers(token),
    )
    return r.json() if r.status_code == 201 else None


def get_threat_model(token: str, model_id: int) -> dict | None:
    r = requests.get(f"{API_BASE_URL}/threat-models/{model_id}", headers=_headers(token))
    return r.json() if r.status_code == 200 else None


def delete_threat_model(token: str, model_id: int) -> bool:
    r = requests.delete(f"{API_BASE_URL}/threat-models/{model_id}", headers=_headers(token))
    return r.status_code == 204


# ── Ingestion / RAG ──

def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def upload_document(token: str, file_obj, filename: str) -> dict | None:
    r = requests.post(
        f"{API_BASE_URL}/ingestion/upload",
        files={"file": (filename, file_obj)},
        headers=_auth_headers(token),
    )
    return r.json() if r.status_code == 200 else None


def list_documents(token: str) -> list:
    r = requests.get(f"{API_BASE_URL}/ingestion/documents", headers=_auth_headers(token))
    return r.json() if r.status_code == 200 else []


def delete_document(token: str, doc_id: int) -> bool:
    r = requests.delete(f"{API_BASE_URL}/ingestion/documents/{doc_id}", headers=_auth_headers(token))
    return r.status_code == 204


def reindex_documents(token: str) -> dict | None:
    r = requests.post(f"{API_BASE_URL}/ingestion/reindex", headers=_auth_headers(token))
    return r.json() if r.status_code == 200 else None


def get_ingestion_stats(token: str) -> dict:
    r = requests.get(f"{API_BASE_URL}/ingestion/stats", headers=_auth_headers(token))
    return r.json() if r.status_code == 200 else {}


def rag_query(token: str, query: str, session_context: str = "") -> dict | None:
    r = requests.post(
        f"{API_BASE_URL}/rag/query",
        json={"query": query, "session_context": session_context},
        headers=_auth_headers(token),
    )
    return r.json() if r.status_code == 200 else None
