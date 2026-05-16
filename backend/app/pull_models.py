"""Pull required Ollama models on startup."""
import httpx

from app.config import settings


def pull_model(model: str) -> None:
    url = f"{settings.ollama_base_url}/api/pull"
    print(f"Pulling model '{model}' from {settings.ollama_base_url}...")
    try:
        with httpx.Client(timeout=600) as client:
            response = client.post(url, json={"name": model}, timeout=600)
            if response.status_code == 200:
                print(f"  ✓ Model '{model}' ready")
            else:
                print(f"  ✗ Failed to pull '{model}': {response.text}")
    except Exception as e:
        print(f"  ✗ Error pulling '{model}': {e}")


def ensure_models():
    pull_model(settings.embedding_model)
    pull_model(settings.llm_model)


if __name__ == "__main__":
    ensure_models()
