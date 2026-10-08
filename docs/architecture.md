# Architecture

## 1. System overview

AI Job Intelligence is a full-stack application for analyzing how closely a resume matches a job posting.

The core pipeline is:

```text
Resume
  ↓
Resume Parser
  ↓
Structured Resume Data
  ↓
Job Parser
  ↓
Structured Job Data
  ↓
Requirement Builder
  ↓
Required / Technology / Preferred Requirements
  ↓
Embedding Generation
  ↓
pgvector Semantic Retrieval
  ↓
Relevant Resume Evidence
  ↓
Gemini Semantic Evaluation
  ↓
Deterministic Scoring Service
  ↓
Match Analysis
  ↓
FastAPI
  ↓
React Dashboard
```

## 2. Requirement builder

The requirement builder is a key boundary between raw job content and evaluation.

It produces categories such as:

```text
required_requirements
technology_requirements
preferred_requirements
```

This allows the scoring layer to distinguish important requirements from optional preferences.

## 3. Semantic evidence retrieval

Exact keyword matching is insufficient for resume/job matching.

The platform therefore creates vector embeddings for relevant text and stores them in PostgreSQL using pgvector.

The retrieval layer finds resume content that is semantically related to a job requirement.

Conceptually:

```text
Job requirement
      ↓
Embedding
      ↓
Vector similarity search
      ↓
Relevant resume evidence
```

The database uses an HNSW vector index to make similarity retrieval practical as the number of stored vectors grows.

## 4. LLM evaluation

Retrieved evidence is supplied to the semantic evaluation layer.

Gemini is responsible for reasoning about whether the candidate's experience actually satisfies a requirement.

The LLM is therefore used for semantic interpretation rather than blindly generating the final score.

## 5. Deterministic scoring

The scoring service acts as the single source of truth for the final score.

The general responsibility is:

```text
semantic evaluation
        +
requirement category/weight
        ↓
deterministic scoring
        ↓
score breakdown
        ↓
final score
```

This separation means the scoring behavior can be tested independently of the LLM.

## 6. Fallback behavior

External LLM calls can fail because of:

- temporary service failures
- API availability problems
- rate limits
- configuration problems

The application includes local fallback analysis so that the matching workflow has a non-LLM path for degraded operation.

This is an important reliability boundary:

```text
                 ┌── Gemini semantic evaluation
Requirement ─────┤
                 └── Local fallback evaluator
                         ↓
                  Scoring Service
```

## 7. Backend

The backend is implemented with FastAPI and is responsible for:

- authentication
- resume management
- job extraction
- requirement processing
- match analysis
- scoring
- persistence
- API responses

The backend is containerized and listens internally on port 8000 in production.

## 8. Frontend

The React frontend provides the user workflow:

```text
Login
  ↓
Resume
  ↓
Job URL
  ↓
Job extraction
  ↓
Match analysis
  ↓
Results
  ↓
Match history
```

Production frontend assets are built with Node and served by Nginx.

## 9. Production request flow

```text
Browser
  ↓
EC2 :80
  ↓
Nginx frontend container
  ├── static React files
  │
  └── /api/*
          ↓
     backend:8000
          ↓
      PostgreSQL/RDS
```

The backend does not need to expose port 8000 publicly.

## 10. AWS architecture

The production deployment uses:

- EC2 for the application host
- RDS PostgreSQL for persistent relational/vector data
- S3 for object storage where required
- VPC networking
- Security groups
- IAM
- AWS Systems Manager
- Elastic IP
- Terraform

The database is kept private and accepts database traffic from the application security group.

## 11. CI/CD architecture

```text
Developer
   ↓
git push origin main
   ↓
GitHub Actions
   ↓
GitHub OIDC
   ↓
AWS IAM deployment role
   ↓
SSM SendCommand
   ↓
EC2
   ↓
scripts/deploy.sh
   ↓
git fetch/reset
   ↓
Docker build
   ↓
Docker Compose
```

No long-lived AWS access key is required in GitHub Actions; authentication is based on OIDC and the AWS IAM role.

## 12. Design principles

### Separation of concerns

Parsing, retrieval, AI reasoning, scoring, API handling, and presentation are separate responsibilities.

### Explainability

Every final score should be understandable in terms of individual requirements and evaluation results.

### Controlled use of AI

The LLM is used where semantic reasoning is valuable. Deterministic application code controls scoring behavior.

### Reliability

The system includes a local fallback path so that external AI-service failures do not automatically make the entire analysis unusable.
