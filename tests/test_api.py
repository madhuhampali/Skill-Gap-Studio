from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_catalog_endpoints_return_roles_and_skills():
    roles = client.get("/roles")
    skills = client.get("/skills")

    assert roles.status_code == 200
    assert len(roles.json()) == 10
    assert skills.status_code == 200
    assert len(skills.json()) >= 60


def test_analyze_returns_match_gaps_and_explainable_pathway():
    response = client.post(
        "/analyze",
        json={"skills": {"python": 2, "sql": 1}, "target_role": "data_analyst", "skills_summary": "I have practiced Python and SQL."},
    )

    assert response.status_code == 200
    body = response.json()
    assert 0 <= body["match_percentage"] <= 100
    assert body["missing_skills"] and body["weak_skills"]
    assert body["learning_pathway"][0]["reason"]


def test_recommend_roles_and_reject_invalid_input():
    recommendation = client.post("/recommend-roles", json={"skills": {"python": 4}, "skills_summary": "Python scripts"})
    invalid_level = client.post("/recommend-roles", json={"skills": {"python": 8}})
    fractional_level = client.post("/recommend-roles", json={"skills": {"python": 2.5}})
    invalid_role = client.post("/analyze", json={"skills": {}, "target_role": "not a role"})

    assert recommendation.status_code == 200
    assert len(recommendation.json()["hybrid"]) == 10
    assert invalid_level.status_code == 422
    assert fractional_level.status_code == 422
    assert invalid_role.status_code == 422
