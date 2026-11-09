"""Weighted role matching and TF-IDF skill/role text similarity."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.skills_catalog import ROLE_BY_ID, ROLES, SKILL_BY_ID, SKILL_ID_BY_NAME


_SKILL_DOCUMENTS = [
    " ".join((skill["name"], skill["category"], skill["description"], skill["learning_resource"]))
    for skill in SKILL_BY_ID.values()
]
_SKILL_VECTORIZER = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
_SKILL_MATRIX = _SKILL_VECTORIZER.fit_transform(_SKILL_DOCUMENTS)
_ROLE_DOCUMENTS = [
    " ".join(
        [role["name"], role["description"]]
        + [
            f"{SKILL_BY_ID[item['skill_id']]['name']} {SKILL_BY_ID[item['skill_id']]['description']}"
            for item in role["required_skills"]
        ]
    )
    for role in ROLES
]
_ROLE_VECTORIZER = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
_ROLE_MATRIX = _ROLE_VECTORIZER.fit_transform(_ROLE_DOCUMENTS)


def normalize_skill_levels(skill_levels: Mapping[str, int | float]) -> dict[str, int]:
    """Resolve IDs/names and validate skill levels in the inclusive 0-5 scale."""
    normalized: dict[str, int] = {}
    for key, raw_level in skill_levels.items():
        skill_id = key if key in SKILL_BY_ID else SKILL_ID_BY_NAME.get(key.strip().casefold())
        if skill_id is None:
            raise ValueError(f"Unknown skill: {key}")
        if isinstance(raw_level, bool) or int(raw_level) != raw_level or not 0 <= int(raw_level) <= 5:
            raise ValueError(f"Skill level for {key} must be an integer from 0 to 5")
        normalized[skill_id] = int(raw_level)
    return normalized


def _skill_detail(skill_id: str, level: int, required: dict[str, Any]) -> dict[str, Any]:
    skill = SKILL_BY_ID[skill_id]
    return {
        "skill_id": skill_id,
        "name": skill["name"],
        "category": skill["category"],
        "current_level": level,
        "required_level": required["required_level"],
        "importance_weight": required["importance_weight"],
        "gap_size": max(0, required["required_level"] - level),
        "prerequisites": skill["prerequisites"],
    }


def weighted_skill_overlap(skill_levels: Mapping[str, int | float], role_key: str) -> dict[str, Any]:
    """Score a role using required-level coverage weighted by role importance."""
    levels = normalize_skill_levels(skill_levels)
    role_id = role_key if role_key in ROLE_BY_ID else next(
        (role["role_id"] for role in ROLES if role["name"].casefold() == role_key.strip().casefold()), None
    )
    if role_id is None:
        raise ValueError(f"Unknown role: {role_key}")
    role = ROLE_BY_ID[role_id]
    total_weight = sum(item["importance_weight"] for item in role["required_skills"])
    earned = 0.0
    matched: list[dict[str, Any]] = []
    weak: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    requirements = {item["skill_id"]: item for item in role["required_skills"]}
    for skill_id, requirement in requirements.items():
        level = levels.get(skill_id, 0)
        earned += requirement["importance_weight"] * min(level / requirement["required_level"], 1.0)
        detail = _skill_detail(skill_id, level, requirement)
        if level >= requirement["required_level"]:
            matched.append(detail)
        elif level == 0:
            missing.append(detail)
        else:
            weak.append(detail)
    score = 100.0 * earned / total_weight if total_weight else 0.0
    return {
        "role_id": role_id,
        "role_name": role["name"],
        "match_percentage": round(score, 2),
        "matched_skills": matched,
        "missing_skills": missing,
        "weak_skills": weak,
        "required_skill_count": len(requirements),
        "total_importance_weight": total_weight,
    }


def match_text_to_skills(text: str, top_k: int = 10) -> list[dict[str, Any]]:
    """Rank catalog skills by TF-IDF cosine similarity to free-text evidence."""
    if not text.strip():
        return []
    query = _SKILL_VECTORIZER.transform([text])
    similarities = cosine_similarity(query, _SKILL_MATRIX).ravel()
    order = np.argsort(similarities)[::-1]
    return [
        {
            "skill_id": list(SKILL_BY_ID)[index],
            "name": SKILL_BY_ID[list(SKILL_BY_ID)[index]]["name"],
            "similarity": round(float(similarities[index]), 4),
        }
        for index in order[:top_k]
        if similarities[index] > 0
    ]


def _student_text(skill_levels: Mapping[str, int | float], summary: str = "") -> str:
    levels = normalize_skill_levels(skill_levels)
    evidence = [
        f"{SKILL_BY_ID[skill_id]['name']} level {level}"
        for skill_id, level in levels.items()
        if level > 0
    ]
    return " ".join([summary, *evidence])


def rank_roles(
    skill_levels: Mapping[str, int | float], summary: str = "", method: str = "hybrid"
) -> list[dict[str, Any]]:
    """Rank all roles by baseline overlap, TF-IDF similarity, or their hybrid."""
    if method not in {"baseline", "tfidf", "hybrid"}:
        raise ValueError("method must be 'baseline', 'tfidf', or 'hybrid'")
    student_document = _student_text(skill_levels, summary)
    role_text = _ROLE_VECTORIZER.transform([student_document])
    role_similarities = cosine_similarity(role_text, _ROLE_MATRIX).ravel()
    results: list[dict[str, Any]] = []
    for index, role in enumerate(ROLES):
        baseline = weighted_skill_overlap(skill_levels, role["role_id"])["match_percentage"]
        tfidf_score = float(role_similarities[index] * 100)
        final_score = baseline if method == "baseline" else tfidf_score if method == "tfidf" else 0.7 * baseline + 0.3 * tfidf_score
        results.append(
            {
                "role_id": role["role_id"],
                "role_name": role["name"],
                "match_percentage": round(float(final_score), 2),
                "baseline_score": round(float(baseline), 2),
                "tfidf_similarity": round(tfidf_score, 2),
                "method": method,
            }
        )
    return sorted(results, key=lambda item: (-item["match_percentage"], item["role_id"]))


def analyze_student(
    skill_levels: Mapping[str, int | float], role_key: str, summary: str = ""
) -> dict[str, Any]:
    """Combine the transparent weighted score with text evidence and role context."""
    result = weighted_skill_overlap(skill_levels, role_key)
    text = _student_text(skill_levels, summary)
    role_index = next(index for index, role in enumerate(ROLES) if role["role_id"] == result["role_id"])
    role_similarity = float(cosine_similarity(_ROLE_VECTORIZER.transform([text]), _ROLE_MATRIX[role_index])[0, 0])
    result["tfidf_similarity"] = round(role_similarity * 100, 2)
    result["text_skill_matches"] = match_text_to_skills(summary, top_k=8)
    result["score_explanation"] = (
        f"The score is the sum of each required skill's importance weight multiplied by capped level coverage, "
        f"divided by total role weight ({result['total_importance_weight']}) and converted to a percentage. "
        "Text similarity is shown separately and does not change this weighted match percentage."
    )
    return result