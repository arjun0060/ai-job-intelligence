import logging

from google.genai import errors as genai_errors

from app.services.ai.gemini_match_analyzer import GeminiMatchAnalyzer
from app.services.ai.local_match_analyzer import LocalMatchAnalyzer
from app.core.exceptions import AIServiceError
from app.services.embeddings.evidence_retrieval_service import (
    EvidenceRetrievalService,
)
from app.services.requirement_builder import RequirementBuilder

logger = logging.getLogger(__name__)


class MatchAnalyzer:
    """
    Primary semantic matcher with a deterministic local fallback.

    Gemini is attempted first.

    Before Gemini evaluation, relevant resume evidence is retrieved
    using vector similarity search. The retrieved evidence is passed
    to Gemini as supporting context.

    If Gemini is unavailable, the local analyzer receives the same
    structured resume/job data and evaluates the requirements
    deterministically.
    """

    def __init__(self):
        self.gemini = GeminiMatchAnalyzer()
        self.fallback = LocalMatchAnalyzer()
        self.evidence_retrieval = EvidenceRetrievalService()
        self.requirement_builder = RequirementBuilder()

    def analyze(
        self,
        db,
        resume_id,
        resume_data: dict,
        job_data: dict,
    ) -> dict:

        try:
            logger.info(
                "Attempting semantic match analysis with Gemini"
            )

            # ---------------------------------------------
            # Retrieve relevant resume evidence
            # ---------------------------------------------

            retrieved_evidence = self._retrieve_evidence(
                db=db,
                resume_id=resume_id,
                job_data=job_data,
            )

            logger.info(
                "Retrieved semantic evidence for %d requirements",
                len(retrieved_evidence),
            )

            # ---------------------------------------------
            # Gemini semantic evaluation
            # ---------------------------------------------

            result = self.gemini.analyze(
                resume_data=resume_data,
                job_data=job_data,
                retrieved_evidence=retrieved_evidence,
            )

            result["analysis_provider"] = "gemini"

            return result

        except (genai_errors.ClientError, genai_errors.ServerError) as error:

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

        except AIServiceError as error:
            # GeminiMatchAnalyzer wraps provider exceptions in
            # AIServiceError, so the original Gemini 429/503/etc.
            # is available through __cause__. Handle that wrapper
            # here so the local analyzer is actually reached.
            if self._is_fallback_error(error):
                logger.warning(
                    "Gemini service error. Using local fallback. "
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
                "Gemini request timed out. Using local fallback: %s",
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

    # =========================================================
    # RETRIEVE SEMANTIC RESUME EVIDENCE
    # =========================================================

    def _retrieve_evidence(
        self,
        db,
        resume_id,
        job_data: dict,
    ) -> dict:
        """Retrieve resume evidence for the normalized requirements."""

        evidence = {}
        requirements = self.requirement_builder.build(job_data)

        groups = (
            requirements.get("required_requirements") or [],
            requirements.get("technology_requirements") or [],
            requirements.get("preferred_requirements") or [],
        )

        for group in groups:
            for item in group:
                requirement = str(
                    item.get("requirement") or ""
                ).strip()
                if not requirement or requirement in evidence:
                    continue

                results = self.evidence_retrieval.retrieve(
                    db=db,
                    resume_id=resume_id,
                    requirement=requirement,
                    limit=3,
                    min_similarity=0.30,
                )

                evidence[requirement] = results

        return evidence

    # =========================================================
    # FALLBACK ERROR DETECTION
    # =========================================================

    @staticmethod
    def _is_fallback_error(
        error: Exception
    ) -> bool:

        current_error = error

        # GeminiMatchAnalyzer wraps provider exceptions in
        # AIServiceError. Walk the exception chain so the
        # original Gemini status code/message is detected.
        while current_error is not None:
            status_code = getattr(
                current_error,
                "status_code",
                None
            )

            if status_code in (
                429,
                500,
                502,
                503,
                504,
            ):
                return True

            error_message = str(
                current_error
            ).lower()

            fallback_keywords = (
                "429",
                "resource_exhausted",
                "quota exceeded",
                "rate limit",
                "temporarily unavailable",
                "service unavailable",
                "high demand",
                "unavailable",
            )

            if any(
                keyword in error_message
                for keyword in fallback_keywords
            ):
                return True

            current_error = current_error.__cause__

        return False

    # =========================================================
    # LOCAL FALLBACK
    # =========================================================

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