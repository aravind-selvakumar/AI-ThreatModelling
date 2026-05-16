import enum
from datetime import datetime

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, Float, ForeignKey,
    Integer, JSON, String, Text, func,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    GUEST = "guest"


class ThreatStatus(str, enum.Enum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    ARCHIVED = "archived"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.GUEST, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    threat_models = relationship("ThreatModel", back_populates="creator")


class ThreatModel(Base):
    __tablename__ = "threat_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, default="")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(Enum(ThreatStatus), default=ThreatStatus.DRAFT, nullable=False)
    components = Column(JSON, default=list)
    data_flows = Column(JSON, default=list)
    trust_boundaries = Column(JSON, default=list)
    session_context = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    creator = relationship("User", back_populates="threat_models")
    threats = relationship("Threat", back_populates="model", cascade="all, delete-orphan")
    context_entries = relationship("SessionContext", back_populates="model", cascade="all, delete-orphan")


class Threat(Base):
    __tablename__ = "threats"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("threat_models.id"), nullable=False)
    component = Column(String(255), nullable=False)
    stride_category = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    dread_scores = Column(JSON, default=dict)
    risk_score = Column(Float, default=0.0)
    status = Column(String(50), default="open")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    model = relationship("ThreatModel", back_populates="threats")
    mitigations = relationship("Mitigation", back_populates="threat", cascade="all, delete-orphan")


class Mitigation(Base):
    __tablename__ = "mitigations"

    id = Column(Integer, primary_key=True, index=True)
    threat_id = Column(Integer, ForeignKey("threats.id"), nullable=False)
    description = Column(Text, nullable=False)
    source_standard = Column(String(255), default="")
    approved = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    threat = relationship("Threat", back_populates="mitigations")


class Standard(Base):
    __tablename__ = "standards"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    doc_type = Column(String(50), default="txt")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class SessionContext(Base):
    __tablename__ = "session_contexts"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("threat_models.id"), nullable=False)
    content = Column(Text, nullable=False)
    added_at = Column(DateTime, server_default=func.now(), nullable=False)

    model = relationship("ThreatModel", back_populates="context_entries")
