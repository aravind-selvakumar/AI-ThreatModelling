# ThreatModellingEngine

AI-powered threat modeling engine using **STRIDE** classification, **DREAD** risk scoring, and **RAG**-augmented analysis — all powered by local or cloud LLMs.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                             Streamlit Frontend (:8501)                                │
│  ┌──────────┐  ┌──────────┐  ┌────────┐  ┌──────────────┐  ┌──────────┐             │
│  │  Login   │  │Dashboard │  │NewModel│  │ RAG Manager   │  │ Reports  │             │
│  │  app.py  │  │ page 1   │  │ page 2 │  │  page 4       │  │  page 5  │             │
│  └────┬─────┘  └────┬─────┘  └────┬───┘  └──────┬───────┘  └──────────┘             │
│       └─────────────┴─────────────┴──────────────┴──────────────────────────────────┘
│                                    │ HTTP (requests)                                  │
└────────────────────────────────────┼──────────────────────────────────────────────────┘
                                     │
┌────────────────────────────────────┼──────────────────────────────────────────────────┐
│                          FastAPI Backend (:8000)                                       │
│                                     │                                                  │
│  ┌──────────────────────────────────┴─────────────────────────────────────────────┐   │
│  │                                    Routers                                      │   │
│  │  ┌────────┐ ┌──────┐ ┌─────────────┐ ┌──────────┐ ┌───────────┐ ┌──────────┐  │   │
│  │  │ Health │ │ Auth │ │ThreatModels │ │ Analysis │ │ Ingestion │ │   RAG    │  │   │
│  │  └────────┘ └──────┘ └─────────────┘ └─────┬────┘ └─────┬────┘ └────┬─────┘  │   │
│  └─────────────────────────────────────────────┼───────────┼───────────┼─────────┘   │
│                                                 │           │           │              │
│  ┌──────────────────────────────────────────────┴───────────┴───────────┴──────────┐  │
│  │                                  Core Engine                                     │  │
│  │                                                                                  │  │
│  │  ┌──────────────────┐    ┌──────────────┐    ┌──────────────────────────────┐   │  │
│  │  │  threat_engine   │───▶│  LLM Provider│───▶│  ┌────────┐  ┌────────────┐  │   │  │
│  │  │  (Orchestrator)  │    │  ┌──────────┐│    │  │ Ollama │  │   Groq    │  │   │  │
│  │  │  ┌─────────────┐ │    │  │  factory  ││    │  │(local) │  │ (cloud)   │  │   │  │
│  │  │  │ 1. STRIDE   │ │    │  └──────────┘│    │  └────────┘  └────────────┘  │   │  │
│  │  │  │ 2. DREAD    │ │    └──────────────┘    └──────────────────────────────┘   │  │
│  │  │  │ 3. Mitigate │ │                                                          │  │
│  │  │  └─────────────┘ │                                                          │  │
│  │  └──────────────────┘                                                          │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
│                                     │                                                  │
│  ┌──────────────────────────────────┼──────────────────────────────────────────────┐   │
│  │                     Data Layer   │                                                │   │
│  │                                  ▼                                                │   │
│  │  ┌─────────────────────────────────────────────────────────────────────────┐     │   │
│  │  │                    PostgreSQL + pgvector (:5432)                         │     │   │
│  │  │  ┌──────────┐ ┌──────────┐ ┌────────┐ ┌──────────┐ ┌────────────────┐  │     │   │
│  │  │  │  users   │ │threat_   │ │ threats│ │mitigations│ │  pgvector      │  │     │   │
│  │  │  │          │ │ models   │ │        │ │           │ │  embeddings    │  │     │   │
│  │  │  └──────────┘ └──────────┘ └────────┘ └──────────┘ └────────────────┘  │     │   │
│  │  └─────────────────────────────────────────────────────────────────────────┘     │   │
│  └──────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                          │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

### Request Flow

```
User Input (components, data flows, trust boundaries)
       │
       ▼
┌──────────────────┐
│  RAG Context     │  similarity_search(component, k=5) → PGVector
│  Retrieval       │  (nomic-embed-text → vector embeddings)
└────────┬─────────┘
         │ context_chunks
         ▼
┌──────────────────┐
│  STAGE 1         │  STRIDE: Spoofing, Tampering, Repudiation,
│  STRIDE          │          Info Disclosure, DoS, Elevation of Priv
│  Classification  │  → list of threats with confidence scores
└────────┬─────────┘
         │ threats (if any)
         ▼
┌──────────────────┐
│  STAGE 2         │  DREAD: Damage, Reproducibility, Exploitability,
│  DREAD           │         Affected Users, Discoverability
│  Risk Scoring    │  → scored threats with risk_score (0-10)
└────────┬─────────┘
         │ scored_threats
         ▼
┌──────────────────┐
│  STAGE 3         │  Mitigation recommendations with priority
│  Mitigation      │  (P0/P1/P2) and source standard references
│  Recommendations │  → actionable mitigation steps
└──────────────────┘
```

## Features

- **STRIDE-Based Threat Classification** — Identifies threats across all 6 STRIDE categories (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege)
- **DREAD Risk Scoring** — Quantifies risk on 5 dimensions (Damage, Reproducibility, Exploitability, Affected Users, Discoverability) with overall risk scores
- **RAG-Augmented Analysis** — Ingests organizational security standards (PDF, MD, TXT), embeds them into PGVector, and retrieves relevant context to ground LLM outputs
- **Mitigation Recommendations** — Generates actionable mitigation steps with priority levels and references to organizational standards
- **Human-in-the-Loop Review** — Threats can be reviewed, approved, or rejected before finalizing
- **Local or Cloud LLM** — Runs fully offline with Ollama or connects to Groq's free API tier for faster cloud-powered analysis
- **JWT Authentication** — Admin and guest user roles with secure token-based auth
- **PDF Reports** — Export analysis results as PDF documents

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit (Python) |
| **Backend** | FastAPI (Python 3.12) |
| **Database** | PostgreSQL 16 + pgvector |
| **LLM (local)** | Ollama (llama3.2:3b) |
| **LLM (cloud)** | Groq (llama-3.3-70b-versatile) |
| **Embeddings** | nomic-embed-text (via Ollama) |
| **Vector Store** | LangChain PGVector |
| **Auth** | JWT (python-jose) + bcrypt |
| **Container** | Docker / Docker Compose |

