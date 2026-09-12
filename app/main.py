from fastapi import FastAPI
from sqlalchemy import text
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.resumes import router as resumes_router
from app.api.v1.resume_analysis import router as resume_analysis
from app.api.v1.jobs import router as jobs_router
from app.api.v1.matches import router as matches_router
from app.api.v1.job_analysis import router as job_analysis_router
from app.api.v1 import hybrid_match
from app.api.v1 import semantic_match
from app.api.v1 import match_analysis
from app.api.v1.analysis_status import router as analysis_status_router

from app.db.base import Base
from app.db.session import engine
from app.models import User, Resume, Job, MatchAnalysis, JobAnalysis
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Job Intelligence API",
    description="AI-powered job discovery and matching platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/health/database")
def database_health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }
    

app.include_router(
    auth_router,
    prefix="/api/v1"
)
app.include_router(
    users_router,
    prefix="/api/v1"
)
app.include_router(
    resumes_router,
    prefix="/api/v1"
)
app.include_router(
    resume_analysis,
    prefix="/api/v1"
)
app.include_router(
    jobs_router,
    prefix="/api/v1"
)
app.include_router(
    matches_router,
    prefix="/api/v1"
)
app.include_router(
    job_analysis_router,
    prefix="/api/v1"
)
app.include_router(
    hybrid_match.router,
    prefix="/api/v1"
)
app.include_router(
    semantic_match.router,
    prefix="/api/v1"
)
app.include_router(
    match_analysis.router,
    prefix="/api/v1"
)


app.include_router(
    analysis_status_router,
    prefix="/api/v1"
)
