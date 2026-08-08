from playwright.sync_api import sync_playwright

from .base import BaseCollector


class AMSCollector(BaseCollector):
    """Collect jobs from the AMS job search for Graz and a 5 km radius."""

    BASE_URL = "https://jobs.ams.at/public/emps/jobs"

    def collect(self, max_pages: int = 5) -> list[dict]:
        jobs = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            for page_number in range(1, max_pages + 1):
                url = (
                    f"{self.BASE_URL}"
                    "?sortOrder=desc"
                    "&location=Graz"
                    "&locationId=MUNICIPALITY_60101"
                    "&vicinity=5"
                    f"&page={page_number}"
                    "&pageSize=100"
                    "&JOB_OFFER_TYPE=SB_WKO"
                    "&JOB_OFFER_TYPE=IJ"
                    "&JOB_OFFER_TYPE=BA"
                    "&JOB_OFFER_TYPE=BZ"
                    "&JOB_OFFER_TYPE=TN"
                    "&sortField=PERIOD"
                )

                with page.expect_response(
                    lambda response: "/api/search" in response.url,
                    timeout=60000,
                ) as response_info:
                    page.goto(
                        url,
                        wait_until="networkidle",
                        timeout=60000,
                    )

                response = response_info.value
                data = response.json()

                results = data.get("results", [])

                if results:
                    print("\n=== AMS FIRST JOB KEYS ===")
                    print(results[0].keys())

                    print("\n=== AMS DATE-RELATED FIELDS ===")
                    for key, value in results[0].items():
                        if any(
                            word in key.lower()
                            for word in ["date", "time", "update", "publish", "create"]
                        ):
                            print(key, "=", value)

                for job in results:
                    working_location = job.get("workingLocation") or {}
                    coordinates = working_location.get("coordinates") or []

                    latitude = None
                    longitude = None

                    if coordinates:
                        latitude = coordinates[0].get("latitude")
                        longitude = coordinates[0].get("longitude")

                    jobs.append(
                        {
                            "title": job.get("title"),
                            "company": (job.get("company") or {}).get("name"),
                            "location": working_location.get("municipality"),
                            "latitude": latitude,
                            "longitude": longitude,
                            "distance_km": None,
                            "salary": None,
                            "url": job.get("urlToJobOffer"),
                            "description": job.get("summary"),
                            "source": "ams",
                            "source_job_id": str(job.get("id")),
                            "published_at": None,
                            "updated_at": job.get("lastUpdatedAt"),
                        }
                    )

                if not results:
                    break

            browser.close()

        return jobs