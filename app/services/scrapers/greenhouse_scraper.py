import requests
from urllib.parse import urlparse

from app.services.scrapers.base import BaseJobScraper
from app.utils.text_cleaner import clean_html


class GreenhouseScraper(BaseJobScraper):

    API_BASE_URL = "https://boards-api.greenhouse.io/v1/boards"

    def can_handle(self, url: str) -> bool:
        return "greenhouse.io" in url

    def scrape(self, url: str) -> dict:

        parsed_url = urlparse(url)

        path_parts = [
            part for part in parsed_url.path.split("/")
            if part
        ]

        if "jobs" not in path_parts:
            raise ValueError("Invalid Greenhouse job URL")

        jobs_index = path_parts.index("jobs")

        if jobs_index == 0:
            raise ValueError("Invalid Greenhouse job URL")

        board_token = path_parts[jobs_index - 1]

        if jobs_index + 1 >= len(path_parts):
            raise ValueError("Job ID not found")

        job_id = path_parts[jobs_index + 1]

        api_url = (
            f"{self.API_BASE_URL}/"
            f"{board_token}/jobs/{job_id}"
        )

        response = requests.get(
            api_url,
            timeout=15
        )

        response.raise_for_status()

        job = response.json()

        description_html = job.get("content")

        # Convert HTML → clean text
        description = clean_html(description_html)


        return {
            "url": url,
            "title": job.get("title"),
            "company": None,
            "location": job.get(
                "location",
                {}
            ).get("name"),
            "department": None,
            "employment_type": None,

            # IMPORTANT: return cleaned text, not HTML
            "description": description,

            "source_type": "greenhouse",
            "raw_data": None
        }