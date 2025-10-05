from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class ExpectationStatus(str, Enum):
    NEW = "Expectation"
    VERIFIED = "Verified"
    DRAFT = "Requirement Draft"
    READY = "DoR Ready"
    APPROVED = "Approved"
    IN_WORK = "In Work"
    VNV = "V&V"
    DONE = "Done"
    ARCHIVED = "Archived"


class RequirementStatus(str, Enum):
    DRAFT = "Draft"
    READY = "Ready"
    APPROVED = "Approved"
    IN_WORK = "In Work"
    VNV = "V&V"
    DONE = "Done"
    ARCHIVED = "Archived"


requirement_expectations = Table(
    "requirement_expectations",
    Base.metadata,
    Column("requirement_id", ForeignKey("requirements.id"), primary_key=True),
    Column("expectation_id", ForeignKey("expectations.id"), primary_key=True),
)


class Expectation(Base):
    __tablename__ = "expectations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    source_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ExpectationStatus] = mapped_column(SAEnum(ExpectationStatus), default=ExpectationStatus.NEW)
    priority: Mapped[str] = mapped_column(String(50), default="Should")
    impact_score: Mapped[float] = mapped_column(Float, default=0.0)
    ice_score: Mapped[float] = mapped_column(Float, default=0.0)
    tags: Mapped[List[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    requirements: Mapped[List["Requirement"]] = relationship(
        "Requirement", secondary=requirement_expectations, back_populates="expectations"
    )
    metric_values: Mapped[List["MetricValue"]] = relationship("MetricValue", back_populates="expectation")


class Requirement(Base):
    __tablename__ = "requirements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    one_pager: Mapped[str] = mapped_column(Text)
    user_story: Mapped[str] = mapped_column(Text)
    acceptance_criteria: Mapped[List[str]] = mapped_column(JSON, default=list)
    raci: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[RequirementStatus] = mapped_column(SAEnum(RequirementStatus), default=RequirementStatus.DRAFT)
    definition_of_ready: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    expectations: Mapped[List[Expectation]] = relationship(
        Expectation, secondary=requirement_expectations, back_populates="requirements"
    )
    versions: Mapped[List["RequirementVersion"]] = relationship(
        "RequirementVersion", back_populates="requirement", cascade="all, delete-orphan"
    )
    decisions: Mapped[List["Decision"]] = relationship("Decision", back_populates="requirement", cascade="all, delete-orphan")
    change_requests: Mapped[List["ChangeRequest"]] = relationship(
        "ChangeRequest", back_populates="requirement", cascade="all, delete-orphan"
    )
    metric_values: Mapped[List["MetricValue"]] = relationship("MetricValue", back_populates="requirement")


class RequirementVersion(Base):
    __tablename__ = "requirement_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    requirement_id: Mapped[int] = mapped_column(ForeignKey("requirements.id"))
    version: Mapped[str] = mapped_column(String(50))
    one_pager: Mapped[str] = mapped_column(Text)
    user_story: Mapped[str] = mapped_column(Text)
    acceptance_criteria: Mapped[List[str]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    requirement: Mapped[Requirement] = relationship("Requirement", back_populates="versions")


class ChangeRequestStatus(str, Enum):
    NEW = "New"
    TRIAGE = "Triage"
    ANALYZED = "Analyzed"
    APPROVED = "Approved"
    IMPLEMENTED = "Implemented"


class ChangeRequest(Base):
    __tablename__ = "change_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    requirement_id: Mapped[int] = mapped_column(ForeignKey("requirements.id"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    impact_summary: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[ChangeRequestStatus] = mapped_column(SAEnum(ChangeRequestStatus), default=ChangeRequestStatus.NEW)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    requirement: Mapped[Requirement] = relationship("Requirement", back_populates="change_requests")
    versions: Mapped[List["ChangeRequestVersion"]] = relationship(
        "ChangeRequestVersion", back_populates="change_request", cascade="all, delete-orphan"
    )


class ChangeRequestVersion(Base):
    __tablename__ = "change_request_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    change_request_id: Mapped[int] = mapped_column(ForeignKey("change_requests.id"))
    version: Mapped[str] = mapped_column(String(50))
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    change_request: Mapped[ChangeRequest] = relationship("ChangeRequest", back_populates="versions")


class Decision(Base):
    __tablename__ = "decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    requirement_id: Mapped[int] = mapped_column(ForeignKey("requirements.id"))
    role: Mapped[str] = mapped_column(String(100))
    decision: Mapped[str] = mapped_column(String(100))
    comment: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    requirement: Mapped[Requirement] = relationship("Requirement", back_populates="decisions")


class MetricDefinition(Base):
    __tablename__ = "metric_definitions"
    __table_args__ = (UniqueConstraint("name", name="uq_metric_definitions_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    value_type: Mapped[str] = mapped_column(String(50))
    unit: Mapped[Optional[str]] = mapped_column(String(50))
    config: Mapped[dict] = mapped_column(JSON, default=dict)

    metric_values: Mapped[List["MetricValue"]] = relationship("MetricValue", back_populates="definition")


class MetricValue(Base):
    __tablename__ = "metric_values"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    definition_id: Mapped[int] = mapped_column(ForeignKey("metric_definitions.id"))
    expectation_id: Mapped[Optional[int]] = mapped_column(ForeignKey("expectations.id"))
    requirement_id: Mapped[Optional[int]] = mapped_column(ForeignKey("requirements.id"))
    source: Mapped[str] = mapped_column(String(50), default="human")
    value: Mapped[str] = mapped_column(String(255))

    definition: Mapped[MetricDefinition] = relationship("MetricDefinition", back_populates="metric_values")
    expectation: Mapped[Optional[Expectation]] = relationship("Expectation", back_populates="metric_values")
    requirement: Mapped[Optional[Requirement]] = relationship("Requirement", back_populates="metric_values")
