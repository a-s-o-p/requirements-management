from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from .models import (
    ChangeRequestStatus,
    ExpectationStatus,
    RequirementStatus,
)


class MetricValueSchema(BaseModel):
    id: int
    definition_id: int
    value: str
    source: str

    class Config:
        orm_mode = True


class ExpectationBase(BaseModel):
    title: str
    description: str
    priority: str = "Should"
    impact_score: float = 0.0
    ice_score: float = 0.0
    tags: List[str] = Field(default_factory=list)


class ExpectationCreate(ExpectationBase):
    source_text: Optional[str] = None


class ExpectationIntakeRequest(BaseModel):
    text: str
    source_text: Optional[str] = None


class ExpectationRead(ExpectationBase):
    id: int
    status: ExpectationStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class RequirementBase(BaseModel):
    title: str
    one_pager: str
    user_story: str
    acceptance_criteria: List[str] = Field(default_factory=list)
    raci: dict = Field(default_factory=dict)


class RequirementCreate(BaseModel):
    expectation_ids: List[int]


class RequirementRead(RequirementBase):
    id: int
    status: RequirementStatus
    definition_of_ready: bool
    created_at: datetime
    updated_at: datetime
    expectations: List[ExpectationRead]

    class Config:
        orm_mode = True


class ChangeRequestCreate(BaseModel):
    requirement_id: int
    title: str
    description: str


class ChangeRequestRead(BaseModel):
    id: int
    requirement_id: int
    title: str
    description: str
    impact_summary: Optional[str]
    status: ChangeRequestStatus
    created_at: datetime

    class Config:
        orm_mode = True


class MetricDefinitionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    value_type: str
    unit: Optional[str] = None
    config: dict = Field(default_factory=dict)


class MetricDefinitionRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    value_type: str
    unit: Optional[str]
    config: dict

    class Config:
        orm_mode = True


class NLQSearchResponse(BaseModel):
    expectations: List[ExpectationRead] = Field(default_factory=list)
    requirements: List[RequirementRead] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
