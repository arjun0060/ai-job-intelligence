class RequirementBuilder:

    def build(
        self,
        job_data: dict
    ) -> dict:

        required_requirements = []
        technology_requirements = []
        preferred_requirements = []

        # ---------------------------------
        # REQUIRED SKILLS
        # ---------------------------------

        for skill in job_data.get(
            "required_skills",
            []
        ):

            required_requirements.append({
                "requirement": skill,
                "category": "technical",
                "importance": "high",
                "source": "required_skills"
            })


        # ---------------------------------
        # TECHNOLOGIES
        # ---------------------------------

        for technology in job_data.get(
            "technologies",
            []
        ):

            technology_requirements.append({
                "requirement": technology,
                "category": "technology",
                "importance": "high",
                "source": "technologies"
            })


        # ---------------------------------
        # RESPONSIBILITIES
        # ---------------------------------

        for responsibility in job_data.get(
            "responsibilities",
            []
        ):

            required_requirements.append({
                "requirement": responsibility,
                "category": "responsibility",
                "importance": "medium",
                "source": "responsibilities"
            })


        # ---------------------------------
        # PREFERRED SKILLS
        # ---------------------------------

        for skill in job_data.get(
            "preferred_skills",
            []
        ):

            preferred_requirements.append({
                "requirement": skill,
                "category": "preferred",
                "importance": "low",
                "source": "preferred_skills"
            })


        # ---------------------------------
        # EDUCATION
        # ---------------------------------

        education_requirements = (
            job_data.get(
                "education_requirements",
                []
            )
        )


        # ---------------------------------
        # EXPERIENCE
        # ---------------------------------

        experience_requirement = (
            job_data.get(
                "experience_requirement",
                {}
            )
        )


        return {
            "required_requirements":
                required_requirements,

            "technology_requirements":
                technology_requirements,

            "preferred_requirements":
                preferred_requirements,

            "education_requirements":
                education_requirements,

            "experience_requirement":
                experience_requirement
        }