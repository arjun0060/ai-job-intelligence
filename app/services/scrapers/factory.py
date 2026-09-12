from app.services.scrapers.ashby_scraper import AshbyScraper
from app.services.scrapers.greenhouse_scraper import GreenhouseScraper
from app.services.scrapers.lever_scraper import LeverScraper
from app.services.scrapers.smartrecruiters_scraper import SmartRecruitersScraper
from app.services.scrapers.oracle_scraper import OracleCloudScraper
from app.services.scrapers.generic_scraper import GenericJobScraper


class JobScraperFactory:

    scrapers = [
        AshbyScraper(),
        GreenhouseScraper(),
        LeverScraper(),
        SmartRecruitersScraper(),
        OracleCloudScraper(),
    ]

    @classmethod
    def get_scraper(cls, url: str):

        for scraper in cls.scrapers:
            if scraper.can_handle(url):
                return scraper

        return GenericJobScraper()