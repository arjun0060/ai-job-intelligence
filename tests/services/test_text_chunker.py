from app.services.embeddings.text_chunker import TextChunker


def test_chunk_resume_creates_expected_chunks():
    resume_data = {
        "summary": "Backend developer with Python experience.",
        "skills": {
            "programming": ["Python", "JavaScript"],
            "backend": ["FastAPI", "PostgreSQL"],
        },
        "experience": {
            "company": "Xplor Rides",
            "role": "Backend Developer",
        },
        "education": {
            "degree": "M.Sc. Computer Science",
        },
    }

    chunks = TextChunker.chunk_resume(resume_data)

    chunk_types = [
        chunk["chunk_type"]
        for chunk in chunks
    ]

    assert "resume_summary" in chunk_types
    assert "resume_skill" in chunk_types
    assert "resume_experience" in chunk_types
    assert "resume_education" in chunk_types


def test_resume_chunks_contain_content():
    resume_data = {
        "summary": "Python backend developer.",
        "skills": {
            "programming": ["Python", "JavaScript"],
        },
        "experience": {
            "role": "Backend Developer",
        },
        "education": {
            "degree": "M.Sc. Computer Science",
        },
    }

    chunks = TextChunker.chunk_resume(resume_data)

    assert len(chunks) == 4

    for chunk in chunks:
        assert "chunk_type" in chunk
        assert "content" in chunk
        assert chunk["content"]
        assert isinstance(chunk["content"], str)


def test_chunk_job_creates_expected_chunks():
    job_data = {
        "required_skills": [
            "Python",
            "FastAPI",
        ],
        "responsibilities": [
            "Build REST APIs",
            "Maintain backend services",
        ],
        "technologies": [
            "PostgreSQL",
            "Docker",
        ],
        "preferred_skills": [
            "AWS",
        ],
        "supporting_competencies": [
            "Agile",
        ],
    }

    chunks = TextChunker.chunk_job(job_data)

    chunk_types = [
        chunk["chunk_type"]
        for chunk in chunks
    ]

    assert "job_required" in chunk_types
    assert "job_responsibility" in chunk_types
    assert "job_technology" in chunk_types
    assert "job_preferred" in chunk_types


def test_job_chunks_contain_content():
    job_data = {
        "required_skills": ["Python"],
        "responsibilities": ["Build APIs"],
        "technologies": ["FastAPI"],
        "preferred_skills": ["AWS"],
        "supporting_competencies": ["Agile"],
    }

    chunks = TextChunker.chunk_job(job_data)

    assert len(chunks) == 5

    for chunk in chunks:
        assert "chunk_type" in chunk
        assert "content" in chunk
        assert chunk["content"]
        assert isinstance(chunk["content"], str)


def test_chunk_job_handles_empty_fields():
    job_data = {
        "required_skills": [],
        "responsibilities": [],
        "technologies": [],
        "preferred_skills": [],
        "supporting_competencies": [],
    }

    chunks = TextChunker.chunk_job(job_data)

    assert chunks == []


def test_chunk_resume_handles_empty_fields():
    resume_data = {
        "summary": "",
        "skills": {},
        "experience": {},
        "education": {},
    }

    chunks = TextChunker.chunk_resume(resume_data)

    assert chunks == []