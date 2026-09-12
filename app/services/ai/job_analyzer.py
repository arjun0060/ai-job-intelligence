import logging

from app.services.ai.gemini_job_analyzer import GeminiJobAnalyzer
from app.services.ai.local_job_analyzer import LocalJobAnalyzer

logger = logging.getLogger(__name__)


class JobAnalyzer:

    def __init__(self):
        self.gemini = GeminiJobAnalyzer()
        self.fallback = LocalJobAnalyzer()

    def analyze(self, job_description: str) -> dict:

        try:

            logger.info(
                "Attempting job analysis with Gemini"
            )

            return self.gemini.analyze(
                job_description=job_description
            )

        except Exception as error:

            logger.warning(
                "Gemini job analysis failed. "
                "Using local fallback. Error: %s",
                error
            )

            return self.fallback.analyze(
                job_description=job_description
            )