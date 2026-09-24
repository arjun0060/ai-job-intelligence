import logging

from app.core.exceptions import AIServiceError
from app.services.ai.gemini_resume_analyzer import GeminiResumeAnalyzer
from app.services.ai.local_resume_analyzer import LocalResumeAnalyzer


logger = logging.getLogger(__name__)


class ResumeAnalyzer:
    def __init__(self):
        self.gemini = GeminiResumeAnalyzer()
        self.fallback = LocalResumeAnalyzer()

    def analyze(self, resume_text: str) -> dict:
        try:
            return self.gemini.analyze(
                resume_text=resume_text
            )

        except AIServiceError as error:
            logger.warning(
                "Gemini resume analysis unavailable. "
                "Using local fallback: %s",
                error,
            )

            return self.fallback.analyze(
                resume_text=resume_text
            )

        except Exception:
            logger.exception(
                "Unexpected Gemini resume analysis failure. "
                "Using local fallback."
            )

            return self.fallback.analyze(
                resume_text=resume_text
            )