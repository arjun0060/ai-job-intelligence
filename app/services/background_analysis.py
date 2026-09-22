import logging

from app.db.session import SessionLocal
from app.models.job import Job
from app.models.job_analysis import JobAnalysis
from app.models.resume import Resume
from app.models.resume_analysis import ResumeAnalysis
from app.services.job_analysis_service import JobAnalysisService
from app.services.resume_analysis_service import analyze_resume
from app.services.embeddings.embedding_manager import EmbeddingManager


logger = logging.getLogger(__name__)


def analyze_resume_background(resume_id):
    db = SessionLocal()

    try:
        resume = (
            db.query(Resume)
            .filter(Resume.id == resume_id)
            .first()
        )

        if not resume:
            logger.error(
                "Resume not found: %s",
                resume_id
            )
            return

        analysis = (
            db.query(ResumeAnalysis)
            .filter(
                ResumeAnalysis.resume_id == resume_id
            )
            .first()
        )

        if not analysis:
            analysis = ResumeAnalysis(
                resume_id=resume_id,
                status="processing"
            )

            db.add(analysis)
            db.commit()

        analyze_resume(
            db=db,
            resume=resume
        )

        

        analysis = (
            db.query(ResumeAnalysis)
            .filter(
                ResumeAnalysis.resume_id == resume_id
            )
            .first()
        )

        resume_data = {
            "skills": analysis.skills or [],
            "experience": analysis.experience or [],
            "education": analysis.education or [],
            "summary": analysis.summary or "",
        }

        embedding_manager = EmbeddingManager()

        embedding_manager.create_resume_embeddings(
            db=db,
            resume_id=resume_id,
            resume_data=resume_data,
        )

        
        if analysis:
            analysis.status = "completed"
            db.commit()

        logger.info(
            "Resume analysis completed: %s",
            resume_id
        )

    except Exception:
        db.rollback()

        try:
            analysis = (
                db.query(ResumeAnalysis)
                .filter(
                    ResumeAnalysis.resume_id == resume_id
                )
                .first()
            )

            if analysis:
                analysis.status = "failed"
                db.commit()

        except Exception:
            db.rollback()
            logger.exception(
                "Failed to update resume analysis status: %s",
                resume_id
            )

        logger.exception(
            "Resume analysis failed: %s",
            resume_id
        )

    finally:
        db.close()


def analyze_job_background(job_id: int):
    db = SessionLocal()

    try:
        job = (
            db.query(Job)
            .filter(Job.id == job_id)
            .first()
        )

        if not job:
            logger.error(
                "Job not found: %s",
                job_id
            )
            return

        # ---------------------------------------------
        # Analyze job description
        # ---------------------------------------------

        analysis = JobAnalysisService.analyze_job(
            db=db,
            job_id=job_id
        )

        if not analysis:
            raise RuntimeError(
                f"Job analysis was not created for job {job_id}"
            )

        # ---------------------------------------------
        # Build job data for embeddings
        # ---------------------------------------------

        job_data = {
            "required_skills": (
                analysis.required_skills or []
            ),
            "supporting_competencies": (
                analysis.supporting_competencies or []
            ),
            "preferred_skills": (
                analysis.preferred_skills or []
            ),
            "technologies": (
                analysis.technologies or []
            ),
            "experience_requirement": (
                analysis.experience_requirement or {}
            ),
            "education_requirements": (
                analysis.education_requirements or []
            ),
            "responsibilities": (
                analysis.responsibilities or []
            ),
            "key_keywords": (
                analysis.key_keywords or []
            ),
            "summary": (
                analysis.summary or ""
            ),
        }

        # ---------------------------------------------
        # Create job embeddings
        # ---------------------------------------------

        embedding_manager = EmbeddingManager()

        embedding_manager.create_job_embeddings(
            db=db,
            job_id=job_id,
            job_data=job_data,
        )

        # ---------------------------------------------
        # Mark analysis as completed
        # ---------------------------------------------

        analysis.status = "completed"

        db.commit()

        logger.info(
            "Job analysis and embeddings completed: %s",
            job_id
        )

    except Exception:
        db.rollback()

        try:
            analysis = (
                db.query(JobAnalysis)
                .filter(
                    JobAnalysis.job_id == job_id
                )
                .first()
            )

            if analysis:
                analysis.status = "failed"
                db.commit()

        except Exception:
            db.rollback()

            logger.exception(
                "Failed to update job analysis status: %s",
                job_id
            )

        logger.exception(
            "Job analysis failed: %s",
            job_id
        )

    finally:
        db.close()