from sqlalchemy.orm import Session

from app.models.job import Job
from app.models.job_analysis import JobAnalysis

from app.services.ai.job_analyzer import JobAnalyzer


class JobAnalysisService:

    @classmethod
    def analyze_job(
        cls,
        db: Session,
        job_id: int,
    ) -> JobAnalysis:

        # ---------------------------------
        # Get job
        # ---------------------------------

        job = (
            db.query(Job)
            .filter(Job.id == job_id)
            .first()
        )

        if not job:
            raise ValueError(
                "Job not found"
            )

        # ---------------------------------
        # Analyze job description
        # ---------------------------------

        analyzer = JobAnalyzer()

        analysis_result = analyzer.analyze(
            job_description=job.description
        )

        # ---------------------------------
        # Check existing analysis
        # ---------------------------------

        existing_analysis = (
            db.query(JobAnalysis)
            .filter(
                JobAnalysis.job_id == job_id
            )
            .first()
        )

        # ---------------------------------
        # Update existing analysis
        # ---------------------------------

        if existing_analysis:

            existing_analysis.required_skills = (
                analysis_result.get(
                    "required_skills",
                    []
                )
            )

            existing_analysis.supporting_competencies = (
                analysis_result.get(
                    "supporting_competencies",
                    []
                )
            )

            existing_analysis.preferred_skills = (
                analysis_result.get(
                    "preferred_skills",
                    []
                )
            )

            existing_analysis.technologies = (
                analysis_result.get(
                    "technologies",
                    []
                )
            )

            existing_analysis.experience_requirement = (
                analysis_result.get(
                    "experience_requirement",
                    {}
                )
            )

            existing_analysis.education_requirements = (
                analysis_result.get(
                    "education_requirements",
                    []
                )
            )

            existing_analysis.responsibilities = (
                analysis_result.get(
                    "responsibilities",
                    []
                )
            )

            existing_analysis.key_keywords = (
                analysis_result.get(
                    "key_keywords",
                    []
                )
            )

            existing_analysis.summary = (
                analysis_result.get(
                    "summary",
                    ""
                )
            )

            db.commit()
            db.refresh(existing_analysis)

            return existing_analysis

        # ---------------------------------
        # Create new analysis
        # ---------------------------------

        job_analysis = JobAnalysis(

            job_id=job_id,

            required_skills=analysis_result.get(
                "required_skills",
                []
            ),

            supporting_competencies=analysis_result.get(
                "supporting_competencies",
                []
            ),

            preferred_skills=analysis_result.get(
                "preferred_skills",
                []
            ),

            technologies=analysis_result.get(
                "technologies",
                []
            ),

            experience_requirement=analysis_result.get(
                "experience_requirement",
                {}
            ),

            education_requirements=analysis_result.get(
                "education_requirements",
                []
            ),

            responsibilities=analysis_result.get(
                "responsibilities",
                []
            ),

            key_keywords=analysis_result.get(
                "key_keywords",
                []
            ),

            summary=analysis_result.get(
                "summary",
                ""
            ),
        )

        db.add(job_analysis)

        db.commit()

        db.refresh(job_analysis)

        return job_analysis