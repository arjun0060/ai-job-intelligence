from app.services.ai.gemini_match_analyzer import (
    GeminiMatchAnalyzer
)

from app.services.requirement_builder import (
    RequirementBuilder
)


class SemanticMatcher:

    def __init__(self):

        self.gemini = GeminiMatchAnalyzer()

        self.requirement_builder = (
            RequirementBuilder()
        )


    # =========================================================
    # BUILD CANDIDATE PROFILE
    # =========================================================

    def build_candidate_profile(
        self,
        resume_data: dict
    ) -> dict:

        return {
            "skills": resume_data.get(
                "skills",
                []
            ),

            "professional_experience": resume_data.get(
                "experience",
                []
            ),

            "education": resume_data.get(
                "education",
                []
            ),

            "professional_summary": resume_data.get(
                "summary",
                ""
            )
        }


    # =========================================================
    # EVALUATE
    # =========================================================

    def evaluate(
        self,
        resume_data: dict,
        job_data: dict
    ) -> dict:

        # ---------------------------------------------
        # Build candidate profile
        # ---------------------------------------------

        candidate_profile = (
            self.build_candidate_profile(
                resume_data
            )
        )


        # ---------------------------------------------
        # Build requirements
        # ---------------------------------------------

        job_requirements = (
            self.requirement_builder.build(
                job_data
            )
        )


        # ---------------------------------------------
        # Semantic evaluation
        # ---------------------------------------------

        semantic_result = (
            self.gemini.analyze_semantic_match(
                candidate_profile=candidate_profile,

                required_requirements=
                    job_requirements[
                        "required_requirements"
                    ],

                technology_requirements=
                    job_requirements[
                        "technology_requirements"
                    ],

                preferred_requirements=
                    job_requirements[
                        "preferred_requirements"
                    ],

                retrieved_evidence={}
            )
        )


        return semantic_result