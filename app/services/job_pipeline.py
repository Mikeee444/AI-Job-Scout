from sqlalchemy.orm import Session

from app.collectors.ams import AMSCollector
from app.database.job_service import save_job
from app.services.scoring_pipeline import score_all_jobs


def collect_and_save_ams_jobs(
    db: Session,
) -> int:
    """Collect AMS jobs from the last 30 days and save them."""

    collector = AMSCollector()
    jobs = collector.collect()

    saved = 0

    for job_data in jobs:
        if not job_data.get("url"):
            continue

        save_job(db, job_data)
        saved += 1

    score_all_jobs(db)

    return saved