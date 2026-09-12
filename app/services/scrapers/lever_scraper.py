import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from app.services.scrapers.base import BaseJobScraper
from app.utils.text_cleaner import clean_html


class LeverScraper(BaseJobScraper):

    API_BASE_URL = "https://api.lever.co/v0/postings"

    def can_handle(self, url: str) -> bool:
        return "jobs.lever.co" in url

    def scrape(self, url: str) -> dict:

        parsed_url = urlparse(url)

        parts = [
            part for part in parsed_url.path.split("/")
            if part
        ]

        # Example:
        # /company/posting-id
        if len(parts) < 2:
            raise ValueError("Invalid Lever job URL")

        company = parts[0]
        posting_id = parts[1]

        api_url = (
            f"{self.API_BASE_URL}/"
            f"{company}/"
            f"{posting_id}"
        )

        response = requests.get(
            api_url,
            headers={
                "Accept": "application/json"
            },
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        description_html = data.get(
            "descriptionPlain"
        ) or data.get(
            "description"
        ) or ""

        description = clean_html(description_html)


        categories = data.get(
            "categories",
            {}
        )

        return {
            "url": url,
            "title": data.get("text"),
            "description": description,
            "location": categories.get("location"),
            "department": categories.get("team"),
            "employment_type": categories.get("commitment"),
            "source_type": "lever"
        }