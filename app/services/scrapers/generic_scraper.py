import requests
from bs4 import BeautifulSoup

from app.services.scrapers.base import BaseJobScraper
from app.utils.text_cleaner import clean_html


class GenericJobScraper(BaseJobScraper):

    def can_handle(self, url: str) -> bool:
        # Generic scraper acts as fallback
        return True

    def scrape(self, url: str) -> dict:

        headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/120 Safari/537.36"
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

        # Remove irrelevant elements
        for element in soup(
            [
                "script",
                "style",
                "nav",
                "footer",
                "header",
                "noscript"
            ]
        ):
            element.decompose()

        # Try semantic containers first
        main_content = (
            soup.find("main")
            or soup.find("article")
            or soup.find(
                attrs={"role": "main"}
            )
        )

        if main_content:
            # Pass HTML to centralized cleaner
            description = clean_html(
                str(main_content)
            )
        else:
            # Clean entire page HTML
            description = clean_html(
                str(soup)
            )

        title = None

        if soup.title:
            title = soup.title.get_text(
                strip=True
            )

        return {
            "url": url,
            "title": title,
            "company": None,
            "description": description,
            "location": None,
            "department": None,
            "employment_type": None,
            "source_type": "generic",
            "raw_data": None
        }