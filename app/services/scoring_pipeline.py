from sqlalchemy.orm import Session

from app.database.models import Job
from app.services.job_scorer import calculate_score


def score_all_jobs(db: Session) -> int:
    """Calculate and save scores for all jobs."""

    jobs = db.query(Job).all()

    for job in jobs:
        job.score = calculate_score(job)

    db.commit()

    return len(jobs)