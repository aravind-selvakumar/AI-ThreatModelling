from datetime import datetime

from pydantic import BaseModel


# ── Auth ──
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str


class GuestTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str = "guest"
    username: str = "guest"


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "guest"


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Common Inputs (used by Threat Models + Analysis) ──
class ComponentInput(BaseModel):
    name: str
    type: str = "component"


class DataFlowInput(BaseModel):
    source: str
    target: str
    protocol: str = ""
    data: str = ""


# ── Threat Model ──
class ThreatModelCreate(BaseModel):
    name: str
    description: str = ""


class ThreatModelResponse(BaseModel):
    id: int
    name: str
    description: str
    created_by: int | None
    status: str
    components: list
    data_flows: list
    trust_boundaries: list
    session_context: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ThreatModelUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    components: list[ComponentInput] | None = None
    data_flows: list[DataFlowInput] | None = None
    trust_boundaries: list[str] | None = None
    session_context: str | None = None


class ThreatModelListItem(BaseModel):
    id: int
    name: str
    status: str
    created_by: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Ingestion / RAG ──
class IngestionStatus(BaseModel):
    document_id: int
    filename: str
    chunk_count: int
    status: str


class DocumentResponse(BaseModel):
    id: int
    title: str
    doc_type: str
    created_at: datetime

    model_config = {"from_attributes": True}


class RAGQueryRequest(BaseModel):
    query: str
    session_context: str = ""


class SourceDocument(BaseModel):
    content: str
    source: str
    doc_type: str


class RAGQueryResponse(BaseModel):
    query: str
    answer: str
    source_documents: list[SourceDocument]


# ── Analysis (STRIDE + DREAD) ──
class AnalysisRequest(BaseModel):
    components: list[ComponentInput] = []
    data_flows: list[DataFlowInput] = []
    trust_boundaries: list[str] = []
    session_context: str = ""


class ThreatItem(BaseModel):
    stride_category: str
    threat_present: bool
    description: str
    confidence: str = "Medium"
    relevant_standard: str | None = None


class DreadScores(BaseModel):
    Damage: int
    Reproducibility: int
    Exploitability: int
    AffectedUsers: int
    Discoverability: int


class ScoredThreatItem(BaseModel):
    stride_category: str
    description: str
    dread_scores: DreadScores
    risk_score: float
    risk_level: str = "Medium"


class MitigationItem(BaseModel):
    stride_category: str
    description: str
    actions: list[str]
    source_standard: str | None = None
    priority: str = "P2"


class ComponentAnalysis(BaseModel):
    component: str
    threats: list[ThreatItem] = []
    scored_threats: list[ScoredThreatItem] = []
    mitigations: list[MitigationItem] = []


class AnalysisResponse(BaseModel):
    components: list[ComponentAnalysis]
    total_threats: int
    average_risk_score: float
