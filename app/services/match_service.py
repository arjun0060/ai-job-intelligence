from uuid import UUID

from sqlalchemy.orm import Session

from app.models.job import Job
from app.models.match_analysis import MatchAnalysis
from app.services.match_analysis_service import (
    MatchAnalysisService,
)


class MatchService:

    def analyze_match(
        self,
        db: Session,
        resume_id: UUID,
        job_id: int,
    ) -> dict:

        existing_match = (
            db.query(MatchAnalysis)
            .filter(
                MatchAnalysis.resume_id == resume_id,
                MatchAnalysis.job_id == job_id,
            )
            .first()
        )

        if existing_match:
            match = existing_match

        else:
            match = MatchAnalysisService.analyze_and_save(
                db=db,
                resume_id=resume_id,
                job_id=job_id,
            )

        job = (
            db.query(Job)
            .filter(
                Job.id == job_id
            )
            .first()
        )

        if not job:
            raise ValueError("Job not found")

        return {
            "id": match.id,
            "resume_id": match.resume_id,
            "job_id": match.job_id,
            "overall_match_score": match.overall_match_score,
            "analysis_data": match.analysis_data,
            "job": job,
            "created_at": match.created_at,
            "updated_at": match.updated_at,
        }