import re
from datetime import datetime


class DeterministicMatcher:

    def normalize(self, value: str) -> str:
        """
        Normalize text for comparison.
        """

        if not value:
            return ""

        return re.sub(
            r"[^a-z0-9+#.]",
            "",
            value.lower().strip()
        )


    def calculate_skill_match(
        self,
        resume_skills: list[str],
        required_skills: list[str],
        preferred_skills: list[str]
    ) -> dict:

        normalized_resume_skills = {
            self.normalize(skill): skill
            for skill in resume_skills
        }

        matched_required = []
        missing_required = []
        matched_preferred = []
        missing_preferred = []


        # Required skills

        for skill in required_skills:

            normalized_skill = self.normalize(skill)

            if normalized_skill in normalized_resume_skills:

                matched_required.append(skill)

            else:

                missing_required.append(skill)


        # Preferred skills

        for skill in preferred_skills:

            normalized_skill = self.normalize(skill)

            if normalized_skill in normalized_resume_skills:

                matched_preferred.append(skill)

            else:

                missing_preferred.append(skill)


        required_score = (
            len(matched_required)
            / len(required_skills)
            * 100
            if required_skills
            else 100
        )

        preferred_score = (
            len(matched_preferred)
            / len(preferred_skills)
            * 100
            if preferred_skills
            else 100
        )


        # Required skills = 80% weight
        # Preferred skills = 20% weight

        score = (
            required_score * 0.8
            +
            preferred_score * 0.2
        )


        return {
            "score": round(score, 2),

            "matched_required_skills":
                matched_required,

            "missing_required_skills":
                missing_required,

            "matched_preferred_skills":
                matched_preferred,

            "missing_preferred_skills":
                missing_preferred
        }


    def calculate_experience_match(
        self,
        candidate_years: float | None,
        minimum_years: int | None
    ) -> dict:

        if minimum_years is None:

            return {
                "score": 100,
                "reason":
                    "No minimum experience requirement specified"
            }


        if candidate_years is None:

            return {
                "score": 50,
                "reason":
                    "Candidate experience duration could not be determined"
            }


        if candidate_years >= minimum_years:

            return {
                "score": 100,
                "reason":
                    "Candidate meets the minimum experience requirement"
            }


        score = (
            candidate_years
            / minimum_years
            * 100
        )


        return {
            "score": round(score, 2),

            "reason": (
                f"Candidate has approximately "
                f"{candidate_years} years of experience "
                f"compared with {minimum_years} "
                f"years required"
            )
        }


    def calculate_education_match(
        self,
        resume_education: list[dict],
        education_requirements: list[str]
    ) -> dict:

        if not education_requirements:

            return {
                "score": 100,
                "matched_requirements": [],
                "reason":
                    "No education requirement specified"
            }


        resume_degrees = " ".join(
            [
                education.get("degree", "").lower()
                for education in resume_education
            ]
        )


        matched_requirements = []

        for requirement in education_requirements:

            requirement_lower = requirement.lower()

            # Basic keyword matching

            keywords = [
                word
                for word in requirement_lower.split()
                if len(word) > 3
            ]

            if any(
                keyword in resume_degrees
                for keyword in keywords
            ):

                matched_requirements.append(
                    requirement
                )


        score = (
            len(matched_requirements)
            / len(education_requirements)
            * 100
        )


        return {
            "score": round(score, 2),

            "matched_requirements":
                matched_requirements,

            "reason":
                "Education requirements compared "
                "against candidate degrees"
        }

    def calculate_total_experience(
        self,
        experience_entries: list[dict]
    ) -> float | None:

        if not experience_entries:
            return None

        total_months = 0

        month_map = {
            "jan": 1,
            "feb": 2,
            "mar": 3,
            "apr": 4,
            "may": 5,
            "jun": 6,
            "jul": 7,
            "aug": 8,
            "sep": 9,
            "oct": 10,
            "nov": 11,
            "dec": 12
        }

        for experience in experience_entries:

            duration = experience.get(
                "duration",
                ""
            )

            try:

                # Example:
                # Jan 2025 – Feb 2026

                parts = re.split(
                    r"\s*[–-]\s*",
                    duration
                )

                if len(parts) != 2:
                    continue

                start = parts[0].strip()
                end = parts[1].strip()


                def parse_date(date_string):

                    tokens = date_string.split()

                    if len(tokens) != 2:
                        return None

                    month = month_map.get(
                        tokens[0][:3].lower()
                    )

                    year = int(tokens[1])

                    if not month:
                        return None

                    return year, month


                start_date = parse_date(start)
                end_date = parse_date(end)

                if not start_date or not end_date:
                    continue


                start_year, start_month = start_date
                end_year, end_month = end_date


                months = (
                    (end_year - start_year) * 12
                    +
                    (end_month - start_month)
                )

                if months > 0:

                    total_months += months

            except Exception:
                continue


        if total_months == 0:
            return None

        return round(
            total_months / 12,
            2
        )