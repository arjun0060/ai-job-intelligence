import json
import logging

from google import genai

from app.core.config import settings
from app.core.exceptions import (
    AIServiceError,
    AIResponseParsingError
)


logger = logging.getLogger(__name__)


class GeminiJobAnalyzer:

    def __init__(self):

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )


    def analyze(
        self,
        job_description: str
    ) -> dict:

        prompt = self._build_prompt(
            job_description
        )

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
                "Gemini job analysis failed"
            )

            raise AIServiceError(
                "Failed to analyze job description"
            ) from error


    def _build_prompt(
        self,
        job_description: str
    ) -> str:

        return f"""
You are a job description intelligence system.

Your task is to extract structured hiring requirements
from the provided job description.

You must identify what is truly important for candidate
evaluation rather than treating every word in the job
description as an equally important requirement.

=================================================

GENERAL RULES

1. Extract ONLY information supported by the job description.

2. Do NOT invent requirements.

3. Do NOT convert generic corporate language into critical
candidate requirements unless the job description clearly
emphasizes it.

For example, statements like:

- "works well with others"
- "manages time effectively"
- "takes ownership"
- "communicates with stakeholders"

should generally be treated as supporting competencies,
not critical technical requirements.

4. Separate requirements into:

- required_skills
- supporting_competencies
- preferred_skills
- technologies

5. Technologies must contain specific:

- programming languages
- frameworks
- databases
- cloud platforms
- DevOps tools
- AI/ML tools
- libraries

6. Broader capabilities belong under skills.

For example:

Technology:
Python

Skill:
Backend development

Do NOT duplicate the same concept unnecessarily.

=================================================

IMPORTANCE RULES

Every extracted requirement must receive an importance level.

Allowed values:

high
medium
low

HIGH:

Use high importance when the requirement is clearly essential.

Examples:

- explicitly required technology
- mandatory years of experience
- core technical competency
- primary responsibility
- repeatedly emphasized requirement

MEDIUM:

Use medium importance when the requirement is relevant
but not clearly essential.

Examples:

- important supporting technology
- secondary responsibility
- common engineering practice
- supporting technical competency

LOW:

Use low importance when the requirement is desirable
or only lightly emphasized.

Examples:

- nice-to-have technology
- optional exposure
- supporting competency
- secondary tooling

IMPORTANT:

Do NOT automatically mark every technology as high.

A technology mentioned once in a long list should usually
be medium unless the job description explicitly identifies
it as required or core.

=================================================

REQUIRED SKILLS

These should represent important professional or technical
capabilities.

Return objects in this format:

{{
    "requirement": "",
    "category": "technical",
    "importance": "high"
}}

Examples:

- Backend system development
- Distributed systems engineering
- Software design
- Data structures and algorithms

Do NOT include vague behavioral traits as required skills
unless clearly mandatory.

=================================================

SUPPORTING COMPETENCIES

These include behavioral or general professional capabilities.

Examples:

- Collaboration
- Communication
- Problem solving
- Time management
- Learning ability

These should NOT dominate the final match score.

Return objects in this format:

{{
    "requirement": "",
    "importance": "medium"
}}

=================================================

PREFERRED SKILLS

Include skills explicitly described as:

- preferred
- nice to have
- bonus
- advantage
- exposure to

Return objects:

{{
    "requirement": "",
    "category": "preferred",
    "importance": "low"
}}

=================================================

TECHNOLOGIES

Extract specific technologies and assign realistic importance.

Return objects:

{{
    "requirement": "",
    "importance": "high"
}}

Examples:

{{
    "requirement": "Python",
    "importance": "high"
}}

{{
    "requirement": "Docker",
    "importance": "medium"
}}

{{
    "requirement": "Kubernetes",
    "importance": "low"
}}

Do NOT automatically classify all technologies as high.

=================================================

EXPERIENCE REQUIREMENTS

If experience is explicitly mentioned, extract it.

If no experience requirement is mentioned:

minimum_years = null
maximum_years = null
description = null

=================================================

EDUCATION REQUIREMENTS

Extract only explicitly stated degree or education requirements.

If none are mentioned:

return []

=================================================

RESPONSIBILITIES

Extract only the core responsibilities.

Do NOT convert every sentence into a responsibility.

Keep responsibilities concise.

Avoid duplicating skills.

=================================================

KEYWORDS

Extract useful technical keywords for search and indexing.

=================================================

JOB DESCRIPTION

{job_description}


=================================================

RETURN ONLY VALID JSON

Do not include markdown.

Use exactly this structure:

{{
    "required_skills": [
        {{
            "requirement": "",
            "category": "technical",
            "importance": "high"
        }}
    ],

    "supporting_competencies": [
        {{
            "requirement": "",
            "importance": "medium"
        }}
    ],

    "preferred_skills": [
        {{
            "requirement": "",
            "category": "preferred",
            "importance": "low"
        }}
    ],

    "technologies": [
        {{
            "requirement": "",
            "importance": "high"
        }}
    ],

    "experience_requirement": {{
        "minimum_years": null,
        "maximum_years": null,
        "description": null
    }},

    "education_requirements": [],

    "responsibilities": [],

    "key_keywords": [],

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