"""Evaluate synthetic role ranking and deterministic skill-gap detection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.matching import rank_roles, weighted_skill_overlap
from src.skills_catalog import ROLE_BY_ID


def _ranking_metrics(profiles: pd.DataFrame, method: str) -> dict[str, float]:
    top_one = 0
    top_three = 0
    for _, profile in profiles.iterrows():
        levels = json.loads(profile["skill_levels"])
        ranking = rank_roles(levels, profile["skills_summary"], method=method)
        target = profile["target_role"]
        top_one += int(ranking[0]["role_id"] == target)
        top_three += int(target in {item["role_id"] for item in ranking[:3]})
    count = len(profiles)
    return {"top_1_accuracy": top_one / count, "top_3_accuracy": top_three / count}


def _gap_detection_metrics(profiles: pd.DataFrame) -> dict[str, float]:
    true_positive = false_positive = false_negative = 0
    for _, profile in profiles.iterrows():
        levels = json.loads(profile["skill_levels"])
        role = ROLE_BY_ID[profile["target_role"]]
        truth = {
            requirement["skill_id"]
            for requirement in role["required_skills"]
            if levels.get(requirement["skill_id"], 0) == 0
        }
        result = weighted_skill_overlap(levels, profile["target_role"])
        detected = {item["skill_id"] for item in result["missing_skills"]}
        true_positive += len(truth & detected)
        false_positive += len(detected - truth)
        false_negative += len(truth - detected)
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    return {"precision": precision, "recall": recall}


def evaluate_profiles(profiles: pd.DataFrame) -> dict[str, Any]:
    """Return top-k ranking results and below-requirement detection metrics."""
    required = {"target_role", "skill_levels", "skills_summary"}
    missing = required.difference(profiles.columns)
    if missing:
        raise ValueError(f"Profile data is missing columns: {sorted(missing)}")
    if profiles.empty:
        raise ValueError("Evaluation requires at least one student profile")
    return {
        "profile_count": len(profiles),
        "baseline": _ranking_metrics(profiles, "baseline"),
        "tfidf": _ranking_metrics(profiles, "tfidf"),
        "hybrid": _ranking_metrics(profiles, "hybrid"),
        "gap_detection": _gap_detection_metrics(profiles),
    }


def write_evaluation_report(results: dict[str, Any], output_path: str | Path) -> Path:
    """Write evaluation metrics with an explanation of synthetic ground truth."""
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Skill-gap system evaluation",
        "",
        f"Evaluated synthetic student profiles: **{results['profile_count']}**",
        "",
        "## Role recommendation",
        "",
        "| Method | Top-1 accuracy | Top-3 accuracy |",
        "| --- | ---: | ---: |",
    ]
    for method in ("baseline", "tfidf", "hybrid"):
        metrics = results[method]
        lines.append(
            f"| {method.title()} | {metrics['top_1_accuracy']:.3f} | {metrics['top_3_accuracy']:.3f} |"
        )
    gap = results["gap_detection"]
    lines.extend(
        [
            "",
            "## Skill-gap detection",
            "",
            "| Method | Precision | Recall |",
            "| --- | ---: | ---: |",
            f"| Level-0 missing-skill detection | {gap['precision']:.3f} | {gap['recall']:.3f} |",
            "",
            "## Interpretation and limits",
            "",
            "The baseline ranks roles by weighted level coverage. TF-IDF ranks catalog role descriptions by cosine similarity to the student's free-text summary and assessed skill names; the hybrid combines both scores. Gap detection compares explicit self-assessed levels with the catalog's required levels, so these precision/recall values measure consistent rule application, not an independently learned classifier. All profiles and target-role labels are synthetic and generated from the same catalog assumptions; these results do not establish real-world fit or job readiness.",
            "",
        ]
    )
    destination.write_text("\n".join(lines), encoding="utf-8")
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profiles", default="data/students.csv")
    parser.add_argument("--output", default="docs/evaluation_results.md")
    args = parser.parse_args()
    profiles = pd.read_csv(args.profiles)
    results = evaluate_profiles(profiles)
    path = write_evaluation_report(results, args.output)
    print(f"Wrote evaluation report: {path}")


if __name__ == "__main__":
    main()