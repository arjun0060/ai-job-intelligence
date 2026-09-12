import json
import logging

from google import genai

from app.core.config import settings
from app.core.exceptions import (
    AIServiceError,
    AIResponseParsingError
)


logger = logging.getLogger(__name__)


class GeminiResumeAnalyzer:

    def __init__(self):

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

    def analyze(self, resume_text: str) -> dict:

        prompt = self._build_prompt(resume_text)

        try:

            response = self.client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )

            response_text = response.text.strip()

            return self._parse_response(
                response_text
            )

        except AIResponseParsingError:
            raise

        except Exception as error:

            logger.exception(
                "Gemini resume analysis failed"
            )

            raise AIServiceError(
                "Failed to analyze resume"
            ) from error

    def _build_prompt(
        self,
        resume_text: str
    ) -> str:

        return f"""
You are an AI-powered resume analysis system.

Your task is to extract structured information
from a candidate's resume.

IMPORTANT RULES:

1. Extract ONLY information explicitly present.
2. Never invent skills, experience, companies,
   education, or achievements.
3. Normalize technology names.
4. Return ONLY valid JSON.
5. Do not include markdown.
6. Use empty arrays when information is unavailable.
7. Keep the summary concise and professional.

RESUME:

{resume_text}

RETURN FORMAT:

{{
    "skills": [],
    "experience": [
        {{
            "role": "",
            "company": "",
            "duration": "",
            "technologies": []
        }}
    ],
    "education": [
        {{
            "degree": "",
            "institution": "",
            "duration": ""
        }}
    ],
    "summary": ""
}}
"""

    def _parse_response(
        self,
        response_text: str
    ) -> dict:

        cleaned_response = response_text.strip()

        if cleaned_response.startswith("```json"):

            cleaned_response = cleaned_response[
                len("```json"):
            ]

        elif cleaned_response.startswith("```"):

            cleaned_response = cleaned_response[
                len("```"):
            ]

        if cleaned_response.endswith("```"):

            cleaned_response = cleaned_response[:-3]

        try:

            return json.loads(
                cleaned_response.strip()
            )

        except json.JSONDecodeError as error:

            logger.error(
                "Failed to parse Gemini response: %s",
                response_text
            )

            raise AIResponseParsingError(
                "AI returned invalid JSON"
            ) from error