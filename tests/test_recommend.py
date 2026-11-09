from src.recommend import recommend_learning_pathway
from src.skills_catalog import ROLE_BY_ID


def test_prerequisites_appear_before_dependent_skills():
    pathway = recommend_learning_pathway({}, "ml_engineer")
    positions = {item["skill_id"]: item["step"] for item in pathway}

    assert positions["python"] < positions["pandas"]
    assert positions["pandas"] < positions["scikit_learn"]
    assert positions["statistics"] < positions["scikit_learn"]
    assert all(item["reason"] and item["learning_resource"] for item in pathway)


def test_pathway_prioritizes_role_gaps_and_explains_level_requirement():
    pathway = recommend_learning_pathway({"sql": 1}, "data_analyst")
    sql_step = next(item for item in pathway if item["skill_id"] == "sql")

    assert sql_step["status"] == "weak"
    assert "weight 5" in sql_step["reason"]
    assert "level 1, need level 4" in sql_step["reason"]


def test_does_not_recommend_missing_prerequisite_for_mastered_skill():
    levels = {
        item["skill_id"]: item["required_level"]
        for item in ROLE_BY_ID["data_analyst"]["required_skills"]
    }
    levels["python"] = 0

    pathway = recommend_learning_pathway(levels, "data_analyst")

    assert pathway == []
