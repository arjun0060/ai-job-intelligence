import requests
from urllib.parse import urlparse

from app.services.scrapers.base import BaseJobScraper
from app.utils.text_cleaner import clean_html


class SmartRecruitersScraper(BaseJobScraper):

    API_BASE_URL = "https://api.smartrecruiters.com/v1/companies"

    def can_handle(self, url: str) -> bool:
        return "smartrecruiters.com" in url

    def scrape(self, url: str) -> dict:

        parsed_url = urlparse(url)

        path_parts = [
            part
            for part in parsed_url.path.split("/")
            if part
        ]

        # Expected:
        # https://jobs.smartrecruiters.com/AccorHotel/744000147688089-revenue-manager

        if len(path_parts) < 2:
            raise ValueError(
                "Invalid SmartRecruiters job URL"
            )

        company_identifier = path_parts[0]
        posting_slug = path_parts[1]

        # -----------------------------------
        # STEP 1: GET COMPANY JOB LIST
        # -----------------------------------

        list_url = (
            f"{self.API_BASE_URL}/"
            f"{company_identifier}/"
            f"postings"
        )

        response = requests.get(
            list_url,
            params={
                "limit": 100
            },
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        jobs = data.get("content", [])

        if not jobs:
            raise ValueError(
                "No job postings found for company"
            )

        # -----------------------------------
        # STEP 2: FIND MATCHING JOB
        # -----------------------------------

        target_job = None

        for job in jobs:

            job_id = str(job.get("id", ""))
            job_uuid = str(job.get("uuid", ""))

            posting_url = (
                job.get("postingUrl")
                or job.get("applyUrl")
                or ""
            )

            # Match using ID, UUID, or URL
            if (
                job_id in posting_slug
                or job_uuid in posting_slug
                or posting_slug in posting_url
            ):
                target_job = job
                break

        if not target_job:
            raise ValueError(
                "Could not find matching job posting"
            )

        # -----------------------------------
        # STEP 3: GET FULL JOB DETAILS
        # -----------------------------------

        posting_id = (
            target_job.get("id")
            or target_job.get("uuid")
        )

        detail_url = (
            f"{self.API_BASE_URL}/"
            f"{company_identifier}/"
            f"postings/"
            f"{posting_id}"
        )

        print(
            "SmartRecruiters Detail URL:",
            detail_url
        )

        response = requests.get(
            detail_url,
            timeout=20
        )

        response.raise_for_status()

        job = response.json()

        # -----------------------------------
        # STEP 4: EXTRACT DESCRIPTION
        # -----------------------------------

        sections = (
            job.get("jobAd", {})
            .get("sections", {})
        )

        description_parts = []

        for section_key, section_value in sections.items():

            # Newer SmartRecruiters response format
            if isinstance(section_value, dict):

                title = section_value.get("title")
                text = section_value.get("text")

                if text:

                    cleaned_text = clean_html(text)

                    if cleaned_text:

                        if title:
                            description_parts.append(
                                f"{title}\n{cleaned_text}"
                            )
                        else:
                            description_parts.append(
                                cleaned_text
                            )

            # Older response format
            elif isinstance(section_value, str):

                cleaned_text = clean_html(
                    section_value
                )

                if cleaned_text:
                    description_parts.append(
                        cleaned_text
                    )

        description = "\n\n".join(
            description_parts
        )

        if not description:
            raise ValueError(
                "Could not extract job description"
            )

        # -----------------------------------
        # STEP 5: RETURN NORMALIZED DATA
        # -----------------------------------

        location = job.get("location", {})

        location_parts = [
            location.get("city"),
            location.get("region"),
            location.get("country")
        ]

        formatted_location = ", ".join(
            part
            for part in location_parts
            if part
        )

        department = job.get("department")

        if isinstance(department, dict):
            department = department.get("label")

        employment_type = job.get(
            "typeOfEmployment"
        )

        if isinstance(employment_type, dict):
            employment_type = employment_type.get(
                "label"
            )

        return {
            "url": url,
            "title": job.get("name"),

            "company": (
                job.get("company", {})
                .get("name")
                or company_identifier
            ),

            "location": (
                formatted_location
                if formatted_location
                else None
            ),

            "department": department,

            "employment_type": employment_type,

            "description": description,

            "source_type": "smartrecruiters",

            "posted_at": job.get(
                "releasedDate"
            ),

            "raw_data": None
        }