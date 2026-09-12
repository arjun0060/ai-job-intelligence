from sqlalchemy.orm import Session

from app.models.resume_analysis import ResumeAnalysis
from app.models.job_analysis import JobAnalysis

from app.services.semantic_matcher import (
    SemanticMatcher
)

from app.services.scoring_service import (
    ScoringService
)


class SemanticMatchService:

    def __init__(self):

        self.matcher = SemanticMatcher()


    def analyze(
        self,
        db: Session,
        resume_id,
        job_id: int
    ) -> dict:

        # --------------------------------
        # FETCH RESUME ANALYSIS
        # --------------------------------

        resume_analysis = (
            db.query(ResumeAnalysis)
            .filter(
                ResumeAnalysis.resume_id == resume_id
            )
            .first()
        )

        if not resume_analysis:

            raise ValueError(
                "Resume analysis not found. "
                "Analyze the resume first."
            )


        # --------------------------------
        # FETCH JOB ANALYSIS
        # --------------------------------

        job_analysis = (
            db.query(JobAnalysis)
            .filter(
                JobAnalysis.job_id == job_id
            )
            .first()
        )

        if not job_analysis:

            raise ValueError(
                "Job analysis not found. "
                "Analyze the job first."
            )


        # --------------------------------
        # BUILD RESUME DATA
        # --------------------------------

        resume_data = {
            "skills":
                resume_analysis.skills or [],

            "experience":
                resume_analysis.experience or [],

            "education":
                resume_analysis.education or [],

            "summary":
                resume_analysis.summary or ""
        }


        # --------------------------------
        # BUILD JOB DATA
        # --------------------------------

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

            "summary": (
                job_analysis.summary or ""
            )
        }


        # --------------------------------
        # SEMANTIC EVALUATION
        # --------------------------------

        try:

            semantic_result = (
                self.matcher.evaluate(
                    resume_data=resume_data,
                    job_data=job_data
                )
            )

        except Exception:

            import traceback

            print(
                "\n========== "
                "SEMANTIC MATCH ERROR "
                "=========="
            )

            traceback.print_exc()

            print(
                "==========================================\n"
            )

            raise


        # --------------------------------
        # SCORE CALCULATION
        # --------------------------------

        score_result = (
            ScoringService.calculate_final_score(
                required_requirements=(
                    semantic_result.get(
                        "required_requirements",
                        []
                    )
                ),

                preferred_requirements=(
                    semantic_result.get(
                        "preferred_requirements",
                        []
                    )
                ),

                technology_requirements=(
                    semantic_result.get(
                        "technology_requirements",
                        []
                    )
                )
            )
        )


        # --------------------------------
        # FINAL RESULT
        # --------------------------------

        return {
            **score_result,
            **semantic_result
        }