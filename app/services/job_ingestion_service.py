from app.services.scrapers.factory import JobScraperFactory
from app.services.scrapers.generic_scraper import GenericJobScraper
from app.services.scrapers.playwright_scraper import PlaywrightScraper


class JobIngestionService:

    MIN_CONTENT_LENGTH = 300

    def __init__(self):

        self.generic_scraper = GenericJobScraper()
        self.playwright_scraper = PlaywrightScraper()

    def is_valid_content(self, result: dict) -> bool:

        content = result.get("content", "")

        if not content:
            return False

        if len(content.strip()) < self.MIN_CONTENT_LENGTH:
            return False

        # Common JS-rendering indicators
        invalid_phrases = [
            "enable javascript",
            "javascript is required",
            "please enable javascript"
        ]

        content_lower = content.lower()

        if any(
            phrase in content_lower
            for phrase in invalid_phrases
        ):
            return False

        return True

    def ingest(self, url: str):

        primary_scraper = (
            JobScraperFactory.get_scraper(url)
        )

        # 1. Try platform-specific scraper
        try:

            result = primary_scraper.scrape(url)

            if self.is_valid_content(result):
                return result

        except Exception as e:

            print(
                f"Primary scraper failed: {e}"
            )

        # 2. Try generic scraper
        try:

            result = self.generic_scraper.scrape(url)

            if self.is_valid_content(result):
                return result

        except Exception as e:

            print(
                f"Generic scraper failed: {e}"
            )

        # 3. Final fallback: browser rendering
        try:

            result = self.playwright_scraper.scrape(url)

            if self.is_valid_content(result):
                return result

        except Exception as e:

            print(
                f"Playwright scraper failed: {e}"
            )

        raise ValueError(
            "Unable to extract meaningful job content"
        )