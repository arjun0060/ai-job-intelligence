import re


class LocalJobAnalyzer:

    TECHNOLOGIES = [
        "python",
        "java",
        "javascript",
        "typescript",
        "c++",
        "c#",
        "go",
        "rust",
        "scala",
        "fastapi",
        "django",
        "flask",
        "react",
        "node.js",
        "nodejs",
        "postgresql",
        "postgres",
        "mysql",
        "mongodb",
        "redis",
        "kafka",
        "spark",
        "hadoop",
        "docker",
        "kubernetes",
        "aws",
        "azure",
        "gcp",
        "terraform",
        "git",
        "linux",
    ]

    EDUCATION_KEYWORDS = [
        "bachelor",
        "b.tech",
        "b.e",
        "b.sc",
        "master",
        "m.tech",
        "m.sc",
        "mba",
        "degree",
    ]

    PREFERRED_KEYWORDS = [
        "preferred",
        "nice to have",
        "bonus",
        "plus",
        "good to have",
        "optional",
    ]

    def analyze(self, job_description: str) -> dict:

        text = job_description or ""
        normalized_text = text.lower()

        technologies = self._extract_technologies(normalized_text)

        preferred_section = self._extract_preferred_section(
            text
        )

        preferred_skills = self._extract_technologies(
            preferred_section.lower()
        )

        required_skills = [
            tech
            for tech in technologies
            if tech not in preferred_skills
        ]

        experience_requirement = self._extract_experience(
            normalized_text
        )

        education_requirements = self._extract_education(
            normalized_text
        )

        responsibilities = self._extract_responsibilities(
            text
        )

        key_keywords = self._extract_keywords(
            normalized_text,
            technologies
        )

        return {
            "required_skills": required_skills,
            "supporting_competencies": [],
            "preferred_skills": preferred_skills,
            "technologies": technologies,
            "experience_requirement": experience_requirement,
            "education_requirements": education_requirements,
            "responsibilities": responsibilities,
            "key_keywords": key_keywords,
            "summary": self._build_summary(
                required_skills,
                technologies
            ),
        }

    def _extract_technologies(self, text: str) -> list:

        found = []

        for technology in self.TECHNOLOGIES:
            pattern = r"(?<!\w)" + re.escape(
                technology.lower()
            ) + r"(?!\w)"

            if re.search(pattern, text):
                normalized = self._normalize_technology(
                    technology
                )

                if normalized not in found:
                    found.append(normalized)

        return found

    @staticmethod
    def _normalize_technology(technology: str) -> str:

        mapping = {
            "python": "Python",
            "java": "Java",
            "javascript": "JavaScript",
            "typescript": "TypeScript",
            "c++": "C++",
            "c#": "C#",
            "go": "Go",
            "rust": "Rust",
            "scala": "Scala",
            "fastapi": "FastAPI",
            "django": "Django",
            "flask": "Flask",
            "react": "React",
            "node.js": "Node.js",
            "nodejs": "Node.js",
            "postgresql": "PostgreSQL",
            "postgres": "PostgreSQL",
            "mysql": "MySQL",
            "mongodb": "MongoDB",
            "redis": "Redis",
            "kafka": "Kafka",
            "spark": "Apache Spark",
            "hadoop": "Hadoop",
            "docker": "Docker",
            "kubernetes": "Kubernetes",
            "aws": "AWS",
            "azure": "Azure",
            "gcp": "GCP",
            "terraform": "Terraform",
            "git": "Git",
            "linux": "Linux",
        }

        return mapping.get(
            technology.lower(),
            technology
        )

    def _extract_preferred_section(
        self,
        text: str
    ) -> str:

        lines = text.splitlines()

        preferred_lines = []
        collecting = False

        for line in lines:

            lower = line.lower()

            if any(
                keyword in lower
                for keyword in self.PREFERRED_KEYWORDS
            ):
                collecting = True

            if collecting:
                preferred_lines.append(line)

        return "\n".join(preferred_lines)

    @staticmethod
    def _extract_experience(text: str) -> dict:

        patterns = [
            r"(\d+)\+?\s*(?:years?|yrs?)",
            r"minimum\s*(?:of\s*)?(\d+)\s*(?:years?|yrs?)",
        ]

        for pattern in patterns:

            match = re.search(pattern, text)

            if match:
                return {
                    "minimum_years": int(match.group(1))
                }

        return {}

    def _extract_education(self, text: str) -> list:

        results = []

        for keyword in self.EDUCATION_KEYWORDS:

            if keyword in text:
                results.append(keyword)

        return list(dict.fromkeys(results))

    @staticmethod
    def _extract_responsibilities(text: str) -> list:

        responsibilities = []

        for line in text.splitlines():

            cleaned = line.strip()

            if not cleaned:
                continue

            if cleaned.startswith(("-", "•", "*")):

                cleaned = cleaned.lstrip(
                    "-•* "
                ).strip()

                if len(cleaned) > 20:
                    responsibilities.append(cleaned)

        return responsibilities[:10]

    @staticmethod
    def _extract_keywords(
        text: str,
        technologies: list
    ) -> list:

        keywords = []

        for technology in technologies:
            keywords.append(technology)

        return list(dict.fromkeys(keywords))

    @staticmethod
    def _build_summary(
        required_skills: list,
        technologies: list
    ) -> str:

        if not required_skills and not technologies:
            return "Job requirements extracted using local analysis."

        return (
            "Requirements extracted using local analysis. "
            f"Identified {len(technologies)} technologies "
            f"and {len(required_skills)} required skills."
        )