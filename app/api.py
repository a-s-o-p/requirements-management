from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from .database import SessionLocal
from .models import ChangeRequest, Expectation, ExpectationStatus, Requirement
from .schemas import (
    ChangeRequestCreate,
    ChangeRequestRead,
    ExpectationIntakeRequest,
    ExpectationRead,
    MetricDefinitionCreate,
    MetricDefinitionRead,
    NLQSearchResponse,
    RequirementCreate,
    RequirementRead,
)
from .services import WorkflowService, get_expectation, get_requirement


router = APIRouter()


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/expectations/intake", response_model=List[ExpectationRead])
def intake_expectations(payload: ExpectationIntakeRequest, db: Session = Depends(get_db)) -> List[ExpectationRead]:
    service = WorkflowService(db)
    expectations = service.ingest_expectations(payload.text)
    response = []
    for expectation in expectations:
        expectation.source_text = payload.source_text or payload.text
        db.add(expectation)
        db.flush()
        response.append(expectation)
    return response


@router.get("/expectations", response_model=List[ExpectationRead])
def list_expectations(db: Session = Depends(get_db)) -> List[ExpectationRead]:
    expectations = db.query(Expectation).order_by(Expectation.created_at.desc()).all()
    return expectations


@router.patch("/expectations/{expectation_id}", response_model=ExpectationRead)
def update_expectation(expectation_id: int, status: ExpectationStatus, db: Session = Depends(get_db)) -> ExpectationRead:
    expectation = get_expectation(db, expectation_id)
    service = WorkflowService(db)
    updated = service.update_expectation_status(expectation, status)
    return updated


@router.post("/requirements/generate", response_model=RequirementRead, status_code=status.HTTP_201_CREATED)
def generate_requirement(payload: RequirementCreate, db: Session = Depends(get_db)) -> RequirementRead:
    service = WorkflowService(db)
    try:
        requirement = service.generate_requirement_from_expectations(payload.expectation_ids)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.refresh(requirement)
    requirement = (
        db.query(Requirement)
        .options(joinedload(Requirement.expectations))
        .filter(Requirement.id == requirement.id)
        .one()
    )
    return requirement


@router.get("/requirements", response_model=List[RequirementRead])
def list_requirements(db: Session = Depends(get_db)) -> List[RequirementRead]:
    requirements = db.query(Requirement).options(joinedload(Requirement.expectations)).all()
    return requirements


@router.post("/requirements/{requirement_id}/approve", response_model=RequirementRead)
def approve_requirement(requirement_id: int, db: Session = Depends(get_db)) -> RequirementRead:
    requirement = get_requirement(db, requirement_id)
    service = WorkflowService(db)
    requirement = service.approve_requirement(requirement)
    db.refresh(requirement)
    requirement = (
        db.query(Requirement)
        .options(joinedload(Requirement.expectations))
        .filter(Requirement.id == requirement_id)
        .one()
    )
    return requirement


@router.post("/change-requests", response_model=ChangeRequestRead, status_code=status.HTTP_201_CREATED)
def submit_change_request(payload: ChangeRequestCreate, db: Session = Depends(get_db)) -> ChangeRequestRead:
    service = WorkflowService(db)
    try:
        change_request = service.submit_change_request(
            payload.requirement_id, payload.title, payload.description
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return change_request


@router.get("/change-requests", response_model=List[ChangeRequestRead])
def list_change_requests(db: Session = Depends(get_db)) -> List[ChangeRequestRead]:
    return db.query(ChangeRequest).all()


@router.post("/metrics/definitions", response_model=MetricDefinitionRead, status_code=status.HTTP_201_CREATED)
def create_metric_definition(payload: MetricDefinitionCreate, db: Session = Depends(get_db)) -> MetricDefinitionRead:
    service = WorkflowService(db)
    definition = service.ensure_metric_definition(
        name=payload.name,
        value_type=payload.value_type,
        description=payload.description,
        unit=payload.unit,
    )
    definition.config = payload.config
    db.add(definition)
    db.flush()
    return definition


@router.post("/search/nlq", response_model=NLQSearchResponse)
def nlq_search(query: str, db: Session = Depends(get_db)) -> NLQSearchResponse:
    service = WorkflowService(db)
    result = service.nlq_search(query)
    return NLQSearchResponse(
        expectations=result["expectations"],
        requirements=result["requirements"],
        recommendations=result["recommendations"],
    )


def create_app() -> FastAPI:
    from .database import Base, engine

    Base.metadata.create_all(bind=engine)
    app = FastAPI(title="AI Requirements Management Platform")
    app.include_router(router, prefix="/api")
    return app
