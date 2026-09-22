import json
import logging

from google import genai

from app.core.config import settings
from app.core.exceptions import (
    AIServiceError,
    AIResponseParsingError,
)

logger = logging.getLogger(__name__)


class GeminiMatchAnalyzer:

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

    # =========================================================
    # MAIN SEMANTIC MATCHING METHOD
    # =========================================================

    def analyze(
        self,
        resume_data: dict,
        job_data: dict,
        retrieved_evidence: dict | None = None,
    ) -> dict:

        # ---------------------------------------------
        # Build separate requirement groups
        # ---------------------------------------------

        required_requirements = (
            self._build_required_requirements(
                job_data=job_data
            )
        )

        technology_requirements = (
            self._build_technology_requirements(
                job_data=job_data
            )
        )

        preferred_requirements = (
            self._build_preferred_requirements(
                job_data=job_data
            )
        )

        # ---------------------------------------------
        # Build candidate profile
        # ---------------------------------------------

        candidate_profile = {
            "skills": (
                resume_data.get("skills")
                or []
            ),
            "experience": (
                resume_data.get("experience")
                or []
            ),
            "education": (
                resume_data.get("education")
                or []
            ),
            "summary": (
                resume_data.get("summary")
                or ""
            ),
        }

        # ---------------------------------------------
        # Semantic evaluation
        # ---------------------------------------------

        analysis_result = (
            self.analyze_semantic_match(
                candidate_profile=candidate_profile,
                required_requirements=required_requirements,
                technology_requirements=technology_requirements,
                preferred_requirements=preferred_requirements,
                retrieved_evidence=retrieved_evidence or {},
            )
        )

        # ---------------------------------------------
        # Normalize AI output
        # ---------------------------------------------

        analysis_result = (
            self._normalize_analysis_result(
                analysis_result=analysis_result,
                required_requirements=required_requirements,
                technology_requirements=technology_requirements,
                preferred_requirements=preferred_requirements,
            )
        )

        return analysis_result

    # =========================================================
    # BUILD REQUIRED REQUIREMENTS
    # =========================================================

    def _build_required_requirements(
        self,
        job_data: dict
    ) -> list:

        requirements = []

        # ---------------------------------------------
        # Required skills
        # ---------------------------------------------

        for item in (
            job_data.get("required_skills")
            or []
        ):

            if isinstance(item, dict):

                requirement = item.get(
                    "requirement"
                )

                if requirement:

                    requirements.append(
                        {
                            "requirement": requirement,
                            "category": item.get(
                                "category",
                                "technical"
                            ),
                            "importance": item.get(
                                "importance",
                                "high"
                            )
                        }
                    )

            elif isinstance(item, str):

                requirements.append(
                    {
                        "requirement": item,
                        "category": "technical",
                        "importance": "high"
                    }
                )

        # ---------------------------------------------
        # Experience requirement
        # ---------------------------------------------

        experience_requirement = (
            job_data.get("experience_requirement")
            or {}
        )
        experience_text = self._experience_text(
            experience_requirement
        )

        if experience_text:
            requirements.append(
                {
                    "requirement": experience_text,
                    "category": "experience",
                    "importance": "high",
                }
            )

        # ---------------------------------------------
        # Education requirements
        # ---------------------------------------------

        for item in (
            job_data.get("education_requirements")
            or []
        ):
            requirement = (
                item.get("requirement")
                if isinstance(item, dict)
                else item
            )

            if requirement:
                requirements.append(
                    {
                        "requirement": str(requirement),
                        "category": "education",
                        "importance": (
                            item.get("importance", "medium")
                            if isinstance(item, dict)
                            else "medium"
                        ),
                    }
                )

        # ---------------------------------------------
        # Responsibilities
        # ---------------------------------------------

        for item in (
            job_data.get("responsibilities")
            or []
        ):

            if isinstance(item, dict):

                requirement = item.get(
                    "requirement"
                )

                if requirement:

                    requirements.append(
                        {
                            "requirement": requirement,
                            "category": "responsibility",
                            "importance": item.get(
                                "importance",
                                "medium"
                            )
                        }
                    )

            elif isinstance(item, str):

                requirements.append(
                    {
                        "requirement": item,
                        "category": "responsibility",
                        "importance": "medium"
                    }
                )

        return requirements

    # =========================================================
    # BUILD TECHNOLOGY REQUIREMENTS
    # =========================================================

    def _build_technology_requirements(
        self,
        job_data: dict
    ) -> list:

        requirements = []

        for item in (
            job_data.get("technologies")
            or []
        ):

            if isinstance(item, dict):

                requirement = item.get(
                    "requirement"
                )

                if requirement:

                    requirements.append(
                        {
                            "requirement": requirement,
                            "category": "technology",
                            "importance": item.get(
                                "importance",
                                "high"
                            )
                        }
                    )

            elif isinstance(item, str):

                requirements.append(
                    {
                        "requirement": item,
                        "category": "technology",
                        "importance": "high"
                    }
                )

        return requirements

    # =========================================================
    # BUILD PREFERRED REQUIREMENTS
    # =========================================================

    def _build_preferred_requirements(
        self,
        job_data: dict
    ) -> list:

        requirements = []

        # ---------------------------------------------
        # Preferred skills
        # ---------------------------------------------

        for item in (
            job_data.get("preferred_skills")
            or []
        ):

            if isinstance(item, dict):

                requirement = item.get(
                    "requirement"
                )

                if requirement:

                    requirements.append(
                        {
                            "requirement": requirement,
                            "category": item.get(
                                "category",
                                "preferred"
                            ),
                            "importance": item.get(
                                "importance",
                                "low"
                            )
                        }
                    )

            elif isinstance(item, str):

                requirements.append(
                    {
                        "requirement": item,
                        "category": "preferred",
                        "importance": "low"
                    }
                )

        # ---------------------------------------------
        # Supporting competencies
        #
        # These are NOT hard requirements.
        # Therefore they belong with preferred.
        # ---------------------------------------------

        for item in (
            job_data.get(
                "supporting_competencies"
            )
            or []
        ):

            if isinstance(item, dict):

                requirement = item.get(
                    "requirement"
                )

                if requirement:

                    requirements.append(
                        {
                            "requirement": requirement,
                            "category": "competency",
                            "importance": item.get(
                                "importance",
                                "low"
                            )
                        }
                    )

            elif isinstance(item, str):

                requirements.append(
                    {
                        "requirement": item,
                        "category": "competency",
                        "importance": "low"
                    }
                )

        return requirements

    # =========================================================
    # SEMANTIC MATCHING
    # =========================================================

    def analyze_semantic_match(
        self,
        candidate_profile: dict,
        required_requirements: list,
        technology_requirements: list,
        preferred_requirements: list,
        retrieved_evidence: dict,
    ) -> dict:

        prompt = f"""
You are an expert technical recruiter and candidate evaluation system.

Your task is to evaluate a candidate against predefined job
requirements using SEMANTIC reasoning.

You are NOT performing keyword matching.

A candidate may partially satisfy a requirement through related
experience, equivalent technologies, relevant projects,
education, or demonstrated work.

However, similarity does NOT automatically mean equivalence.

=================================================

STRICT INPUT RULES

The requirements below were already extracted from the job description.

You MUST evaluate ONLY these requirements.

DO NOT:

1. Create new requirements.
2. Remove requirements.
3. Merge multiple requirements.
4. Rewrite requirements.
5. Change requirement categories.
6. Change requirement importance.
7. Invent candidate skills.
8. Invent projects or achievements.
9. Assume unrelated technologies are equivalent.
10. Assume behavioral skills without evidence.

=================================================

SEMANTIC EVALUATION RULES

Evaluate meaning rather than exact keyword overlap.

Examples:

Python backend experience may support general software development
requirements.

PostgreSQL experience may provide INDIRECT evidence for relational
database knowledge, but does NOT mean the candidate knows MySQL.

Docker experience may provide partial evidence for containerization,
but does NOT prove Kubernetes experience.

A Computer Science degree provides INDIRECT evidence of fundamental
Computer Science knowledge, but does NOT automatically prove advanced
expertise in algorithms or distributed systems.

Professional experience alone does NOT automatically prove:

- communication
- leadership
- teamwork
- time management
- decision making
- supervision

These require explicit evidence or strong contextual evidence.

=================================================

TECHNOLOGY EVALUATION RULES

Technology requirements must be evaluated independently.

DIRECT:

Candidate explicitly lists or demonstrates the exact technology.

Example:

Requirement: Python

Candidate explicitly uses Python professionally.

Score: usually 80-100.

INDIRECT:

Candidate has closely related technology experience.

Example:

Requirement: MySQL

Candidate has PostgreSQL and general SQL experience.

Score: usually 30-60.

Do NOT treat related technologies as direct matches.

NONE:

Technology is not mentioned and no meaningful related experience exists.

Score: usually 0-10.

=================================================

EVIDENCE LEVELS

DIRECT:

The candidate explicitly demonstrates the requirement.

INDIRECT:

The candidate has related experience that reasonably supports
partial capability.

NONE:

There is no meaningful evidence.

=================================================

SCORING GUIDELINES

90-100:
Very strong direct evidence.

70-89:
Strong direct evidence with good relevance.

40-69:
Partial or indirect evidence.

10-39:
Weak or limited evidence.

0-9:
No meaningful evidence.

Do NOT inflate scores.

Do NOT give 100 unless the candidate clearly demonstrates
exceptionally strong and explicit evidence.

=================================================

IMPORTANT BEHAVIORAL REQUIREMENTS

For requirements such as:

- teamwork
- communication
- leadership
- supervision
- time management
- decision making

Be conservative.

Mandatory collaboration, teamwork, communication, or stakeholder
responsibilities must remain required when they were extracted as
required responsibilities. Do not downgrade them simply because
they are behavioral.

Do NOT assume these abilities simply because the candidate
has professional work experience.

If there is no meaningful evidence:

score should generally be between 0 and 20.

=================================================

RETRIEVED RESUME EVIDENCE

The following evidence was retrieved from the candidate's
resume using semantic vector search.

Use this evidence as supporting information when evaluating
requirements.

IMPORTANT:

1. Retrieved evidence is supporting evidence, not automatic proof.
2. High vector similarity does NOT mean the requirement is satisfied.
3. Verify experience level, duration, context, and specificity.
4. Treat explicit minimum/maximum experience requirements as a separate
   requirement and compare them against the candidate's documented
   professional experience.
5. Do NOT infer missing years of experience.
6. Do NOT infer responsibilities that are not supported.
6. If retrieved evidence is weak or insufficient, score conservatively.
7. Evidence must be supported by the candidate profile or retrieved resume evidence.
8. Do NOT treat vector similarity as the candidate's match score.
9. A technology appearing in retrieved evidence does not prove the
   candidate satisfies additional experience requirements associated
   with that technology.
10. For example, "Kubernetes" evidence does not prove "five years of
    production Kubernetes administration."

{json.dumps(retrieved_evidence, indent=2)}

=================================================

CANDIDATE PROFILE

{json.dumps(candidate_profile, indent=2)}

=================================================

REQUIRED REQUIREMENTS

{json.dumps(required_requirements, indent=2)}

=================================================

TECHNOLOGY REQUIREMENTS

{json.dumps(technology_requirements, indent=2)}

=================================================

PREFERRED REQUIREMENTS

{json.dumps(preferred_requirements, indent=2)}

=================================================

OUTPUT RULES

Return every input requirement EXACTLY once.

The "requirement" value MUST be copied EXACTLY from the input.

Do not add requirements.

Do not omit requirements.

Do not move requirements between groups.

Use evidence ONLY from the candidate profile or retrieved resume evidence.

When using retrieved evidence, include the actual relevant resume
content in the "evidence" field.

Do not include vector similarity as the candidate score.

Return ONLY valid JSON.

Return exactly this structure:

{{
    "required_requirements": [
        {{
            "requirement": "",
            "category": "",
            "importance": "",
            "score": 0,
            "evidence_level": "direct",
            "evidence": [],
            "reason": ""
        }}
    ],

    "technology_requirements": [
        {{
            "requirement": "",
            "category": "technology",
            "importance": "",
            "score": 0,
            "evidence_level": "direct",
            "evidence": [],
            "reason": ""
        }}
    ],

    "preferred_requirements": [
        {{
            "requirement": "",
            "category": "",
            "importance": "",
            "score": 0,
            "evidence_level": "direct",
            "evidence": [],
            "reason": ""
        }}
    ],

    "strengths": [],

    "gaps": [
        {{
            "gap": "",
            "importance": "high",
            "recommendation": ""
        }}
    ],

    "overall_assessment": ""
}}
"""

        try:

            response = (
                self.client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt
                )
            )

            response_text = (
                response.text
                .strip()
            )

            return self._parse_response(
                response_text
            )

        except AIResponseParsingError:
            raise

        except Exception as error:

            logger.exception(
                "Gemini semantic matching failed"
            )

            raise AIServiceError(
                "Failed to perform semantic job matching"
            ) from error

    @staticmethod
    def _experience_text(experience_requirement: dict) -> str | None:
        minimum = experience_requirement.get("minimum_years")
        maximum = experience_requirement.get("maximum_years")
        description = experience_requirement.get("description")

        if minimum is not None and maximum is not None:
            return (
                f"At least {float(minimum):g} years of experience "
                f"and no more than {float(maximum):g} years"
            )

        if minimum is not None:
            return f"At least {float(minimum):g} years of professional experience"

        if maximum is not None:
            return f"No more than {float(maximum):g} years of professional experience"

        return str(description).strip() if description else None

    # =========================================================
    # NORMALIZE LLM OUTPUT
    # =========================================================

    def _normalize_analysis_result(
        self,
        analysis_result: dict,
        required_requirements: list,
        technology_requirements: list,
        preferred_requirements: list
    ) -> dict:

        # ---------------------------------------------
        # Normalize required requirements
        # ---------------------------------------------

        normalized_required = (
            self._normalize_requirement_group(
                original_requirements=
                required_requirements,

                ai_results=
                analysis_result.get(
                    "required_requirements",
                    []
                )
            )
        )

        # ---------------------------------------------
        # Normalize technology requirements
        # ---------------------------------------------

        normalized_technologies = (
            self._normalize_requirement_group(
                original_requirements=
                technology_requirements,

                ai_results=
                analysis_result.get(
                    "technology_requirements",
                    []
                )
            )
        )

        # ---------------------------------------------
        # Normalize preferred requirements
        # ---------------------------------------------

        normalized_preferred = (
            self._normalize_requirement_group(
                original_requirements=
                preferred_requirements,

                ai_results=
                analysis_result.get(
                    "preferred_requirements",
                    []
                )
            )
        )

        return {
            "required_requirements":
            normalized_required,

            "technology_requirements":
            normalized_technologies,

            "preferred_requirements":
            normalized_preferred,

            "strengths": (
                analysis_result.get(
                    "strengths",
                    []
                )
            ),

            "gaps": (
                analysis_result.get(
                    "gaps",
                    []
                )
            ),

            "overall_assessment": (
                analysis_result.get(
                    "overall_assessment",
                    ""
                )
            )
        }

    # =========================================================
    # NORMALIZE REQUIREMENT GROUP
    # =========================================================

    def _normalize_requirement_group(
        self,
        original_requirements: list,
        ai_results: list
    ) -> list:

        normalized_results = []

        ai_lookup = {}

        # ---------------------------------------------
        # Build lookup from AI response
        # ---------------------------------------------

        for item in ai_results:

            if not isinstance(
                item,
                dict
            ):
                continue

            requirement = item.get(
                "requirement"
            )

            if requirement:

                ai_lookup[
                    requirement.strip()
                ] = item

        # ---------------------------------------------
        # Ensure every original requirement exists
        # ---------------------------------------------

        for original in original_requirements:

            if not isinstance(
                original,
                dict
            ):
                continue

            requirement_text = (
                original.get(
                    "requirement",
                    ""
                )
            )

            if not requirement_text:
                continue

            ai_item = ai_lookup.get(
                requirement_text.strip()
            )

            # -----------------------------------------
            # AI evaluated requirement
            # -----------------------------------------

            if ai_item:

                score = ai_item.get(
                    "score",
                    0
                )

                try:

                    score = float(score)

                except (
                    ValueError,
                    TypeError
                ):

                    score = 0

                score = max(
                    0,
                    min(
                        100,
                        score
                    )
                )

                evidence_level = (
                    ai_item.get(
                        "evidence_level",
                        "none"
                    )
                )

                # Protect against invalid evidence levels

                if evidence_level not in (
                    "direct",
                    "indirect",
                    "none"
                ):

                    evidence_level = "none"

                evidence = (
                    ai_item.get(
                        "evidence",
                        []
                    )
                )

                if not isinstance(
                    evidence,
                    list
                ):

                    evidence = []

                normalized_results.append(
                    {
                        "requirement":
                        requirement_text,

                        "category":
                        original.get(
                            "category",
                            "technical"
                        ),

                        "importance":
                        original.get(
                            "importance",
                            "medium"
                        ),

                        "score":
                        round(
                            score,
                            2
                        ),

                        "evidence_level":
                        evidence_level,

                        "evidence":
                        evidence,

                        "reason":
                        ai_item.get(
                            "reason",
                            ""
                        )
                    }
                )

            # -----------------------------------------
            # Requirement omitted by AI
            # -----------------------------------------

            else:

                logger.warning(
                    "AI omitted requirement: %s",
                    requirement_text
                )

                normalized_results.append(
                    {
                        "requirement":
                        requirement_text,

                        "category":
                        original.get(
                            "category",
                            "technical"
                        ),

                        "importance":
                        original.get(
                            "importance",
                            "medium"
                        ),

                        "score":
                        0,

                        "evidence_level":
                        "none",

                        "evidence":
                        [],

                        "reason": (
                            "The requirement was not "
                            "evaluated by the AI."
                        )
                    }
                )

        return normalized_results

    # =========================================================
    # RESPONSE PARSER
    # =========================================================

    def _parse_response(
        self,
        response_text: str
    ) -> dict:

        cleaned_response = (
            response_text
            .strip()
        )

        # ---------------------------------------------
        # Remove markdown code blocks
        # ---------------------------------------------

        if cleaned_response.startswith(
            "```json"
        ):

            cleaned_response = (
                cleaned_response[
                    len("```json"):
                ]
            )

        elif cleaned_response.startswith(
            "```"
        ):

            cleaned_response = (
                cleaned_response[
                    len("```"):
                ]
            )

        if cleaned_response.endswith(
            "```"
        ):

            cleaned_response = (
                cleaned_response[:-3]
            )

        # ---------------------------------------------
        # Parse JSON
        # ---------------------------------------------

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