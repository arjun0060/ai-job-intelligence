# Scoring and Evaluation

## Purpose

The scoring system evaluates a candidate against individual job requirements and produces an explainable overall match result.

The key design decision is to separate **semantic reasoning** from **final scoring**.

## Evaluation pipeline

```text
Job requirement
      ↓
Retrieve relevant resume evidence
      ↓
Semantic evaluation
      ↓
Requirement-level result
      ↓
Deterministic score
      ↓
Aggregated match score
```

## Why not let the LLM generate the final score?

A pure LLM-generated score can be difficult to reproduce and debug.

For example, the same candidate and job could potentially receive different scores depending on wording or model behavior.

The platform therefore uses Gemini for semantic interpretation and application code for deterministic scoring.

## Requirement-level analysis

Each requirement is evaluated independently.

The evaluator considers whether the resume contains evidence supporting the requirement.

The result can then be represented as a requirement-level assessment containing information such as:

- requirement
- category
- semantic assessment
- supporting evidence
- match status
- score contribution

This creates a traceable path from the job requirement to the final result.

## Evidence retrieval

The retrieval layer uses sentence-transformer embeddings and pgvector semantic search.

The purpose is to find evidence even when the resume does not use exactly the same wording as the job description.

For example:

```text
Job:
"Experience building RESTful backend services"

Resume:
"Developed production APIs using FastAPI and PostgreSQL"
```

Semantic retrieval can identify the second statement as relevant evidence even though the wording differs.

## Requirement categories

The requirement builder distinguishes between requirement types, including:

- required requirements
- technology requirements
- preferred requirements

This allows the scoring service to treat core qualifications differently from optional preferences.

## Deterministic scoring

The scoring service converts requirement-level evaluation results into a consistent score.

The important property is that the aggregation logic lives in application code rather than inside the LLM.

Conceptually:

```text
Requirement A → score contribution
Requirement B → score contribution
Requirement C → score contribution
...
                    ↓
            deterministic aggregation
                    ↓
              final score
```

## Explainability

The result should allow a user to understand:

- what matched
- what partially matched
- what was missing
- which resume evidence supported the match
- how individual requirements contributed to the result

This is more useful than returning a single unexplained percentage.

## LLM fallback

When Gemini cannot be used, the application can use local fallback analysis.

Fallback behavior is intentionally less dependent on an external AI service and is intended to keep the workflow operational during service failures or rate limits.

The fallback should not be described as equivalent to full semantic LLM reasoning; it is a degraded but useful analysis path.

## Testing the scoring layer

The scoring service should be testable independently from the Gemini service.

This makes it possible to verify deterministic behavior with unit tests and to avoid making external AI calls for every test.

The project test suite was brought to a passing state with 80 automated tests.
