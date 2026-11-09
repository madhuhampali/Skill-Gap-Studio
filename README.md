# AI-Based Student Skill Gap Analysis System

A local learning-planning tool that compares a skill assessment with the requirements of a selected job role. It reports a transparent weighted match, separates missing from below-level skills, and produces a prerequisite-aware pathway with an explanation and resource for every recommendation.

Only generated synthetic student profiles are included. Do not load personal student data. This is a skills-planning aid, not a measure of a person's potential, job readiness, or employment suitability.

## Requirements

- Python 3.10 or newer
- Dependencies in `requirements.txt`

## Setup and run order

Run setup from the project root in PowerShell. Start the API and dashboard in separate terminals so both remain available. The commands below follow the requested order.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m src.generate_data
python -m src.evaluate
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
streamlit run app/dashboard.py
python -m pytest
```

The API is documented at `http://127.0.0.1:8000/docs`. Evaluation writes `docs/evaluation_results.md`. Run servers in separate terminals; run tests from a third terminal or after stopping them.

## Components

- `src/skills_catalog.py`: 75 skills, 10 roles, requirement weights/levels, prerequisites, and learning resources.
- `src/generate_data.py`: seeded synthetic catalog/profile files in `data/`.
- `src/matching.py`: weighted overlap, skill-text TF-IDF similarity, and baseline/TF-IDF/hybrid role rankings.
- `src/recommend.py`: role gap priorities and prerequisite-ordered explainable pathway.
- `src/evaluate.py`: top-1/top-3 role ranking accuracy, missing-skill precision/recall, and method comparison.
- `api/main.py`: FastAPI catalog, analysis, and role-recommendation endpoints.
- `app/dashboard.py`: resume upload, synthetic profile selection, or custom assessment; Plotly radar/gap charts, explanation panel, pathway, PDF and CSV exports.
- `src/resume_parser.py`: in-memory PDF, DOCX, and TXT extraction with skill evidence and editable proficiency suggestions.

## Screenshots

Add screenshots of the profile selection, match analysis, and learning pathway here after launching the dashboard.

## Limitations

- Student profiles and target-role labels are synthetic; evaluation is not evidence of performance on real learners or jobs.
- The catalog contains only 75 skills and 10 example roles, and cannot represent the full range of industries, seniority, or local requirements.
- Importance weights, required levels, prerequisite links, and generated profiles are simplified assumptions.
- TF-IDF is a lightweight lexical baseline; it does not understand nuanced descriptions, proficiency evidence, or transferable skills.
- Resume parsing only recognizes catalog skill names and selected aliases in selectable text. It does not OCR scanned PDFs, and proficiency levels are rough wording-based suggestions that users must review. Uploads are processed in memory and are not saved by this app.
- The reported percentage is weighted level coverage, not probability of hiring or success. Recommendations should be reviewed and adapted by the learner.

## Tests

Run `python -m pytest` from the project root. Tests cover deterministic synthetic generation, score and gap behavior, prerequisite ordering, resume extraction/inference, and API responses/input validation.
