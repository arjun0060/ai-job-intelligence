import logging

from google.genai import errors as genai_errors

from app.services.ai.gemini_match_analyzer import GeminiMatchAnalyzer
from app.services.ai.local_match_analyzer import LocalMatchAnalyzer

logger = logging.getLogger(__name__)


class MatchAnalyzer:
    """
    Primary semantic matcher with a deterministic local fallback.

    Gemini is attempted first. If the provider is unavailable,
    the local analyzer receives the same structured resume/job data
    and evaluates the requirements deterministically.
    """

    def __init__(self):
        self.gemini = GeminiMatchAnalyzer()
        self.fallback = LocalMatchAnalyzer()

    def analyze(
        self,
        resume_data: dict,
        job_data: dict,
    ) -> dict:

        try:
            logger.info(
                "Attempting semantic match analysis with Gemini"
            )

            result = self.gemini.analyze(
                resume_data=resume_data,
                job_data=job_data,
            )

            result["analysis_provider"] = "gemini"

            return result

        except genai_errors.ClientError as error:

            if self._is_fallback_error(error):

                logger.warning(
                    "Gemini unavailable. Using local fallback. "
                    "Error: %s",
                    error,
                )

                result = self._fallback_analyze(
                    resume_data=resume_data,
                    job_data=job_data,
                )

                result["analysis_provider"] = "local"
                result["fallback_reason"] = (
                    "Gemini was temporarily unavailable, so the "
                    "match was evaluated using the local "
                    "deterministic analyzer."
                )

                return result

            raise

        except TimeoutError as error:

            logger.warning(
                "Gemini request timed out. "
                "Using local fallback: %s",
                error,
            )

            result = self._fallback_analyze(
                resume_data=resume_data,
                job_data=job_data,
            )

            result["analysis_provider"] = "local"
            result["fallback_reason"] = (
                "Gemini request timed out, so the match was "
                "evaluated using the local deterministic analyzer."
            )

            return result

    @staticmethod
    def _is_fallback_error(error: Exception) -> bool:

        status_code = getattr(error, "status_code", None)

        if status_code in (429, 500, 502, 503, 504):
            return True

        error_message = str(error).lower()

        fallback_keywords = (
            "429",
            "resource_exhausted",
            "quota exceeded",
            "rate limit",
            "temporarily unavailable",
            "service unavailable",
        )

        return any(
            keyword in error_message
            for keyword in fallback_keywords
        )

    def _fallback_analyze(
        self,
        resume_data: dict,
        job_data: dict,
    ) -> dict:
        """
        Pass the original structured data directly to the
        local analyzer.

        LocalMatchAnalyzer is responsible for building:
        - required requirements
        - technology requirements
        - preferred requirements
        """

        return self.fallback.analyze(
            resume_data=resume_data,
            job_data=job_data,
        )