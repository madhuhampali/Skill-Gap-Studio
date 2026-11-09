# Skill-gap system evaluation

Evaluated synthetic student profiles: **500**

## Role recommendation

| Method | Top-1 accuracy | Top-3 accuracy |
| --- | ---: | ---: |
| Baseline | 0.910 | 0.990 |
| Tfidf | 0.530 | 0.914 |
| Hybrid | 0.926 | 0.996 |

## Skill-gap detection

| Method | Precision | Recall |
| --- | ---: | ---: |
| Level-0 missing-skill detection | 1.000 | 1.000 |

## Interpretation and limits

The baseline ranks roles by weighted level coverage. TF-IDF ranks catalog role descriptions by cosine similarity to the student's free-text summary and assessed skill names; the hybrid combines both scores. Gap detection compares explicit self-assessed levels with the catalog's required levels, so these precision/recall values measure consistent rule application, not an independently learned classifier. All profiles and target-role labels are synthetic and generated from the same catalog assumptions; these results do not establish real-world fit or job readiness.
