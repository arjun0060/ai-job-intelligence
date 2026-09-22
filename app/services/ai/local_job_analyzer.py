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
        "react.js",
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
        "html5",
        "html",
        "css3",
        "css",
        "scss",
        "graphql",
        "websockets",
        "redux",
        "zustand",
        "webpack",
        "babel",
        "vite",
        "parcel",
        "material ui",
        "tailwind css",
        "ant design",
        "jest",
        "react testing library",
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
        "graduate",
    ]

    PREFERRED_KEYWORDS = [
        "preferred",
        "nice to have",
        "bonus",
        "plus",
        "good to have",
        "optional",
    ]

    SECTION_HEADERS = {
        "responsibilities",
        "requirements",
        "qualifications",
        "skills",
        "preferred qualifications",
        "preferred skills",
        "nice to have",
        "eligibility",
        "education",
    }

    def analyze(self, job_description: str) -> dict:
        text = job_description or ""
        normalized_text = text.lower()

        sections = self._extract_sections(text)

        technologies = self._extract_technologies(normalized_text)

        preferred_text = self._get_preferred_text(sections)

        preferred_technologies = self._extract_technologies(
            preferred_text.lower()
        )

        requirement_lines = self._extract_requirement_lines(
            sections
        )

        responsibilities = self._extract_responsibilities_from_sections(
            sections
        )

        generic_requirements = self._extract_generic_requirements(
            requirement_lines,
            technologies,
            preferred_technologies,
        )

        required_skills = []

        for requirement in generic_requirements:
            if requirement not in required_skills:
                required_skills.append(requirement)

        preferred_skills = []

        for requirement in self._extract_preferred_requirements(
            preferred_text
        ):
            if requirement not in preferred_skills:
                preferred_skills.append(requirement)

        for technology in preferred_technologies:
            if technology not in preferred_skills:
                preferred_skills.append(technology)

        experience_requirement = self._extract_experience(
            normalized_text
        )

        education_requirements = self._extract_education(
            normalized_text
        )

        key_keywords = self._extract_keywords(
            normalized_text,
            technologies,
        )

        summary = self._build_summary(
            required_skills=required_skills,
            technologies=technologies,
            responsibilities=responsibilities,
        )

        return {
            "required_skills": required_skills[:20],
            "supporting_competencies": [],
            "preferred_skills": preferred_skills[:20],
            "technologies": technologies,
            "experience_requirement": experience_requirement,
            "education_requirements": education_requirements,
            "responsibilities": responsibilities[:10],
            "key_keywords": key_keywords,
            "summary": summary,
        }

    def _extract_sections(self, text: str) -> dict[str, list[str]]:
        sections = {}
        current_section = "general"

        sections[current_section] = []

        for raw_line in text.splitlines():
            line = raw_line.strip()

            if not line:
                continue

            normalized = re.sub(
                r"^[•\-\*\u2022]+\s*",
                "",
                line,
            ).strip()

            header = normalized.rstrip(":").strip().lower()

            if header in self.SECTION_HEADERS:
                current_section = header
                sections.setdefault(current_section, [])
                continue

            sections.setdefault(current_section, []).append(
                normalized
            )

        return sections

    def _extract_requirement_lines(
        self,
        sections: dict[str, list[str]],
    ) -> list[str]:
        requirement_lines = []

        requirement_sections = {
            "requirements",
            "qualifications",
            "skills",
            "preferred qualifications",
            "preferred skills",
            "nice to have",
        }

        for section_name in requirement_sections:
            for line in sections.get(section_name, []):
                if self._is_meaningful_requirement(line):
                    requirement_lines.append(line)

        return list(dict.fromkeys(requirement_lines))

    def _extract_generic_requirements(
        self,
        requirement_lines: list[str],
        technologies: list[str],
        preferred_technologies: list[str],
    ) -> list[str]:
        requirements = []

        preferred_set = {
            technology.lower()
            for technology in preferred_technologies
        }

        for line in requirement_lines:
            cleaned = self._clean_requirement(line)

            if not cleaned:
                continue

            if cleaned.lower() in preferred_set:
                continue

            if self._is_preferred_requirement(cleaned):
                continue

            # Experience duration is modeled separately so it can be
            # evaluated quantitatively instead of as a text requirement.
            if re.search(
                r"\b(?:at least|minimum|\d+\s*[-–+]?\s*)\d*\s*years?\b",
                cleaned.lower(),
            ) or re.search(
                r"\b\d+\s*[-–]\s*\d+\s*years?\b",
                cleaned.lower(),
            ):
                continue

            requirements.append(cleaned)

            # If a line is only a technology name, it will
            # already be represented in the technology list.
            # Keeping it here is still useful for deterministic
            # matching, so we do not remove it.

        return list(dict.fromkeys(requirements))

    def _extract_preferred_requirements(
        self,
        preferred_text: str,
    ) -> list[str]:
        requirements = []

        for line in preferred_text.splitlines():
            cleaned = self._clean_requirement(line)

            if not cleaned:
                continue

            if self._is_meaningful_requirement(cleaned):
                requirements.append(cleaned)

        return list(dict.fromkeys(requirements))

    def _extract_technologies(self, text: str) -> list[str]:
        found = []

        # Sort longest first so that:
        # "react testing library" is detected before "react"
        technologies = sorted(
            self.TECHNOLOGIES,
            key=len,
            reverse=True,
        )

        for technology in technologies:
            pattern = (
                r"(?<!\w)"
                + re.escape(technology.lower())
                + r"(?!\w)"
            )

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
            "react.js": "React",
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
            "html5": "HTML5",
            "html": "HTML",
            "css3": "CSS3",
            "css": "CSS",
            "scss": "SCSS",
            "graphql": "GraphQL",
            "websockets": "WebSockets",
            "redux": "Redux",
            "zustand": "Zustand",
            "webpack": "Webpack",
            "babel": "Babel",
            "vite": "Vite",
            "parcel": "Parcel",
            "material ui": "Material UI",
            "tailwind css": "Tailwind CSS",
            "ant design": "Ant Design",
            "jest": "Jest",
            "react testing library": "React Testing Library",
        }

        return mapping.get(
            technology.lower(),
            technology,
        )

    def _get_preferred_text(
        self,
        sections: dict[str, list[str]],
    ) -> str:
        preferred_sections = {
            "preferred qualifications",
            "preferred skills",
            "nice to have",
        }

        lines = []

        for section in preferred_sections:
            lines.extend(sections.get(section, []))

        return "\n".join(lines)

    @staticmethod
    def _extract_experience(text: str) -> dict:
        patterns = [
            r"(\d+)\s*[-–]\s*(\d+)\s*(?:years?|yrs?)",
            r"(\d+)\s*\+?\s*(?:years?|yrs?)",
            r"minimum\s+(?:of\s+)?(\d+)\s*(?:years?|yrs?)",
            r"at least\s+(\d+)\s*(?:years?|yrs?)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text)

            if not match:
                continue

            if len(match.groups()) >= 2:
                return {
                    "minimum_years": int(match.group(1)),
                    "maximum_years": int(match.group(2)),
                }

            return {
                "minimum_years": int(match.group(1))
            }

        return {}

    def _extract_education(self, text: str) -> list[str]:
        results = []

        for keyword in self.EDUCATION_KEYWORDS:
            if keyword in text:
                results.append(keyword)

        return list(dict.fromkeys(results))

    @staticmethod
    def _extract_responsibilities_from_sections(
        sections: dict[str, list[str]],
    ) -> list[str]:
        responsibilities = []

        for line in sections.get("responsibilities", []):
            cleaned = LocalJobAnalyzer._clean_requirement(line)

            if not cleaned or len(cleaned) <= 20:
                continue

            responsibilities.extend(
                LocalJobAnalyzer._split_responsibility(cleaned)
            )

        return list(dict.fromkeys(responsibilities))

    @staticmethod
    def _split_responsibility(line: str) -> list[str]:
        """Split common multi-action responsibility bullets into evaluable items."""
        patterns = (
            (
                r"^(.*?)\btroubleshoot, debug, and optimize\b(.*)$",
                lambda m: [
                    f"{m.group(1).strip()}Troubleshoot {m.group(2).strip()}".strip(),
                    f"{m.group(1).strip()}Debug {m.group(2).strip()}".strip(),
                    f"{m.group(1).strip()}Optimize {m.group(2).strip()}".strip(),
                ],
            ),
            (
                r"^(.*?)\bparticipate in code reviews, testing, and technical documentation\.?$",
                lambda m: [
                    f"{m.group(1).strip()}Participate in code reviews.",
                    f"{m.group(1).strip()}Participate in testing.",
                    f"{m.group(1).strip()}Contribute to technical documentation.",
                ],
            ),
            (
                r"^(.*?)\bdesign, implement, and deploy features\b(.*)$",
                lambda m: [
                    f"{m.group(1).strip()}Design features {m.group(2).strip()}".strip(),
                    f"{m.group(1).strip()}Implement features {m.group(2).strip()}".strip(),
                    f"{m.group(1).strip()}Deploy features {m.group(2).strip()}".strip(),
                ],
            ),
        )

        for pattern, builder in patterns:
            match = re.match(pattern, line, flags=re.IGNORECASE)
            if match:
                return list(dict.fromkeys(
                    item for item in builder(match) if len(item) > 20
                ))

        return [line]

    @staticmethod
    def _clean_requirement(line: str) -> str:
        cleaned = re.sub(
            r"^[•\-\*\u2022]+\s*",
            "",
            line,
        ).strip()

        cleaned = re.sub(
            r"\s+",
            " ",
            cleaned,
        )

        return cleaned

    @staticmethod
    def _is_meaningful_requirement(
        line: str,
    ) -> bool:
        cleaned = LocalJobAnalyzer._clean_requirement(line)

        if len(cleaned) < 8:
            return False

        ignored = {
            "requirements",
            "qualifications",
            "skills",
            "eligibility",
            "education",
            "preferred",
            "responsibilities",
        }

        return cleaned.lower() not in ignored

    @staticmethod
    def _is_preferred_requirement(
        text: str,
    ) -> bool:
        lowered = text.lower()

        return any(
            keyword in lowered
            for keyword in LocalJobAnalyzer.PREFERRED_KEYWORDS
        )

    @staticmethod
    def _extract_keywords(
        text: str,
        technologies: list[str],
    ) -> list[str]:
        keywords = list(technologies)

        generic_keywords = [
            "frontend",
            "backend",
            "api",
            "rest",
            "responsive design",
            "state management",
            "performance optimization",
            "testing",
            "code review",
            "problem solving",
            "agile",
            "security",
            "scalable web applications",
        ]

        for keyword in generic_keywords:
            if keyword in text:
                keywords.append(keyword)

        return list(dict.fromkeys(keywords))

    @staticmethod
    def _build_summary(
        required_skills: list[str],
        technologies: list[str],
        responsibilities: list[str],
    ) -> str:
        if not required_skills and not technologies:
            return (
                "Job requirements extracted using local analysis."
            )

        return (
            "Requirements extracted using local analysis. "
            f"Identified {len(technologies)} technologies, "
            f"{len(required_skills)} required skills, and "
            f"{len(responsibilities)} responsibilities."
        )