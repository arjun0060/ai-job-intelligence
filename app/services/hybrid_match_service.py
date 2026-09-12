from sqlalchemy.orm import Session

from app.models.resume_analysis import ResumeAnalysis
from app.models.job_analysis import JobAnalysis

from app.services.ai.match_analyzer import MatchAnalyzer


from app.services.scoring_service import (
    ScoringService,
)


class HybridMatchService:

    @classmethod
    def analyze(
        cls,
        db: Session,
        resume_id,
        job_id,
    ):
        # ---------------------------------------------------------
        # Get preprocessed resume analysis
        # ---------------------------------------------------------

        resume_analysis = (
            db.query(ResumeAnalysis)
            .filter(
                ResumeAnalysis.resume_id == resume_id
            )
            .first()
        )

        if not resume_analysis:
            raise ValueError(
                "Resume analysis not found"
            )

        if resume_analysis.status != "completed":
            raise ValueError(
                "Resume analysis is not ready"
            )

        # ---------------------------------------------------------
        # Get preprocessed job analysis
        # ---------------------------------------------------------

        job_analysis = (
            db.query(JobAnalysis)
            .filter(
                JobAnalysis.job_id == job_id
            )
            .first()
        )

        if not job_analysis:
            raise ValueError(
                "Job analysis not found"
            )

        if job_analysis.status != "completed":
            raise ValueError(
                "Job analysis is not ready"
            )

        # ---------------------------------------------------------
        # Build structured resume data
        # ---------------------------------------------------------

        resume_data = {
            "skills": resume_analysis.skills or [],
            "experience": resume_analysis.experience or [],
            "education": resume_analysis.education or [],
            "summary": resume_analysis.summary or "",
        }

        # ---------------------------------------------------------
        # Build structured job data
        # ---------------------------------------------------------

        job_data = {
            "required_skills": (
                job_analysis.required_skills or []
            ),
            "supporting_competencies": (
                job_analysis.supporting_competencies or []
            ),
            "preferred_skills": (
                job_analysis.preferred_skills or []
            ),
            "technologies": (
                job_analysis.technologies or []
            ),
            "experience_requirement": (
                job_analysis.experience_requirement or {}
            ),
            "education_requirements": (
                job_analysis.education_requirements or []
            ),
            "responsibilities": (
                job_analysis.responsibilities or []
            ),
            "key_keywords": (
                job_analysis.key_keywords or []
            ),
            "summary": job_analysis.summary or "",
        }

        # ---------------------------------------------------------
        # Gemini semantic matching
        #
        # IMPORTANT:
        # The current GeminiMatchAnalyzer expects:
        #
        # analyze(
        #     resume_data=...,
        #     job_data=...
        # )
        #
        # Do NOT pass resume_text or job_description here.
        # ---------------------------------------------------------

        analyzer = MatchAnalyzer()

        analysis_result = analyzer.analyze(
            resume_data=resume_data,
            job_data=job_data,
        )

        # ---------------------------------------------------------
        # Deterministic scoring
        # ---------------------------------------------------------

        scoring_result = (
            ScoringService.calculate_final_score(
                required_requirements=(
                    analysis_result.get(
                        "required_requirements",
                        [],
                    )
                ),
                technology_requirements=(
                    analysis_result.get(
                        "technology_requirements",
                        [],
                    )
                ),
                preferred_requirements=(
                    analysis_result.get(
                        "preferred_requirements",
                        [],
                    )
                ),
            )
        )

        # ---------------------------------------------------------
        # Merge scoring result into semantic analysis
        # ---------------------------------------------------------

        analysis_result.update(
            scoring_result
        )

        return analysis_result