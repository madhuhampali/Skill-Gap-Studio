"""Generate seeded synthetic student profiles and publish catalog files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.skills_catalog import ROLES, SKILLS


def generate_profiles(n_students: int = 500, seed: int = 42) -> pd.DataFrame:
    """Create synthetic skill assessments with a known target-role label."""
    if n_students < 10:
        raise ValueError("n_students must be at least 10")
    rng = np.random.default_rng(seed)
    skill_by_id = {skill["skill_id"]: skill for skill in SKILLS}
    records: list[dict[str, object]] = []

    for index in range(n_students):
        role = ROLES[index % len(ROLES)]
        required = {item["skill_id"]: item for item in role["required_skills"]}
        levels: dict[str, int] = {}
        for skill in SKILLS:
            requirement = required.get(skill["skill_id"])
            center = requirement["required_level"] - 0.7 if requirement else 1.1
            center += (requirement["importance_weight"] - 3) * 0.12 if requirement else 0
            levels[skill["skill_id"]] = int(np.clip(round(rng.normal(center, 1.15)), 0, 5))

        strongest = sorted(required, key=lambda key: (-levels[key], key))[:4]
        skill_names = [skill_by_id[skill_id]["name"] for skill_id in strongest]
        summary_templates = [
            f"I have practiced {skill_names[0]} and {skill_names[1]} in small projects.",
            f"My recent learning includes {skill_names[2]} and {skill_names[3]}.",
            "I want to apply these skills in collaborative projects.",
        ]
        records.append(
            {
                "student_id": f"SYN{index + 1:04d}",
                "target_role": role["role_id"],
                "skill_levels": json.dumps(levels, sort_keys=True),
                "skills_summary": " ".join(summary_templates),
            }
        )
    return pd.DataFrame(records)


def write_synthetic_data(output_dir: str | Path = "data", seed: int = 42) -> dict[str, Path]:
    """Write skills, roles, and default student profiles to data/."""
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    skills_path = destination / "skills.csv"
    roles_path = destination / "roles.json"
    profiles_path = destination / "students.csv"
    pd.DataFrame(SKILLS).to_csv(skills_path, index=False)
    roles_path.write_text(json.dumps(ROLES, indent=2), encoding="utf-8")
    generate_profiles(seed=seed).to_csv(profiles_path, index=False)
    return {"skills": skills_path, "roles": roles_path, "students": profiles_path}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="data")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    for name, path in write_synthetic_data(args.output_dir, args.seed).items():
        print(f"Wrote synthetic {name}: {path}")


if __name__ == "__main__":
    main()
