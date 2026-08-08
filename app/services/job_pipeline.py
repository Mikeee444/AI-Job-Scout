from sqlalchemy.orm import Session

from app.collectors.ams import AMSCollector
from app.database.job_service import save_job


def collect_and_save_ams_jobs(
    db: Session,
    max_pages: int = 5,
) -> int:
    """Collect AMS jobs and save them to the database."""

    collector = AMSCollector()
    jobs = collector.collect(max_pages=max_pages)

    saved = 0

    for job_data in jobs:
        save_job(db, job_data)
        saved += 1

    return saved