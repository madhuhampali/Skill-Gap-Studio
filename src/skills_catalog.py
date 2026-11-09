"""Curated synthetic skill and job-role catalog for explainable matching."""

from __future__ import annotations

from typing import Any


def _skill(
    skill_id: str,
    name: str,
    category: str,
    prerequisites: tuple[str, ...] = (),
    description: str = "",
) -> dict[str, Any]:
    """Build a catalog entry with a concise, actionable learning resource."""
    return {
        "skill_id": skill_id,
        "name": name,
        "category": category,
        "prerequisites": list(prerequisites),
        "description": description or f"Core concepts and practical use of {name}.",
        "learning_resource": f"Study a short {name} tutorial, then complete a small guided practice project.",
    }


SKILLS = [
    _skill("python", "Python", "Programming", description="Write scripts, functions, and data-oriented programs."),
    _skill("r", "R", "Programming"),
    _skill("sql", "SQL", "Data", description="Query and transform structured data with relational databases."),
    _skill("java", "Java", "Programming"),
    _skill("javascript", "JavaScript", "Programming", description="Build interactive web and server-side applications."),
    _skill("typescript", "TypeScript", "Programming", ("javascript",)),
    _skill("csharp", "C#", "Programming"),
    _skill("kotlin", "Kotlin", "Programming"),
    _skill("swift", "Swift", "Programming"),
    _skill("git", "Git", "Developer Tools", description="Track code changes and collaborate with branches and reviews."),
    _skill("linux", "Linux", "Systems"),
    _skill("data_structures", "Data Structures", "Computer Science"),
    _skill("oop", "Object-Oriented Programming", "Computer Science"),
    _skill("statistics", "Statistics", "Mathematics", description="Summarize data, uncertainty, and statistical tests."),
    _skill("probability", "Probability", "Mathematics", ("statistics",)),
    _skill("excel", "Spreadsheets", "Data"),
    _skill("pandas", "Pandas", "Data", ("python",), "Analyze tabular data with Python data frames."),
    _skill("numpy", "NumPy", "Data", ("python",)),
    _skill("data_visualization", "Data Visualization", "Data", description="Communicate patterns with clear charts and dashboards."),
    _skill("tableau", "Tableau", "Data", ("data_visualization",)),
    _skill("power_bi", "Power BI", "Data", ("data_visualization",)),
    _skill("data_cleaning", "Data Cleaning", "Data", ("sql",)),
    _skill("business_analysis", "Business Analysis", "Business"),
    _skill("ab_testing", "A/B Testing", "Data", ("statistics",)),
    _skill("etl", "ETL Pipelines", "Data Engineering", ("sql", "python")),
    _skill("database_design", "Database Design", "Data Engineering", ("sql",)),
    _skill("postgresql", "PostgreSQL", "Data Engineering", ("sql",)),
    _skill("mongodb", "MongoDB", "Data Engineering"),
    _skill("redis", "Redis", "Data Engineering"),
    _skill("data_warehousing", "Data Warehousing", "Data Engineering", ("sql", "database_design")),
    _skill("spark", "Apache Spark", "Data Engineering", ("python", "data_warehousing")),
    _skill("scikit_learn", "Scikit-learn", "Machine Learning", ("python", "statistics", "pandas")),
    _skill("feature_engineering", "Feature Engineering", "Machine Learning", ("pandas", "statistics")),
    _skill("model_evaluation", "Model Evaluation", "Machine Learning", ("statistics", "scikit_learn")),
    _skill("deep_learning", "Deep Learning", "Machine Learning", ("python", "probability")),
    _skill("nlp", "Natural Language Processing", "Machine Learning", ("python", "deep_learning")),
    _skill("cloud", "Cloud Fundamentals", "Cloud", description="Understand cloud regions, identity, storage, and compute."),
    _skill("aws", "AWS", "Cloud", ("cloud",)),
    _skill("azure", "Azure", "Cloud", ("cloud",)),
    _skill("gcp", "Google Cloud", "Cloud", ("cloud",)),
    _skill("docker", "Docker", "DevOps", ("linux",)),
    _skill("kubernetes", "Kubernetes", "DevOps", ("docker", "linux")),
    _skill("ci_cd", "CI/CD", "DevOps", ("git",)),
    _skill("terraform", "Terraform", "DevOps", ("cloud",)),
    _skill("monitoring", "Monitoring and Observability", "DevOps", ("linux",)),
    _skill("networking", "Computer Networking", "Infrastructure"),
    _skill("cybersecurity", "Cybersecurity Fundamentals", "Security", ("networking",)),
    _skill("owasp", "OWASP Web Security", "Security", ("cybersecurity", "javascript")),
    _skill("threat_modeling", "Threat Modeling", "Security", ("cybersecurity",)),
    _skill("siem", "SIEM Analysis", "Security", ("cybersecurity",)),
    _skill("testing", "Software Testing", "Quality Assurance"),
    _skill("pytest", "Pytest", "Quality Assurance", ("python", "testing")),
    _skill("selenium", "Selenium", "Quality Assurance", ("javascript", "testing")),
    _skill("playwright", "Playwright", "Quality Assurance", ("javascript", "testing")),
    _skill("html", "HTML", "Frontend"),
    _skill("css", "CSS", "Frontend", ("html",)),
    _skill("accessibility", "Web Accessibility", "Frontend", ("html",)),
    _skill("react", "React", "Frontend", ("javascript", "html", "css")),
    _skill("ux_design", "UX Design", "Frontend"),
    _skill("rest_api", "REST APIs", "Backend", ("http_basics",)),
    _skill("http_basics", "HTTP Fundamentals", "Backend", ("networking",)),
    _skill("fastapi", "FastAPI", "Backend", ("python", "rest_api")),
    _skill("django", "Django", "Backend", ("python", "rest_api")),
    _skill("nodejs", "Node.js", "Backend", ("javascript",)),
    _skill("express", "Express", "Backend", ("nodejs", "rest_api")),
    _skill("microservices", "Microservices", "Backend", ("rest_api", "docker")),
    _skill("kafka", "Apache Kafka", "Data Engineering", ("python", "data_warehousing")),
    _skill("mobile_design", "Mobile UI Design", "Mobile"),
    _skill("android", "Android Development", "Mobile", ("kotlin",)),
    _skill("ios", "iOS Development", "Mobile", ("swift",)),
    _skill("flutter", "Flutter", "Mobile", ("dart",)),
    _skill("dart", "Dart", "Programming"),
    _skill("agile", "Agile Delivery", "Product"),
    _skill("documentation", "Technical Documentation", "Communication"),
]


