from typing import Protocol


class ResumeAnalyzer(Protocol):

    def analyze(
        self,
        resume_text: str
    ) -> dict:
        ...