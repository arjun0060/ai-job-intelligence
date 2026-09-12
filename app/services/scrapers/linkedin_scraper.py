import requests
from bs4 import BeautifulSoup

from app.services.scrapers.base import BaseJobScraper
from app.utils.text_cleaner import clean_html


class LinkedInScraper(BaseJobScraper):

    def can_handle(self, url: str) -> bool:
        return "linkedin.com/jobs" in url

    def scrape(self, url: str) -> dict:

        headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # -------------------------------
        # JOB TITLE
        # -------------------------------

        title_element = soup.select_one(
            "h1.top-card-layout__title"
        )

        title = (
            title_element.get_text(
                strip=True
            )
            if title_element
            else None
        )

        # -------------------------------
        # COMPANY
        # -------------------------------

        company_element = soup.select_one(
            "a.topcard__org-name-link"
        )

        company = (
            company_element.get_text(
                strip=True
            )
            if company_element
            else None
        )

        # -------------------------------
        # LOCATION
        # -------------------------------

        location_element = soup.select_one(
            "span.topcard__flavor--bullet"
        )

        location = (
            location_element.get_text(
                strip=True
            )
            if location_element
            else None
        )

        # -------------------------------
        # JOB DESCRIPTION
        # -------------------------------

        description_element = soup.select_one(
            ".show-more-less-html__markup"
        )

        if not description_element:

            description_element = soup.select_one(
                ".description__text"
            )

        if not description_element:
            raise ValueError(
                "Could not locate LinkedIn job description"
            )

        description = clean_html(
            str(description_element)
        )

        if (
            not description
            or len(description) < 100
        ):
            raise ValueError(
                "LinkedIn job description is empty"
            )

        return {
            "url": url,
            "title": title,
            "company": company,
            "location": location,
            "department": None,
            "employment_type": None,
            "description": description,
            "source_type": "linkedin",
            "posted_at": None,
            "raw_data": None
        }