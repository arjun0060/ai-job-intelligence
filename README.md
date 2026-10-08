# AI Job Intelligence

An AI-powered resume-to-job matching platform that analyzes a candidate's resume against a job posting and produces requirement-level match intelligence, strengths, gaps, evidence, and an explainable score.

## What the system does

The platform follows this flow:

```text
Resume
  ↓
Resume Parser
  ↓
Job Parser
  ↓
Requirement Extraction
  ↓
Semantic Evaluation
  ↓
Deterministic Scoring Engine
  ↓
Match Analysis API
  ↓
React Dashboard
```

The system combines LLM-based semantic reasoning with deterministic scoring so that the final result is explainable and reproducible rather than being an opaque LLM-generated number.

## Key capabilities

- Resume upload and parsing
- Job posting extraction
- Requirement-level analysis
- Technology/skill requirement extraction
- Preferred vs. required requirement separation
- Semantic evidence retrieval using embeddings
- PostgreSQL + pgvector vector search
- Gemini-based semantic evaluation
- Deterministic scoring
- Explainable score breakdown
- Strength and gap analysis
- Local fallback analysis when the Gemini service is unavailable or rate-limited
- FastAPI REST backend
- React dashboard
- Automated tests
- Dockerized deployment
- Terraform-managed AWS infrastructure
- GitHub Actions CI/CD

## My Contribution

I designed and built the platform end-to-end. My work covered the backend architecture, resume and job parsing, requirement extraction, embedding generation, pgvector semantic search, evidence retrieval, Gemini integration, deterministic scoring engine, REST APIs, React dashboard, automated testing, Dockerization, Terraform infrastructure, AWS deployment, and GitHub Actions CI/CD.

I also designed the hybrid evaluation architecture so that the LLM provides semantic reasoning while the final scoring remains deterministic and explainable. I implemented local fallback analysis for cases where the Gemini service is unavailable or rate-limited.

| Area | Contribution |
|---|---|
| Backend | FastAPI application and service architecture |
| Parsing | Resume and job-posting extraction |
| AI | Gemini semantic evaluation and reasoning |
| Retrieval | Sentence-transformer embeddings, pgvector and HNSW search |
| Scoring | Deterministic requirement-level scoring |
| Evidence | Semantic evidence retrieval from candidate content |
| Frontend | React dashboard and match-analysis views |
| Testing | Automated API/unit testing with Pytest and Schemathesis |
| Infrastructure | Terraform-managed AWS infrastructure |
| Deployment | Docker, Docker Compose, GitHub Actions, OIDC and AWS SSM |
| Reliability | Local fallback analysis for unavailable AI services |

## Architecture

The application is intentionally split into clear responsibilities:

- **Parsing layer** converts resumes and job postings into structured data.
- **Requirement builder** identifies required, technology, and preferred requirements.
- **Embedding/retrieval layer** finds semantically relevant resume evidence.
- **LLM evaluator** performs semantic reasoning over requirements and retrieved evidence.
- **Scoring service** converts evaluation results into deterministic, explainable scores.
- **API layer** exposes the workflow to the frontend.
- **React frontend** presents the analysis and match history.

See [`docs/architecture.md`](docs/architecture.md).

## Scoring philosophy

The LLM is not treated as the sole source of truth for the final score.

The evaluation is designed as:

```text
Requirement
    ↓
Relevant resume evidence
    ↓
Semantic evaluation
    ↓
Deterministic scoring
    ↓
Score breakdown
    ↓
Final match score
```

This makes the output easier to explain, test, debug, and change.

See [`docs/scoring.md`](docs/scoring.md).

## Technology stack

### Backend
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- pgvector
- Pydantic

### AI / Retrieval
- Google Gemini
- Sentence Transformers
- Vector embeddings
- Semantic similarity search
- pgvector HNSW indexing

### Frontend
- React
- Vite
- Nginx

### Infrastructure / DevOps
- AWS EC2
- AWS RDS PostgreSQL
- AWS S3
- AWS VPC
- AWS IAM
- AWS SSM
- Docker
- Docker Compose
- Terraform
- GitHub Actions
- GitHub OIDC

### Testing
- Pytest
- Schemathesis
- Postman

## Deployment

Production deployment uses:

```text
Git push to main
      ↓
GitHub Actions
      ↓
GitHub OIDC authentication
      ↓
AWS IAM role
      ↓
AWS SSM SendCommand
      ↓
EC2 deployment script
      ↓
Docker image builds
      ↓
Docker Compose
      ↓
Frontend + Backend
```

The backend is intentionally not exposed directly to the internet. Nginx serves the React application and proxies `/api/` requests to the backend over the Docker network.

See [`docs/deployment.md`](docs/deployment.md).

## Local development

### Backend

Create and activate a virtual environment, install the project dependencies, configure the environment variables, and start FastAPI with Uvicorn.

Example:

```bash
uvicorn app.main:app --reload
```

### Frontend

```bash
npm install
npm run dev
```

### Docker

The repository contains separate container definitions for the backend and frontend.

Production uses:

```bash
docker compose -f docker-compose.prod.yml up -d
```

## Environment variables

Copy the example environment file and provide the required local values:

```bash
cp .env.example .env
```

Do not commit real credentials, API keys, database passwords, or other secrets.

## Testing

The project includes automated backend/API tests. The test suite was brought to a passing state with 80 tests.

Typical commands:

```bash
pytest
```

For API contract/property testing:

```bash
schemathesis run http://127.0.0.1:8000/openapi.json
```

Authentication or protected endpoints may require the appropriate test configuration.

## Production considerations

The deployment is designed as a practical, cost-conscious AWS setup rather than an unnecessarily large architecture.

Current architecture separates:

- public application access through EC2
- private PostgreSQL access through RDS
- application and database security groups
- infrastructure management through Terraform
- deployment through GitHub Actions and AWS SSM

The EC2 application host uses Docker Compose to run the frontend and backend containers.

## Project structure

```text
ai-job-intelligence/
├── app/
│   ├── api/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── frontend/
├── scripts/
│   └── deploy.sh
├── terraform/
├── tests/
├── Dockerfile
├── docker-compose.prod.yml
├── .dockerignore
├── requirements.docker.txt
├── .env.example
└── README.md
```

## Design ownership

The important engineering decisions in this project were made around three goals:

1. **Useful AI reasoning** — semantic matching should understand meaning rather than rely only on exact keyword matches.
2. **Explainability** — the final score should be traceable to individual requirements and evidence.
3. **Operational reliability** — the application should continue to provide useful behavior when an external AI service is unavailable.

The resulting architecture therefore uses AI where semantic reasoning adds value and deterministic application logic where consistency and explainability matter.

## Status

The platform has been containerized, provisioned on AWS with Terraform, and connected to an automated GitHub Actions deployment workflow using AWS OIDC and SSM.