def _requirements(*items: tuple[str, int, int]) -> list[dict[str, Any]]:
    return [
        {"skill_id": skill_id, "importance_weight": weight, "required_level": level}
        for skill_id, weight, level in items
    ]


ROLES = [
    {
        "role_id": "data_analyst",
        "name": "Data Analyst",
        "description": "Explore business data, answer questions, and communicate evidence with clear reports.",
        "required_skills": _requirements(("sql", 5, 4), ("statistics", 4, 3), ("excel", 3, 3), ("pandas", 4, 3), ("data_visualization", 5, 4), ("tableau", 4, 3), ("data_cleaning", 4, 3), ("business_analysis", 3, 2), ("ab_testing", 2, 2)),
    },
    {
        "role_id": "ml_engineer",
        "name": "ML Engineer",
        "description": "Build, test, and operationalize machine-learning systems and data products.",
        "required_skills": _requirements(("python", 5, 4), ("scikit_learn", 5, 3), ("feature_engineering", 4, 3), ("model_evaluation", 5, 4), ("sql", 3, 3), ("docker", 4, 3), ("ci_cd", 3, 3), ("cloud", 3, 2), ("data_structures", 3, 3), ("git", 3, 3)),
    },
    {
        "role_id": "backend_developer",
        "name": "Backend Developer",
        "description": "Design server-side applications, APIs, and reliable data services.",
        "required_skills": _requirements(("python", 4, 3), ("rest_api", 5, 4), ("fastapi", 4, 3), ("sql", 4, 3), ("postgresql", 4, 3), ("git", 3, 3), ("testing", 4, 3), ("docker", 3, 2), ("data_structures", 3, 3), ("linux", 2, 2)),
    },
    {
        "role_id": "frontend_developer",
        "name": "Frontend Developer",
        "description": "Build accessible, responsive user interfaces for web applications.",
        "required_skills": _requirements(("html", 5, 4), ("css", 5, 4), ("javascript", 5, 4), ("typescript", 4, 3), ("react", 5, 4), ("accessibility", 4, 3), ("testing", 3, 3), ("git", 3, 3), ("ux_design", 3, 2), ("playwright", 2, 2)),
    },
    {
        "role_id": "devops_engineer",
        "name": "DevOps Engineer",
        "description": "Automate delivery and operate cloud infrastructure with reliable observability.",
        "required_skills": _requirements(("linux", 5, 4), ("cloud", 5, 4), ("docker", 5, 4), ("kubernetes", 4, 3), ("ci_cd", 5, 4), ("terraform", 4, 3), ("monitoring", 4, 3), ("networking", 3, 3), ("git", 3, 3), ("python", 2, 2)),
    },
    {
        "role_id": "cybersecurity_analyst",
        "name": "Cybersecurity Analyst",
        "description": "Monitor systems, investigate security signals, and help reduce technical risk.",
        "required_skills": _requirements(("cybersecurity", 5, 4), ("networking", 5, 4), ("linux", 4, 3), ("siem", 5, 3), ("threat_modeling", 4, 3), ("owasp", 3, 2), ("cloud", 3, 2), ("python", 2, 2), ("documentation", 3, 3)),
    },
    {
        "role_id": "qa_engineer",
        "name": "QA Engineer",
        "description": "Design and automate checks that give teams confidence in software quality.",
        "required_skills": _requirements(("testing", 5, 4), ("pytest", 4, 3), ("selenium", 4, 3), ("playwright", 4, 3), ("javascript", 3, 3), ("python", 3, 3), ("git", 3, 3), ("ci_cd", 3, 2), ("documentation", 2, 3)),
    },
    {
        "role_id": "data_scientist",
        "name": "Data Scientist",
        "description": "Use statistics and machine learning to model patterns and communicate findings.",
        "required_skills": _requirements(("python", 5, 4), ("statistics", 5, 4), ("probability", 4, 3), ("pandas", 4, 4), ("numpy", 3, 3), ("scikit_learn", 5, 4), ("data_visualization", 3, 3), ("feature_engineering", 4, 3), ("model_evaluation", 5, 4), ("sql", 3, 3)),
    },
    {
        "role_id": "full_stack_developer",
        "name": "Full-Stack Developer",
        "description": "Deliver features across browser interfaces, APIs, and persistent data stores.",
        "required_skills": _requirements(("javascript", 5, 4), ("html", 4, 3), ("css", 4, 3), ("react", 4, 3), ("nodejs", 4, 3), ("express", 4, 3), ("rest_api", 4, 3), ("sql", 3, 2), ("git", 3, 3), ("testing", 3, 3)),
    },
    {
        "role_id": "mobile_developer",
        "name": "Mobile Developer",
        "description": "Create mobile applications with usable interfaces and platform-aware features.",
        "required_skills": _requirements(("kotlin", 4, 3), ("android", 5, 4), ("swift", 4, 3), ("ios", 5, 4), ("flutter", 4, 3), ("dart", 3, 3), ("mobile_design", 4, 3), ("git", 3, 3), ("testing", 3, 3), ("api_basics", 3, 2)),
    },
]

# The catalog contains a few cross-platform skills shared by multiple roles.
SKILLS.extend(
    [
        _skill("api_basics", "API Integration", "Mobile", ("rest_api",)),
    ]
)

SKILL_BY_ID = {skill["skill_id"]: skill for skill in SKILLS}
SKILL_ID_BY_NAME = {skill["name"].casefold(): skill["skill_id"] for skill in SKILLS}
ROLE_BY_ID = {role["role_id"]: role for role in ROLES}
ROLE_ID_BY_NAME = {role["name"].casefold(): role["role_id"] for role in ROLES}


def get_role(role_key: str) -> dict[str, Any]:
    """Resolve a role by stable ID or display name."""
    normalized = role_key.strip().casefold()
    role_id = normalized if normalized in ROLE_BY_ID else ROLE_ID_BY_NAME.get(normalized)
    if role_id is None:
        raise ValueError(f"Unknown role: {role_key}")
    return ROLE_BY_ID[role_id]


def get_skill(skill_id: str) -> dict[str, Any]:
    """Return a skill entry by stable ID."""
    try:
        return SKILL_BY_ID[skill_id]
    except KeyError as error:
        raise ValueError(f"Unknown skill: {skill_id}") from error