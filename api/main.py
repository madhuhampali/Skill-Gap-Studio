"""FastAPI endpoints for the synthetic skill-gap analysis system."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field, StrictInt, field_validator

from src.matching import analyze_student, normalize_skill_levels, rank_roles
from src.recommend import recommend_learning_pathway
from src.skills_catalog import ROLES, SKILLS, get_role


app = FastAPI(
    title="Skill Gap Analysis API",
    description="Explainable role matching and learning pathways using a synthetic skill catalog.",
    version="1.0.0",
)


class StudentSkillsRequest(BaseModel):
    """Validated student skill levels with optional free-text evidence."""

    skills: dict[str, StrictInt] = Field(default_factory=dict, description="Skill ID or skill name mapped to a level from 0 to 5")
    skills_summary: str = Field(default="", max_length=3000)

    @field_validator("skills")
    @classmethod
    def validate_skills(cls, value: dict[str, int]) -> dict[str, int]:
        normalize_skill_levels(value)
        return value


class AnalyzeRequest(StudentSkillsRequest):
    """Input contract for the selected target role analysis."""

    target_role: str

    @field_validator("target_role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        get_role(value)
        return value


@app.get("/roles")
def list_roles() -> list[dict[str, Any]]:
    """List roles with their weighted skill requirements."""
    return ROLES


@app.get("/skills")
def list_skills() -> list[dict[str, Any]]:
    """List catalog skills, categories, prerequisites, and learning resources."""
    return SKILLS


@app.post("/analyze")
def analyze(request: AnalyzeRequest) -> dict[str, Any]:
    """Return weighted match, gaps, text signals, and an ordered pathway."""
    result = analyze_student(request.skills, request.target_role, request.skills_summary)
    result["learning_pathway"] = recommend_learning_pathway(request.skills, request.target_role)
    return result


@app.post("/recommend-roles")
def recommend_roles(request: StudentSkillsRequest) -> dict[str, Any]:
    """Return baseline, TF-IDF, and combined role rankings."""
    return {
        method: rank_roles(request.skills, request.skills_summary, method=method)
        for method in ("baseline", "tfidf", "hybrid")
    }