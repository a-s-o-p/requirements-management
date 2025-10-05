from __future__ import annotations

from typing import Iterable, List, Sequence

from sqlalchemy.orm import Session

from .agents import AgentRegistry
from .models import (
    ChangeRequest,
    ChangeRequestStatus,
    Expectation,
    ExpectationStatus,
    MetricDefinition,
    MetricValue,
    Requirement,
    RequirementStatus,
    RequirementVersion,
)


class WorkflowService:
    def __init__(self, session: Session, agents: AgentRegistry | None = None) -> None:
        self.session = session
        self.agents = agents or AgentRegistry()

    # Expectation management -------------------------------------------------
    def ingest_expectations(self, raw_text: str) -> List[Expectation]:
        drafts = self.agents.extractor.extract(raw_text)
        expectations: List[Expectation] = []
        for draft in drafts:
            expectation = Expectation(
                title=draft.title,
                description=draft.description,
                source_text=raw_text,
                priority=draft.priority,
                impact_score=draft.impact_score,
                ice_score=draft.ice_score,
                tags=draft.tags,
            )
            self.session.add(expectation)
            expectations.append(expectation)
        self.session.flush()
        return expectations

    def update_expectation_status(self, expectation: Expectation, status: ExpectationStatus) -> Expectation:
        expectation.status = status
        self.session.add(expectation)
        self.session.flush()
        return expectation

    # Requirement management -------------------------------------------------
    def generate_requirement_from_expectations(self, expectation_ids: Sequence[int]) -> Requirement:
        expectations = (
            self.session.query(Expectation)
            .filter(Expectation.id.in_(expectation_ids))
            .all()
        )
        if not expectations:
            raise ValueError("No expectations provided for requirement generation")
        primary = expectations[0]
        draft = self.agents.generator.generate(primary, expectations[1:])
        requirement = Requirement(
            title=draft.title,
            one_pager=draft.one_pager,
            user_story=draft.user_story,
            acceptance_criteria=draft.acceptance_criteria,
            raci=draft.raci,
            status=RequirementStatus.DRAFT,
        )
        requirement.expectations.extend(expectations)
        self.session.add(requirement)
        self.session.flush()
        version = RequirementVersion(
            requirement_id=requirement.id,
            version="0.1.0",
            one_pager=requirement.one_pager,
            user_story=requirement.user_story,
            acceptance_criteria=requirement.acceptance_criteria,
        )
        self.session.add(version)
        for expectation in expectations:
            expectation.status = ExpectationStatus.DRAFT
        self.session.flush()
        self.evaluate_definition_of_ready(requirement)
        return requirement

    def evaluate_definition_of_ready(self, requirement: Requirement) -> Requirement:
        analysis = self.agents.dependency.analyze(requirement, self.session.query(Requirement).all())
        requirement.definition_of_ready = analysis["definition_of_ready"]
        if requirement.definition_of_ready:
            requirement.status = RequirementStatus.READY
        self.session.add(requirement)
        self.session.flush()
        return requirement

    def approve_requirement(self, requirement: Requirement) -> Requirement:
        requirement.status = RequirementStatus.APPROVED
        self.session.add(requirement)
        self.session.flush()
        for expectation in requirement.expectations:
            expectation.status = ExpectationStatus.APPROVED
        return requirement

    # Change request management ---------------------------------------------
    def submit_change_request(self, requirement_id: int, title: str, description: str) -> ChangeRequest:
        requirement = self.session.get(Requirement, requirement_id)
        if not requirement:
            raise ValueError("Requirement not found")
        change_request = ChangeRequest(
            requirement=requirement,
            title=title,
            description=description,
            status=ChangeRequestStatus.TRIAGE,
        )
        self.session.add(change_request)
        self.session.flush()
        impact_summary = self.agents.impact.analyze(change_request)
        change_request.impact_summary = impact_summary
        change_request.status = ChangeRequestStatus.ANALYZED
        self.session.add(change_request)
        self.session.flush()
        return change_request

    # Metrics ----------------------------------------------------------------
    def ensure_metric_definition(
        self, name: str, value_type: str, description: str | None = None, unit: str | None = None
    ) -> MetricDefinition:
        definition = (
            self.session.query(MetricDefinition)
            .filter(MetricDefinition.name == name)
            .one_or_none()
        )
        if definition:
            return definition
        definition = MetricDefinition(name=name, value_type=value_type, description=description, unit=unit)
        self.session.add(definition)
        self.session.flush()
        return definition

    def attach_metric_value(
        self,
        definition: MetricDefinition,
        *,
        expectation: Expectation | None = None,
        requirement: Requirement | None = None,
        value: str,
        source: str = "ai",
    ) -> MetricValue:
        metric_value = MetricValue(
            definition=definition,
            expectation=expectation,
            requirement=requirement,
            value=value,
            source=source,
        )
        self.session.add(metric_value)
        self.session.flush()
        return metric_value

    # Search -----------------------------------------------------------------
    def nlq_search(self, query: str) -> dict:
        return self.agents.search.search(self.session, query)


# Helper functions -----------------------------------------------------------

def get_requirement(session: Session, requirement_id: int) -> Requirement:
    requirement = session.get(Requirement, requirement_id)
    if not requirement:
        raise ValueError("Requirement not found")
    return requirement


def get_expectation(session: Session, expectation_id: int) -> Expectation:
    expectation = session.get(Expectation, expectation_id)
    if not expectation:
        raise ValueError("Expectation not found")
    return expectation
