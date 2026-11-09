from src.matching import analyze_student, weighted_skill_overlap
from src.skills_catalog import ROLE_BY_ID


def test_weighted_score_is_full_for_exact_requirements_and_gaps_are_empty():
    role = ROLE_BY_ID["data_analyst"]
    levels = {item["skill_id"]: item["required_level"] for item in role["required_skills"]}

    result = weighted_skill_overlap(levels, "data_analyst")

    assert result["match_percentage"] == 100.0
    assert len(result["matched_skills"]) == len(role["required_skills"])
    assert result["missing_skills"] == []
    assert result["weak_skills"] == []


def test_gap_detection_distinguishes_missing_from_weak():
    result = weighted_skill_overlap({"sql": 1}, "data_analyst")

    assert any(item["skill_id"] == "sql" for item in result["weak_skills"])
    assert any(item["skill_id"] == "statistics" for item in result["missing_skills"])
    assert result["match_percentage"] < 100


def test_analysis_explains_score_and_separates_text_signal():
    result = analyze_student(
        {"python": 3, "pandas": 2},
        role_key="data_analyst",
        summary="I use Python for data analysis",
    )

    assert "importance weight" in result["score_explanation"]
    assert 0 <= result["tfidf_similarity"] <= 100
    assert result["text_skill_matches"]
