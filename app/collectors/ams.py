from datetime import datetime, timedelta, timezone

from playwright.sync_api import sync_playwright

from .base import BaseCollector


class AMSCollector(BaseCollector):
    """Collect AMS jobs for Graz and a 5 km radius from the last 30 days."""

    BASE_URL = "https://jobs.ams.at/public/emps/jobs"

    def collect(self, max_pages: int = 400) -> list[dict]:
        jobs = []
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            stop_collecting = False

            for page_number in range(1, max_pages + 1):

                if stop_collecting:
                    break

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

                if not results:
                    break

                page_has_recent_jobs = False

                for job in results:

                    last_updated = job.get("lastUpdatedAt")

                    if not last_updated:
                        continue

                    try:
                        job_date = datetime.fromisoformat(
                            last_updated.replace("Z", "+00:00")
                        )
                    except ValueError:
                        continue

                    # AMS is sorted newest -> oldest.
                    # Once we reach jobs older than 30 days,
                    # we don't need to continue collecting.
                    if job_date < cutoff:
                        stop_collecting = True
                        continue

                    page_has_recent_jobs = True

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
                            "published_at": last_updated,
                            "updated_at": last_updated,
                        }
                    )

                print(
                    f"AMS page {page_number}: "
                    f"{len(results)} results, "
                    f"{len(jobs)} jobs collected"
                )

                if not page_has_recent_jobs:
                    break

            browser.close()

        print(f"AMS collection finished: {len(jobs)} jobs")

        return jobs