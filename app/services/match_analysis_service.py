from sqlalchemy.orm import Session

from app.models.match_analysis import MatchAnalysis

from app.services.hybrid_match_service import (
    HybridMatchService
)
from app.services.scoring_service import ScoringService

from app.models.job import Job


class MatchAnalysisService:

    @classmethod
    def analyze_and_save(
        cls,
        db: Session,
        resume_id,
        job_id,
    ) -> MatchAnalysis:

        # ---------------------------------
        # Run hybrid analysis
        # ---------------------------------

        analysis_result = HybridMatchService.analyze(
            db=db,
            resume_id=resume_id,
            job_id=job_id,
        )

        # ---------------------------------
        # Check existing analysis
        # ---------------------------------

        existing_analysis = (
            db.query(MatchAnalysis)
            .filter(
                MatchAnalysis.resume_id == resume_id,
                MatchAnalysis.job_id == job_id,
            )
            .first()
        )

        # ---------------------------------
        # Update existing analysis
        # ---------------------------------

        if existing_analysis:

            existing_analysis.overall_match_score = (
                analysis_result.get(
                    "overall_score",
                    0,
                )
            )

            existing_analysis.analysis_data = (
                analysis_result
            )

            db.commit()

            db.refresh(
                existing_analysis
            )

            return existing_analysis

        # ---------------------------------
        # Create new analysis
        # ---------------------------------

        match_analysis = MatchAnalysis(

            resume_id=resume_id,

            job_id=job_id,

            overall_match_score=(
                analysis_result.get(
                    "overall_score",
                    0,
                )
            ),

            analysis_data=analysis_result,
        )

        db.add(
            match_analysis
        )

        db.commit()

        db.refresh(
            match_analysis
        )

        return match_analysis


    @staticmethod
    def recalculate_match_score(
        match,
    ):
        analysis_data = match.analysis_data

        scoring_result = (
            ScoringService.calculate_final_score(
                required_requirements=
                    analysis_data.get(
                        "required_requirements",
                        [],
                    ),

                preferred_requirements=
                    analysis_data.get(
                        "preferred_requirements",
                        [],
                    ),

                technology_requirements=
                    analysis_data.get(
                        "technology_requirements",
                        [],
                    ),
            )
        )

        # Update analysis data
        analysis_data.update(
            scoring_result
        )

        # Update database model
        match.analysis_data = analysis_data

        match.overall_match_score = (
            scoring_result["overall_score"]
        )

        return match

    @classmethod
    def get_match(
        cls,
        db: Session,
        match_id: int,
    ):
        result = (
            db.query(
                MatchAnalysis,
                Job,
            )
            .join(
                Job,
                MatchAnalysis.job_id == Job.id,
            )
            .filter(
                MatchAnalysis.id == match_id
            )
            .first()
        )

        if not result:
            raise ValueError(
                "Match not found"
            )

        match, job = result

        return {
            "id": match.id,
            "resume_id": match.resume_id,
            "job_id": match.job_id,
            "overall_match_score": (
                match.overall_match_score
            ),
            "analysis_data": match.analysis_data,
            "job": job,
            "created_at": match.created_at,
            "updated_at": match.updated_at,
        }


    @classmethod
    def get_matches_by_resume(
        cls,
        db: Session,
        resume_id,
    ):
        results = (
            db.query(
                MatchAnalysis,
                Job,
            )
            .join(
                Job,
                MatchAnalysis.job_id == Job.id,
            )
            .filter(
                MatchAnalysis.resume_id == resume_id
            )
            .order_by(
                MatchAnalysis.overall_match_score.desc()
            )
            .all()
        )

        return [
            {
                "id": match.id,
                "resume_id": match.resume_id,
                "job_id": match.job_id,
                "overall_match_score": (
                    match.overall_match_score
                ),
                "analysis_data": match.analysis_data,
                "job": job,
                "created_at": match.created_at,
                "updated_at": match.updated_at,
            }
            for match, job in results
        ]


    @classmethod
    def get_matches_by_job(
        cls,
        db: Session,
        job_id: int,
    ):
        results = (
            db.query(
                MatchAnalysis,
                Job,
            )
            .join(
                Job,
                MatchAnalysis.job_id == Job.id,
            )
            .filter(
                MatchAnalysis.job_id == job_id
            )
            .order_by(
                MatchAnalysis.overall_match_score.desc()
            )
            .all()
        )

        return [
            {
                "id": match.id,
                "resume_id": match.resume_id,
                "job_id": match.job_id,
                "overall_match_score": (
                    match.overall_match_score
                ),
                "analysis_data": match.analysis_data,
                "job": job,
                "created_at": match.created_at,
                "updated_at": match.updated_at,
            }
            for match, job in results
        ]