## Quick Start

### Prerequisites

- Docker Desktop 4.30+
- 8 GB+ RAM (16 GB recommended for local LLM)
- 4 GB+ free disk space

### Setup

```bash
# Clone and start all services
git clone <repo-url>
cd ThreatModellingEngine
docker compose up -d
```

This starts 4 containers:
- **postgres** — Database with pgvector extension
- **ollama** — Local LLM server (pulls models on first startup)
- **backend** — FastAPI on port 8000
- **frontend** — Streamlit on port 8501

Wait 2-3 minutes for Ollama to download models and the backend to initialize. Then open **http://localhost:8501**.

Default admin credentials:
- Username: `admin`
- Password: `admin`

## Configuration

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `ollama` | `ollama` (local) or `groq` (cloud) |
| `GROQ_API_KEY` | — | Groq API key (free at https://console.groq.com) |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model name |
| `OLLAMA_PORT` | `11434` | Local Ollama port |
| `SECRET_KEY` | `change-me-in-production` | JWT signing secret |
| `API_PORT` | `8000` | Backend port |
| `FRONTEND_PORT` | `8501` | Frontend port |

### Switching to Groq (Free Cloud LLM)

```bash
# 1. Get a free API key from https://console.groq.com
# 2. Edit .env:
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your_key_here
# 3. Rebuild:
docker compose up -d --build backend
```

No Ollama dependency needed when using Groq — the LLM runs on Groq's infrastructure (much faster on CPU-limited systems).

## API Reference

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/health` | — | Service health check |
| `POST` | `/auth/login` | — | Login, returns JWT |
| `POST` | `/auth/guest` | — | Guest access (no password) |
| `POST` | `/auth/users` | Admin | Create user |
| `GET` | `/auth/users` | Admin | List users |
| `GET` | `/auth/me` | Bearer | Current user info |
| `POST` | `/threat-models/` | Bearer | Create threat model |
| `GET` | `/threat-models/` | Bearer | List all models |
| `GET` | `/threat-models/{id}` | Bearer | Get model details |
| `PUT` | `/threat-models/{id}` | Bearer | Update model |
| `DELETE` | `/threat-models/{id}` | Bearer | Delete model |
| `POST` | `/analysis/run` | Bearer | Run analysis (stateless) |
| `POST` | `/analysis/run-for-model/{id}` | Bearer | Run analysis + persist |
| `POST` | `/ingestion/upload` | Admin | Upload document |
| `GET` | `/ingestion/documents` | Admin | List documents |
| `DELETE` | `/ingestion/documents/{id}` | Admin | Delete document |
| `POST` | `/ingestion/reindex` | Admin | Re-index all documents |
| `GET` | `/ingestion/stats` | Admin | Vector store stats |
| `POST` | `/rag/query` | Bearer | Query RAG knowledge base |

## Project Structure

```
├── docker-compose.yml          # Multi-service orchestration
├── .env                        # Environment config
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py             # FastAPI entry point
│       ├── config.py           # Pydantic settings
│       ├── seed.py             # Admin user seed
│       ├── api/routes/
│       │   ├── health.py       # GET /health
│       │   ├── auth.py         # POST /auth/*
│       │   ├── threat_models.py # CRUD threat models
│       │   ├── analysis.py     # POST /analysis/*
│       │   ├── ingestion.py    # Document management
│       │   └── rag.py          # RAG query endpoint
│       ├── core/
│       │   ├── threat_engine.py # Pipeline orchestrator
│       │   ├── stride.py       # STRIDE prompt builder
│       │   ├── dread.py        # DREAD prompt builder
│       │   ├── mitigations.py  # Mitigation prompt builder
│       │   └── llm_provider.py # Ollama / Groq factory
│       ├── db/
│       │   ├── models.py       # 6 SQLAlchemy ORM models
│       │   └── session.py      # Async session factory
│       └── ingestion/
│           ├── loader.py       # PDF / TXT / MD loader
│           ├── chunker.py      # Recursive text splitter
│           └── vectorstore.py  # PGVector operations
└── frontend/
    ├── Dockerfile
    ├── app.py                  # Login page
    └── pages/
        ├── 1_Dashboard.py      # Threat model list
        ├── 2_New_Model.py      # Create model
        ├── 3_Review.py         # Review models
        ├── 4_RAG_Manager.py   # Document management
        └── 5_Reports.py        # Export PDFs
```

## Database Schema

6 tables managed via SQLAlchemy auto-migration:

- **users** — id, username (unique), password_hash, role (admin/guest), created_at
- **threat_models** — id, name, description, created_by (FK→users), status (draft/review/approved/archived), components (JSON), data_flows (JSON), trust_boundaries (JSON), session_context, timestamps
- **threats** — id, model_id (FK→threat_models), component, stride_category, description, dread_scores (JSON), risk_score, status
- **mitigations** — id, threat_id (FK→threats), description, source_standard, approved
- **standards** — id, title, content, doc_type
- **session_contexts** — id, model_id (FK→threat_models), content

## License

MIT
