import json

from src.generate_data import generate_profiles
from src.skills_catalog import ROLES, SKILLS


def test_catalog_and_generator_are_reproducible():
    first = generate_profiles(n_students=50, seed=29)
    second = generate_profiles(n_students=50, seed=29)

    assert 60 <= len(SKILLS) <= 80
    assert len(ROLES) == 10
    assert first.equals(second)
    assert len(first) == 50
    profile = json.loads(first.iloc[0]["skill_levels"])
    assert len(profile) == len(SKILLS)
    assert all(0 <= level <= 5 for level in profile.values())
    assert first["skills_summary"].str.len().gt(0).all()
