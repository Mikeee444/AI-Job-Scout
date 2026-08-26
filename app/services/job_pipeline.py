from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.collectors.ams import AMSCollector
from app.database.job_service import save_job
from app.database.models import Job
from app.services.scoring_pipeline import score_all_jobs


def collect_and_save_ams_jobs(
    db: Session,
) -> int:
    """Collect AMS jobs for a selected period and keep only that period."""

    periods = {
        "1": 1,
        "7": 7,
        "15": 15,
        "30": 30,
    }

    print()
    print("Select AMS collection period:")
    print("1 = Last 1 day")
    print("7 = Last 7 days")
    print("15 = Last 15 days")
    print("30 = Last 30 days")

    while True:
        choice = input(
            "Enter choice (1/7/15/30): "
        ).strip()

        if choice in periods:
            days_back = periods[choice]
            break

        print(
            "Invalid choice. "
            "Please enter 1, 7, 15, or 30."
        )

    cutoff = (
        datetime.now(timezone.utc)
        - timedelta(days=days_back)
    )

    print()
    print(
        f"Collecting AMS jobs from the last "
        f"{days_back} day(s)..."
    )
    print()

    collector = AMSCollector()

    jobs = collector.collect(
        days_back=days_back
    )

    saved = 0

    for job_data in jobs:

        # AMS jobs without a URL cannot be stored
        # because the database requires a URL.
        if not job_data.get("url"):
            continue

        save_job(db, job_data)
        saved += 1

    # -----------------------------------------------------
    # Remove AMS jobs outside the selected period
    # -----------------------------------------------------

    old_ams_jobs = (
        db.query(Job)
        .filter(Job.source == "ams")
        .all()
    )

    deleted = 0

    for job in old_ams_jobs:

        # Records without a publication date cannot be
        # reliably placed inside the selected period.
        if job.published_at is None:
            db.delete(job)
            deleted += 1
            continue

        published_at = job.published_at

        # SQLite may return a naive datetime.
        if published_at.tzinfo is None:
            published_at = published_at.replace(
                tzinfo=timezone.utc
            )

        if published_at < cutoff:
            db.delete(job)
            deleted += 1

    db.commit()

    # Recalculate scores after the database has been cleaned.
    score_all_jobs(db)

    print()
    print(f"Jobs collected: {len(jobs)}")
    print(f"Jobs saved/updated: {saved}")
    print(f"Old AMS jobs removed: {deleted}")
    print()

    return saved