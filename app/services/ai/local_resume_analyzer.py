import re


class LocalResumeAnalyzer:

    SKILLS = [
        "Python",
        "C",
        "C++",
        "Java",
        "JavaScript",
        "TypeScript",

        "FastAPI",
        "Django",
        "Flask",
        "React",
        "Node.js",

        "HTML",
        "CSS",
        "Tailwind CSS",

        "PostgreSQL",
        "MySQL",
        "MongoDB",
        "Redis",
        "SQL",
        "NoSQL",

        "AWS",
        "EC2",
        "RDS",
        "S3",
        "Route53",
        "IAM",

        "Docker",
        "Kubernetes",
        "Git",
        "GitHub",
        "CI/CD",

        "Apache Spark",
        "Hadoop",
        "Kafka",

        "SQLAlchemy",
        "REST API",
        "RESTful API",
        "Microservices",

        "Machine Learning",
        "Deep Learning",
        "TensorFlow",
        "PyTorch",
        "OpenCV",
        "YOLO",
        "YOLOv8",

        "Pandas",
        "NumPy",
        "Scikit-learn",
    ]

    DEGREE_PATTERNS = [
        r"\bM\.?S\.?c\.?\b",
        r"\bM\.?Tech\b",
        r"\bB\.?S\.?c\.?\b",
        r"\bB\.?Tech\b",
        r"\bB\.?E\.?\b",
        r"\bMCA\b",
        r"\bMBA\b",
        r"\bPh\.?D\b",
        r"\bBachelor(?:'s)?\b",
        r"\bMaster(?:'s)?\b",
        r"\bDoctorate\b",
    ]

    EXPERIENCE_SECTION_HEADERS = [
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "employment history",
    ]

    EDUCATION_SECTION_HEADERS = [
        "education",
        "academic background",
        "academic qualifications",
    ]

    def analyze(self, resume_text: str) -> dict:
        if not resume_text or not resume_text.strip():
            return self._empty_result()

        text = self._normalize_text(resume_text)

        skills = self._extract_skills(text)
        experience = self._extract_experience(text)
        education = self._extract_education(text)
        summary = self._extract_summary(text)

        return {
            "skills": skills,
            "experience": experience,
            "education": education,
            "summary": summary,
        }

    def _normalize_text(self, text: str) -> str:
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        return text.strip()

    def _extract_skills(self, text: str) -> list[str]:
        skills = []

        for skill in self.SKILLS:
            pattern = re.compile(
                r"(?<![\w+#.])"
                + re.escape(skill)
                + r"(?![\w+#.])",
                re.IGNORECASE,
            )

            if pattern.search(text):
                skills.append(skill)

        return skills

    def _extract_experience(self, text: str) -> list[dict]:
        section = self._extract_section(
            text,
            self.EXPERIENCE_SECTION_HEADERS,
        )

        if not section:
            return []

        entries = []

        lines = [
            line.strip()
            for line in section.split("\n")
            if line.strip()
        ]

        current = None

        for line in lines:

            if self._looks_like_role(line):

                if current:
                    entries.append(current)

                current = {
                    "role": line,
                    "company": "",
                    "duration": "",
                    "technologies": [],
                }

                continue

            if current is None:
                continue

            duration = self._extract_duration(line)

            if duration and not current["duration"]:
                current["duration"] = duration
                continue

            if not current["company"] and self._looks_like_company(line):
                current["company"] = line

        if current:
            entries.append(current)

        for entry in entries:
            entry["technologies"] = self._extract_skills(
                " ".join(
                    [
                        entry.get("role", ""),
                        entry.get("company", ""),
                        entry.get("duration", ""),
                    ]
                )
            )

        return entries

    def _extract_education(self, text: str) -> list[dict]:
        section = self._extract_section(
            text,
            self.EDUCATION_SECTION_HEADERS,
        )

        if not section:
            return []

        entries = []

        lines = [
            line.strip()
            for line in section.split("\n")
            if line.strip()
        ]

        for line in lines:

            if not self._looks_like_degree(line):
                continue

            entries.append(
                {
                    "degree": line,
                    "institution": "",
                    "duration": self._extract_duration(line),
                }
            )

        return entries

    def _extract_summary(self, text: str) -> str | None:
        section = self._extract_section(
            text,
            [
                "summary",
                "professional summary",
                "profile",
                "objective",
            ],
        )

        if not section:
            return None

        lines = [
            line.strip()
            for line in section.split("\n")
            if line.strip()
        ]

        if not lines:
            return None

        return " ".join(lines)[:1000]

    def _extract_section(
        self,
        text: str,
        headers: list[str],
    ) -> str | None:

        lines = text.split("\n")

        normalized_headers = {
            header.lower().strip()
            for header in headers
        }

        start_index = None

        for index, line in enumerate(lines):
            normalized = line.strip().lower()

            if normalized in normalized_headers:
                start_index = index + 1
                break

        if start_index is None:
            return None

        section_lines = []

        known_sections = (
            self.EXPERIENCE_SECTION_HEADERS
            + self.EDUCATION_SECTION_HEADERS
            + [
                "skills",
                "technical skills",
                "projects",
                "certifications",
                "summary",
                "professional summary",
                "profile",
                "objective",
            ]
        )

        known_sections = {
            section.lower()
            for section in known_sections
        }

        for line in lines[start_index:]:

            normalized = line.strip().lower()

            if normalized in known_sections:
                break

            section_lines.append(line)

        return "\n".join(section_lines).strip()

    def _looks_like_role(self, line: str) -> bool:
        role_keywords = [
            "developer",
            "engineer",
            "intern",
            "analyst",
            "manager",
            "architect",
            "scientist",
            "consultant",
            "associate",
            "lead",
            "administrator",
        ]

        lowered = line.lower()

        return any(
            keyword in lowered
            for keyword in role_keywords
        )

    def _looks_like_company(self, line: str) -> bool:
        company_keywords = [
            "technologies",
            "technology",
            "software",
            "solutions",
            "systems",
            "labs",
            "inc",
            "ltd",
            "llc",
            "corp",
        ]

        lowered = line.lower()

        return any(
            keyword in lowered
            for keyword in company_keywords
        )

    def _looks_like_degree(self, line: str) -> bool:
        return any(
            re.search(
                pattern,
                line,
                re.IGNORECASE,
            )
            for pattern in self.DEGREE_PATTERNS
        )

    def _extract_duration(self, text: str) -> str:
        patterns = [
            r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
            r"[a-z]*\s+\d{4}\s*[-–—]\s*"
            r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
            r"[a-z]*\s+\d{4}\b",

            r"\b\d{4}\s*[-–—]\s*(?:Present|Current|\d{4})\b",

            r"\b\d+\+?\s+years?\b",

            r"\b\d+\s+years?\s+\d+\s+months?\b",
        ]

        for pattern in patterns:
            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if match:
                return match.group(0)

        return ""

    def _empty_result(self) -> dict:
        return {
            "skills": [],
            "experience": [],
            "education": [],
            "summary": None,
        }