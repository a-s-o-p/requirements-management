from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Iterable, List, Sequence

from sqlalchemy.orm import Session

from .llm import LLMClient
from .models import ChangeRequest, Expectation, Requirement


@dataclass
class ExpectationDraft:
    title: str
    description: str
    priority: str
    impact_score: float
    ice_score: float
    tags: List[str]


@dataclass
class RequirementDraft:
    title: str
    one_pager: str
    user_story: str
    acceptance_criteria: List[str]
    raci: dict


class BaseAgent:
    name: str

    def __init__(self, name: str) -> None:
        self.name = name


class ExpectationExtractorAgent(BaseAgent):
    def __init__(self, llm: LLMClient) -> None:
        super().__init__("extractor")
        self.llm = llm

    def extract(self, raw_text: str) -> List[ExpectationDraft]:
        payload = self.llm.structured_completion(
            system_prompt=(
                "You are an AI requirements analyst converting stakeholder discovery notes into "
                "structured expectation drafts. Return JSON with an 'expectations' array; each "
                "item must contain title, description, priority, impact_score, ice_score, and tags."
            ),
            user_prompt=raw_text,
        )
        drafts: List[ExpectationDraft] = []
        for item in payload.get("expectations", []):
            tags = item.get("tags") or []
            if isinstance(tags, str):
                tags = [tag.strip() for tag in tags.split(",") if tag.strip()]
            drafts.append(
                ExpectationDraft(
                    title=item.get("title", "Untitled")[:80],
                    description=item.get("description", ""),
                    priority=item.get("priority", "Could"),
                    impact_score=float(item.get("impact_score", 0.0)),
                    ice_score=float(item.get("ice_score", 0.0)),
                    tags=list(tags),
                )
            )
        return drafts


class RequirementGeneratorAgent(BaseAgent):
    def __init__(self, llm: LLMClient) -> None:
        super().__init__("generator")
        self.llm = llm

    def generate(self, expectation: Expectation, related: Sequence[Expectation]) -> RequirementDraft:
        context = {
            "primary_expectation": {
                "title": expectation.title,
                "description": expectation.description,
                "priority": expectation.priority,
                "impact_score": expectation.impact_score,
                "tags": expectation.tags,
            },
            "related_expectations": [
                {
                    "title": rel.title,
                    "description": rel.description,
                    "priority": rel.priority,
                    "impact_score": rel.impact_score,
                    "tags": rel.tags,
                }
                for rel in related
            ],
        }
        payload = self.llm.structured_completion(
            system_prompt=(
                "You are an AI product manager producing requirement blueprints. "
                "Given the JSON context, respond with JSON containing title, one_pager, user_story, "
                "acceptance_criteria (array of strings), and raci (object)."
            ),
            user_prompt=json.dumps(context, ensure_ascii=False),
        )
        acceptance = payload.get("acceptance_criteria") or []
        if isinstance(acceptance, str):
            acceptance = [acceptance]
        raci = payload.get("raci") or {}
        return RequirementDraft(
            title=payload.get("title", expectation.title)[:80],
            one_pager=payload.get("one_pager", ""),
            user_story=payload.get("user_story", ""),
            acceptance_criteria=list(acceptance),
            raci=raci,
        )


class DependencyAnalyzerAgent(BaseAgent):
    def __init__(self, llm: LLMClient) -> None:
        super().__init__("dependency-analyzer")
        self.llm = llm

    def analyze(self, requirement: Requirement, all_requirements: Iterable[Requirement]) -> dict:
        conflicts = []
        dependencies = []
        target_tags = set()
        for exp in requirement.expectations:
            target_tags.update(exp.tags)
        for other in all_requirements:
            if other.id == requirement.id:
                continue
            other_tags = {tag for exp in other.expectations for tag in exp.tags}
            overlap = target_tags.intersection(other_tags)
            if overlap:
                dependencies.append({"requirement_id": other.id, "shared_tags": sorted(overlap)})
            if other.title.lower() == requirement.title.lower():
                conflicts.append({"requirement_id": other.id, "reason": "Title duplicates existing requirement"})
        heuristics = {
            "requirement": {
                "id": requirement.id,
                "title": requirement.title,
                "acceptance_criteria_count": len(requirement.acceptance_criteria or []),
                "expectation_tags": sorted(target_tags),
            },
            "candidate_dependencies": dependencies,
            "candidate_conflicts": conflicts,
        }
        payload = self.llm.structured_completion(
            system_prompt=(
                "You are an AI requirement operations analyst. Evaluate whether the incoming "
                "requirement is definition-of-ready (boolean 'definition_of_ready') based on the "
                "provided JSON describing acceptance criteria counts and detected overlaps. You may "
                "refine the dependency/conflict arrays but keep requirement_id values unchanged."
            ),
            user_prompt=json.dumps(heuristics, ensure_ascii=False),
        )
        return {
            "dependencies": payload.get("dependencies", dependencies),
            "conflicts": payload.get("conflicts", conflicts),
            "definition_of_ready": payload.get(
                "definition_of_ready",
                bool(requirement.acceptance_criteria and len(requirement.acceptance_criteria) >= 3 and not conflicts),
            ),
        }


class ImpactAnalyzerAgent(BaseAgent):
    def __init__(self, llm: LLMClient) -> None:
        super().__init__("impact-analyzer")
        self.llm = llm

    def analyze(self, change_request: ChangeRequest) -> str:
        context = {
            "change_request": {
                "id": change_request.id,
                "requirement_id": change_request.requirement_id,
                "title": change_request.title,
                "description": change_request.description,
            }
        }
        return self.llm.complete(
            system_prompt=(
                "You are an AI change-control specialist summarising impact assessments. "
                "Respond with two concise sentences describing sentiment and blast radius."
            ),
            user_prompt=json.dumps(context, ensure_ascii=False),
        )


class SearchAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__("search")

    def search(self, session: Session, query: str) -> dict:
        like = f"%{query.lower()}%"
        expectations = (
            session.query(Expectation)
            .filter(Expectation.title.ilike(like) | Expectation.description.ilike(like))
            .order_by(Expectation.created_at.desc())
            .all()
        )
        requirements = (
            session.query(Requirement)
            .filter(Requirement.title.ilike(like) | Requirement.one_pager.ilike(like))
            .order_by(Requirement.created_at.desc())
            .all()
        )
        recommendations: List[str] = []
        if not expectations:
            recommendations.append("No expectation found. Consider logging a new expectation from stakeholder interview.")
        if not requirements:
            recommendations.append("No requirement found. Evaluate if a new requirement draft is needed.")
        return {
            "expectations": expectations,
            "requirements": requirements,
            "recommendations": recommendations,
        }


class AgentRegistry:
    def __init__(self, llm_client: LLMClient | None = None) -> None:
        llm = llm_client or LLMClient()
        self.extractor = ExpectationExtractorAgent(llm)
        self.generator = RequirementGeneratorAgent(llm)
        self.dependency = DependencyAnalyzerAgent(llm)
        self.impact = ImpactAnalyzerAgent(llm)
        self.search = SearchAgent()

    def as_dict(self) -> dict:
        return {
            "extractor": self.extractor,
            "generator": self.generator,
            "dependency": self.dependency,
            "impact": self.impact,
            "search": self.search,
        }
