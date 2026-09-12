from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.models.resume_analysis import ResumeAnalysis

from app.services.ai.gemini_resume_analyzer import (
    GeminiResumeAnalyzer
)


def analyze_resume(
    db: Session,
    resume: Resume
) -> ResumeAnalysis:

    analyzer = GeminiResumeAnalyzer()

    result = analyzer.analyze(
        resume.extracted_text
    )

    existing_analysis = (
        db.query(ResumeAnalysis)
        .filter(
            ResumeAnalysis.resume_id == resume.id
        )
        .first()
    )

    if existing_analysis:

        existing_analysis.skills = result.get(
            "skills",
            []
        )

        existing_analysis.experience = result.get(
            "experience",
            []
        )

        existing_analysis.education = result.get(
            "education",
            []
        )

        existing_analysis.summary = result.get(
            "summary"
        )

        db.commit()

        db.refresh(existing_analysis)

        return existing_analysis

    analysis = ResumeAnalysis(

        resume_id=resume.id,

        skills=result.get(
            "skills",
            []
        ),

        experience=result.get(
            "experience",
            []
        ),

        education=result.get(
            "education",
            []
        ),

        summary=result.get(
            "summary"
        )
    )

    db.add(analysis)

    db.commit()

    db.refresh(analysis)

    return analysis