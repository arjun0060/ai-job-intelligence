import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from app.services.scrapers.base import BaseJobScraper
from app.utils.text_cleaner import clean_html


class AshbyScraper(BaseJobScraper):

    API_BASE_URL = "https://api.ashbyhq.com/posting-api/job-board"

    def can_handle(self, url: str) -> bool:
        return "jobs.ashbyhq.com" in url

    def scrape(self, url: str) -> dict:

        parsed_url = urlparse(url)

        path_parts = [
            part for part in parsed_url.path.split("/")
            if part
        ]

        if len(path_parts) < 2:
            raise ValueError(
                "Invalid Ashby job URL"
            )

        job_board_name = path_parts[0]
        job_identifier = path_parts[1]

        api_url = (
            f"{self.API_BASE_URL}/"
            f"{job_board_name}"
        )

        response = requests.get(
            api_url,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        jobs = data.get("jobs", [])

        target_job = None

        for job in jobs:

            job_url = job.get("jobUrl", "")

            if job_identifier in job_url:
                target_job = job
                break

        if not target_job:
            raise ValueError(
                "Job posting not found on Ashby job board"
            )

        # Extract and clean job description
        description = target_job.get("descriptionPlain")

        if not description:
            description_html = target_job.get("descriptionHtml")

            if description_html:
                description = clean_html(description_html)  
                    

        return {
            "url": url,
            "title": target_job.get("title"),

            # Normalized field name
            "description": description,

            "location": target_job.get("location"),
            "department": target_job.get("department"),
            "employment_type": target_job.get("employmentType"),

            # Ashby board name as fallback company identifier
            "company": job_board_name.replace("-", " ").title(),

            "source_type": "ashby",

            # Useful while developing/debugging
            "raw_data": None
        }