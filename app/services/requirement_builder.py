class RequirementBuilder:
    """Build the normalized requirement groups used by match analysis."""

    def build(self, job_data: dict) -> dict:
        required_requirements = []
        technology_requirements = []
        preferred_requirements = []

        for item in job_data.get("required_skills") or []:
            requirement = self._text(item)
            if requirement:
                required_requirements.append(
                    self._requirement(
                        item=item,
                        requirement=requirement,
                        category="technical",
                        importance="high",
                        source="required_skills",
                    )
                )

        for item in job_data.get("technologies") or []:
            requirement = self._text(item)
            if requirement:
                technology_requirements.append(
                    self._requirement(
                        item=item,
                        requirement=requirement,
                        category="technology",
                        importance="high",
                        source="technologies",
                    )
                )

        for item in job_data.get("responsibilities") or []:
            requirement = self._text(item)
            if requirement:
                required_requirements.append(
                    self._requirement(
                        item=item,
                        requirement=requirement,
                        category="responsibility",
                        importance="medium",
                        source="responsibilities",
                    )
                )

        for item in job_data.get("education_requirements") or []:
            requirement = self._text(item)
            if requirement:
                required_requirements.append(
                    self._requirement(
                        item=item,
                        requirement=requirement,
                        category="education",
                        importance="medium",
                        source="education_requirements",
                    )
                )

        experience_requirement = (
            job_data.get("experience_requirement") or {}
        )
        experience_text = self._experience_text(
            experience_requirement
        )
        if experience_text:
            required_requirements.append(
                {
                    "requirement": experience_text,
                    "category": "experience",
                    "importance": "high",
                    "source": "experience_requirement",
                }
            )

        for item in job_data.get("preferred_skills") or []:
            requirement = self._text(item)
            if requirement:
                preferred_requirements.append(
                    self._requirement(
                        item=item,
                        requirement=requirement,
                        category="preferred",
                        importance="low",
                        source="preferred_skills",
                    )
                )

        return {
            "required_requirements": required_requirements,
            "technology_requirements": technology_requirements,
            "preferred_requirements": preferred_requirements,
            "education_requirements": job_data.get(
                "education_requirements", []
            ),
            "experience_requirement": experience_requirement,
        }

    @staticmethod
    def _text(item) -> str | None:
        if isinstance(item, dict):
            return item.get("requirement")
        if isinstance(item, str):
            return item
        return None

    @staticmethod
    def _requirement(
        item,
        requirement: str,
        category: str,
        importance: str,
        source: str,
    ) -> dict:
        return {
            "requirement": requirement,
            "category": (
                item.get("category", category)
                if isinstance(item, dict)
                else category
            ),
            "importance": (
                item.get("importance", importance)
                if isinstance(item, dict)
                else importance
            ),
            "source": source,
        }

    @staticmethod
    def _experience_text(experience_requirement: dict) -> str | None:
        minimum = experience_requirement.get("minimum_years")
        maximum = experience_requirement.get("maximum_years")
        description = experience_requirement.get("description")

        if minimum is not None and maximum is not None:
            return (
                f"At least {minimum:g} years of experience "
                f"and no more than {maximum:g} years"
            )

        if minimum is not None:
            return f"At least {minimum:g} years of professional experience"

        if maximum is not None:
            return f"No more than {maximum:g} years of professional experience"

        if description:
            return str(description).strip()

        return None
