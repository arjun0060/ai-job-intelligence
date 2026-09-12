from sqlalchemy.orm import Session
from app.services.job_repository import (
    JobRepository
)

from app.services.scrapers.ashby_scraper import (
    AshbyScraper
)
from app.services.scrapers.greenhouse_scraper import (
    GreenhouseScraper
)
from app.services.scrapers.lever_scraper import (
    LeverScraper
)
from app.services.scrapers.oracle_scraper import (
    OracleScraper
)
from app.services.scrapers.smartrecruiters_scraper import (
    SmartRecruitersScraper
)
from app.services.scrapers.generic_scraper import (
    GenericJobScraper
)
from app.services.scrapers.playwright_scraper import (
    PlaywrightJobScraper
)
from app.services.scrapers.linkedin_scraper import (
    LinkedInScraper
)

class JobService:

    specific_scrapers = [
        AshbyScraper(),
        GreenhouseScraper(),
        LeverScraper(),
        OracleScraper(),
        SmartRecruitersScraper(),
        LinkedInScraper()
    ]

    generic_scraper = GenericJobScraper()

    playwright_scraper = PlaywrightJobScraper()


    @classmethod
    def extract_job(cls, url: str):

        errors = []

        # STEP 1: Try platform-specific scraper
        for scraper in cls.specific_scrapers:

            if scraper.can_handle(url):

                try:

                    job_data = scraper.scrape(url)

                    if job_data.get("description"):
                        return job_data

                except Exception as e:

                    errors.append(
                        f"{scraper.__class__.__name__}: {str(e)}"
                    )

        # STEP 2: Try generic requests scraper
        try:

            job_data = cls.generic_scraper.scrape(url)

            if (
                job_data.get("description")
                and len(job_data["description"]) > 100
            ):
                return job_data

        except Exception as e:

            errors.append(
                f"GenericJobScraper: {str(e)}"
            )

        # STEP 3: Playwright fallback
        try:

            job_data = cls.playwright_scraper.scrape(url)

            if (
                job_data.get("description")
                and len(job_data["description"]) > 100
            ):
                return job_data

        except Exception as e:

            errors.append(
                f"PlaywrightJobScraper: {str(e)}"
            )

        raise ValueError(
            "Could not extract job description. "
            f"Errors: {' | '.join(errors)}"
        )
    

    @classmethod
    def extract_and_save(
        cls,
        url: str,
        db: Session
    ):

        # Reuse existing extraction logic
        job_data = cls.extract_job(url)

        print("\nDESCRIPTION BEFORE SAVING:")
        print(job_data.get("description"))
        print("\nDESCRIPTION LENGTH:")
        print(len(job_data.get("description", "")))

        # Check if URL already exists
        existing_job = JobRepository.get_by_url(
            db=db,
            url=url
        )

        if existing_job:
            return existing_job

        # Save new job
        job = JobRepository.create(
            db=db,
            job_data=job_data
        )

        return job