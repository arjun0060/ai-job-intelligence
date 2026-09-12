import re


class LocalResumeAnalyzer:

    SKILLS = [
        "Python",
        "FastAPI",
        "Django",
        "Flask",
        "JavaScript",
        "TypeScript",
        "React",
        "Node.js",
        "PostgreSQL",
        "MySQL",
        "MongoDB",
        "Redis",
        "Docker",
        "Kubernetes",
        "AWS",
        "Git",
        "CI/CD",
        "Machine Learning",
        "TensorFlow",
        "PyTorch",
        "OpenCV",
        "YOLO",
        "SQLAlchemy",
        "REST API"
    ]

    def analyze(self, resume_text: str) -> dict:

        skills = []

        for skill in self.SKILLS:

            pattern = re.compile(
                r"\b" + re.escape(skill) + r"\b",
                re.IGNORECASE
            )

            if pattern.search(resume_text):
                skills.append(skill)

        return {
            "skills": skills,
            "experience": [],
            "education": [],
            "summary": None
        }