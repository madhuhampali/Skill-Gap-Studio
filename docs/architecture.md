# Architecture

```mermaid
flowchart LR
    A[Seeded synthetic profile generator] --> B[CSV profiles and catalog JSON]
    C[Skill and role catalog] --> D[Weighted overlap matching]
    C --> E[TF-IDF and cosine similarity]
    B --> F[FastAPI and Streamlit]
    D --> F
    E --> F
    F --> G[Explainable gap report]
    C --> H[Prerequisite graph]
    H --> I[Ranked learning pathway]
    D --> I
    I --> G
    B --> J[Evaluation]
    D --> J
    E --> J
    J --> K[Markdown evaluation report]
```

The weighted score uses only student skill levels and each target role's importance/required-level values. TF-IDF cosine similarity is a separate text signal, and is combined only in the explicit hybrid role-ranking mode. Recommendations traverse skill prerequisites before dependent items and attach a reason and learning resource to every step. All generated student records are synthetic.
