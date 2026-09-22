from typing import Any


class TextChunker:

    @staticmethod
    def chunk_resume(resume_data: dict) -> list[dict[str, Any]]:
        chunks = []

        TextChunker._add_chunks(
            chunks,
            resume_data.get("summary"),
            "resume_summary",
        )

        TextChunker._add_chunks(
            chunks,
            resume_data.get("skills"),
            "resume_skill",
        )

        TextChunker._add_chunks(
            chunks,
            resume_data.get("experience"),
            "resume_experience",
        )

        TextChunker._add_chunks(
            chunks,
            resume_data.get("education"),
            "resume_education",
        )

        return chunks

    @staticmethod
    def chunk_job(job_data: dict) -> list[dict[str, Any]]:
        chunks = []

        TextChunker._add_chunks(
            chunks,
            job_data.get("required_skills"),
            "job_required",
        )

        TextChunker._add_chunks(
            chunks,
            job_data.get("responsibilities"),
            "job_responsibility",
        )

        TextChunker._add_chunks(
            chunks,
            job_data.get("technologies"),
            "job_technology",
        )

        TextChunker._add_chunks(
            chunks,
            job_data.get("preferred_skills"),
            "job_preferred",
        )

        TextChunker._add_chunks(
            chunks,
            job_data.get("supporting_competencies"),
            "job_competency",
        )

        return chunks

    @staticmethod
    def _add_chunks(
        chunks: list[dict[str, Any]],
        value: Any,
        chunk_type: str,
    ) -> None:

        if not value:
            return

        if isinstance(value, dict):
            values = list(value.values())
        elif isinstance(value, (list, tuple)):
            values = value
        else:
            values = [value]

        for item in values:

            if isinstance(item, dict):
                content = TextChunker._dict_to_text(item)
            else:
                content = str(item).strip()

            if not content:
                continue

            chunks.append(
                {
                    "chunk_type": chunk_type,
                    "content": content,
                }
            )

    @staticmethod
    def _dict_to_text(data: dict) -> str:
        parts = []

        for key, value in data.items():

            if value is None:
                continue

            if isinstance(value, (list, tuple)):
                value = ", ".join(str(item) for item in value)

            parts.append(
                f"{key.replace('_', ' ').title()}: {value}"
            )

        return " | ".join(parts)