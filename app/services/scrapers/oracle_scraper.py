from app.services.scrapers.base import BaseJobScraper
from app.services.scrapers.generic_scraper import GenericJobScraper


class OracleScraper(BaseJobScraper):

    def __init__(self):
        self.generic_scraper = GenericJobScraper()

    def can_handle(self, url: str) -> bool:

        oracle_patterns = [
            "oraclecloud.com",
            "oraclecloud.net",
            "fa.oraclecloud.com",
            "oracle.com"
        ]

        return any(
            pattern in url.lower()
            for pattern in oracle_patterns
        )

    def scrape(self, url: str) -> dict:

        """
        Oracle Recruiting implementations vary significantly
        across organizations.

        Attempt standard HTTP extraction first.
        """

        result = self.generic_scraper.scrape(url)

        result["source_type"] = "oracle"

        return result