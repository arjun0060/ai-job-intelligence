from sqlalchemy.orm import Session

from app.models.job import Job


class JobRepository:

    @staticmethod
    def get_by_url(
        db: Session,
        url: str
    ):

        return (
            db.query(Job)
            .filter(Job.url == url)
            .first()
        )


    @staticmethod
    def create(
        db: Session,
        job_data: dict
    ):

        job = Job(
            title=job_data.get("title"),
            company=job_data.get("company"),
            location=job_data.get("location"),
            department=job_data.get("department"),
            employment_type=job_data.get(
                "employment_type"
            ),
            description=job_data.get("description"),
            url=job_data.get("url"),
            source_type=job_data.get(
                "source_type"
            )
        )

        db.add(job)

        db.commit()

        db.refresh(job)

        return job