"""Build explainable, prerequisite-aware learning pathways."""

from __future__ import annotations

import heapq
from typing import Any, Mapping

from src.matching import normalize_skill_levels
from src.skills_catalog import ROLE_BY_ID, ROLES, SKILL_BY_ID


def recommend_learning_pathway(
    skill_levels: Mapping[str, int | float], role_key: str
) -> list[dict[str, Any]]:
    """Rank role gaps and insert low-level prerequisites before dependent skills."""
    levels = normalize_skill_levels(skill_levels)
    role_id = role_key if role_key in ROLE_BY_ID else next(
        (role["role_id"] for role in ROLES if role["name"].casefold() == role_key.strip().casefold()), None
    )
    if role_id is None:
        raise ValueError(f"Unknown role: {role_key}")
    role = ROLE_BY_ID[role_id]
    targets = {
        item["skill_id"]: {
            "required_level": item["required_level"],
            "importance_weight": item["importance_weight"],
            "direct_requirement": True,
        }
        for item in role["required_skills"]
    }

    def add_prerequisites(skill_id: str, inherited_weight: int) -> None:
        for prerequisite_id in SKILL_BY_ID[skill_id]["prerequisites"]:
            if levels.get(prerequisite_id, 0) >= 2:
                continue
            current = targets.get(prerequisite_id)
            if current is None:
                targets[prerequisite_id] = {
                    "required_level": 2,
                    "importance_weight": inherited_weight,
                    "direct_requirement": False,
                    "dependent_skill": skill_id,
                }
            else:
                current["importance_weight"] = max(current["importance_weight"], inherited_weight)
            add_prerequisites(prerequisite_id, inherited_weight)

    for requirement in role["required_skills"]:
        if levels.get(requirement["skill_id"], 0) < requirement["required_level"]:
            add_prerequisites(requirement["skill_id"], requirement["importance_weight"])

    candidates = {
        skill_id: target
        for skill_id, target in targets.items()
        if levels.get(skill_id, 0) < target["required_level"]
    }
    dependencies: dict[str, set[str]] = {skill_id: set() for skill_id in candidates}
    dependents: dict[str, set[str]] = {skill_id: set() for skill_id in candidates}
    for skill_id in candidates:
        for prerequisite_id in SKILL_BY_ID[skill_id]["prerequisites"]:
            if prerequisite_id in candidates:
                dependencies[skill_id].add(prerequisite_id)
                dependents[prerequisite_id].add(skill_id)

    def priority(skill_id: str) -> tuple[int, int, str]:
        target = candidates[skill_id]
        gap = target["required_level"] - levels.get(skill_id, 0)
        return (-target["importance_weight"] * gap, -gap, skill_id)

    ready = [(priority(skill_id), skill_id) for skill_id, deps in dependencies.items() if not deps]
    heapq.heapify(ready)
    ordered: list[str] = []
    while ready:
        _, skill_id = heapq.heappop(ready)
        ordered.append(skill_id)
        for dependent in dependents[skill_id]:
            dependencies[dependent].remove(skill_id)
            if not dependencies[dependent]:
                heapq.heappush(ready, (priority(dependent), dependent))

    pathway: list[dict[str, Any]] = []
    for position, skill_id in enumerate(ordered, start=1):
        target = candidates[skill_id]
        skill = SKILL_BY_ID[skill_id]
        current = levels.get(skill_id, 0)
        required = target["required_level"]
        kind = "missing" if current == 0 else "weak"
        if target.get("direct_requirement"):
            reason = (
                f"Required for {role['name']} (weight {target['importance_weight']}); "
                f"you are at level {current}, need level {required}."
            )
        else:
            dependent_name = SKILL_BY_ID[target["dependent_skill"]]["name"]
            reason = (
                f"Foundation for {dependent_name}, which is required for {role['name']}; "
                f"you are at level {current}, need level {required} before progressing."
            )
        pathway.append(
            {
                "step": position,
                "skill_id": skill_id,
                "skill_name": skill["name"],
                "category": skill["category"],
                "current_level": current,
                "target_level": required,
                "gap_size": required - current,
                "importance_weight": target["importance_weight"],
                "status": kind,
                "reason": reason,
                "prerequisites": skill["prerequisites"],
                "learning_resource": skill["learning_resource"],
            }
        )
    return pathway