from __future__ import annotations

import json

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.agents import AgentRegistry
from app.database import Base
from app.models import (
    ChangeRequestStatus,
    ExpectationStatus,
    RequirementStatus,
)
from app.services import WorkflowService


class FakeLLMClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def structured_completion(self, *, system_prompt: str, user_prompt: str, temperature: float | None = None) -> dict:
        self.calls.append(("structured", system_prompt))
        try:
            payload = json.loads(user_prompt)
        except json.JSONDecodeError:
            payload = None
        if payload is None:
            # Expectation extraction branch
            return {
                "expectations": [
                    {
                        "title": "Improve onboarding analytics",
                        "description": "Improve onboarding analytics for growth teams to understand conversion.",
                        "priority": "Should",
                        "impact_score": 72,
                        "ice_score": 65,
                        "tags": ["growth"],
                    },
                    {
                        "title": "Ensure login security must support MFA",
                        "description": "Ensure login security must support MFA for administrators.",
                        "priority": "Must",
                        "impact_score": 81,
                        "ice_score": 70,
                        "tags": ["security"],
                    },
                ]
            }
        if "primary_expectation" in payload:
            return {
                "title": payload["primary_expectation"]["title"],
                "one_pager": "Problem, goal, and value statement synthesised by AI.",
                "user_story": "As an operations leader I want analytics improvements so that we increase activation.",
                "acceptance_criteria": [
                    "Data events recorded for onboarding journey.",
                    "Dashboards expose cohort conversion with MFA usage.",
                    "Security controls documented and approved.",
                ],
                "raci": {
                    "Responsible": payload["primary_expectation"]["title"],
                    "Accountable": "Product Owner",
                    "Consulted": [rel["title"] for rel in payload["related_expectations"]],
                    "Informed": ["Stakeholders"],
                },
            }
        if "requirement" in payload:
            return {
                "dependencies": payload.get("candidate_dependencies", []),
                "conflicts": payload.get("candidate_conflicts", []),
                "definition_of_ready": payload["requirement"]["acceptance_criteria_count"] >= 3,
            }
        raise AssertionError("Unexpected structured_completion payload")

    def complete(self, *, system_prompt: str, user_prompt: str, temperature: float | None = None) -> str:
        self.calls.append(("complete", system_prompt))
        payload = json.loads(user_prompt)
        requirement_id = payload["change_request"]["requirement_id"]
        return (
            f"Change impacts requirement #{requirement_id} with positive sentiment. "
            "Estimated reach: 2 teams."
        )


@pytest.fixture()
def session() -> Session:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    with TestingSessionLocal() as session:
        yield session


def test_end_to_end_workflow(session: Session) -> None:
    fake_llm = FakeLLMClient()
    agents = AgentRegistry(llm_client=fake_llm)
    service = WorkflowService(session, agents)

    text = (
        "Improve onboarding analytics for #growth teams to understand conversion. "
        "Ensure login security must support MFA for administrators."
    )
    expectations = service.ingest_expectations(text)
    session.commit()

    assert len(expectations) == 2
    assert all(exp.status == ExpectationStatus.NEW for exp in expectations)
    assert expectations[0].priority in {"Should", "Must", "Could"}

    requirement = service.generate_requirement_from_expectations([exp.id for exp in expectations])
    session.commit()

    assert requirement.status in {RequirementStatus.DRAFT, RequirementStatus.READY}
    assert len(requirement.acceptance_criteria) >= 3
    assert requirement.definition_of_ready is True

    requirement = service.approve_requirement(requirement)
    session.commit()

    assert requirement.status == RequirementStatus.APPROVED
    assert all(exp.status == ExpectationStatus.APPROVED for exp in requirement.expectations)

    change_request = service.submit_change_request(
        requirement.id,
        title="Adjust analytics scope",
        description="Improve reporting dimensions for growth teams",
    )
    session.commit()

    assert change_request.status == ChangeRequestStatus.ANALYZED
    assert "Change impacts requirement" in change_request.impact_summary

    definition = service.ensure_metric_definition("NPS", "float", "Net Promoter Score", "%")
    metric = service.attach_metric_value(definition, requirement=requirement, value="75")
    session.commit()

    assert metric.value == "75"
    assert metric.definition.name == "NPS"

    result = service.nlq_search("analytics")
    assert len(result["requirements"]) >= 1
    assert not result["recommendations"]

    structured_calls = [call for call in fake_llm.calls if call[0] == "structured"]
    complete_calls = [call for call in fake_llm.calls if call[0] == "complete"]
    assert len(structured_calls) >= 3
    assert len(complete_calls) == 1
