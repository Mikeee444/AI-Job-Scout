from sqlalchemy.orm import Session

from .models import Job


def save_job(db: Session, job_data: dict) -> Job:
    """Save a job to the database."""

    job = Job(
        title=job_data["title"],
        company=job_data["company"],
        location=job_data.get("location"),
        salary=job_data.get("salary"),
        url=job_data["url"],
        description=job_data.get("description"),
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job