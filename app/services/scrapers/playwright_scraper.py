from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from app.services.scrapers.base import BaseJobScraper
from app.utils.text_cleaner import clean_html


class PlaywrightJobScraper(BaseJobScraper):

    def can_handle(self, url: str) -> bool:
        return True

    def scrape(self, url: str) -> dict:

        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=True
            )

            try:

                page = browser.new_page(
                    viewport={
                        "width": 1920,
                        "height": 1080
                    },
                    user_agent=(
                        "Mozilla/5.0 "
                        "(Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 "
                        "(KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    )
                )

                page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=30000
                )

                # Allow JavaScript / SPA content to render
                page.wait_for_timeout(3000)

                html = page.content()

                title = page.title()

            finally:

                browser.close()

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        # Remove irrelevant page elements
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

        # Try extracting meaningful content first
        main_content = (
            soup.find("main")
            or soup.find("article")
            or soup.find(
                attrs={"role": "main"}
            )
        )

        if main_content:

            description = clean_html(
                str(main_content)
            )

        else:

            description = clean_html(
                str(soup)
            )

        # -------------------------------
        # VALIDATE EXTRACTED CONTENT
        # -------------------------------

        if (
            not description
            or len(description.strip()) < 100
        ):
            raise ValueError(
                "Could not extract meaningful content "
                "using Playwright"
            )

        # -------------------------------
        # DETECT BLOCKED / ERROR PAGES
        # -------------------------------

        blocked_indicators = [
            "access denied",
            "you don't have permission",
            "you do not have permission",
            "forbidden",
            "captcha",
            "verify you are human",
            "verify that you are human",
            "security check",
            "temporarily blocked",
            "request blocked",
            "errors.edgesuite.net",
            "unusual traffic",
            "automated requests",
            "bot detection"
        ]

        description_lower = description.lower()

        if any(
            indicator in description_lower
            for indicator in blocked_indicators
        ):
            raise ValueError(
                "Website blocked automated access"
            )

        # Also validate page title
        blocked_titles = [
            "access denied",
            "forbidden",
            "just a moment",
            "security check",
            "attention required"
        ]

        if (
            title
            and title.lower().strip()
            in blocked_titles
        ):
            raise ValueError(
                "Website blocked automated access"
            )

        return {
            "url": url,
            "title": title,
            "company": None,
            "description": description,
            "location": None,
            "department": None,
            "employment_type": None,
            "source_type": "playwright",
            "posted_at": None,
            "raw_data": None
        }