from datetime import datetime, timezone

from sqlalchemy.orm import Session

from .models import Job

def parse_datetime(value):
    """Convert an ISO timestamp string to a Python datetime."""
    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    return datetime.fromisoformat(value.replace("Z", "+00:00"))

def save_job(db: Session, job_data: dict) -> Job:
    """Insert a new job or update an existing job."""

    source = job_data.get("source")
    source_job_id = job_data.get("source_job_id")

    job = (
        db.query(Job)
        .filter(
            Job.source == source,
            Job.source_job_id == source_job_id,
        )
        .first()
    )

    if job is None:
        job = Job(
            source=source,
            source_job_id=source_job_id,
        )
        db.add(job)

    job.title = job_data["title"]
    job.company = job_data["company"]
    job.location = job_data.get("location")
    job.latitude = job_data.get("latitude")
    job.longitude = job_data.get("longitude")
    job.distance_km = job_data.get("distance_km")
    job.salary = job_data.get("salary")
    job.url = job_data["url"]
    job.description = job_data.get("description")
    job.published_at = parse_datetime(job_data.get("published_at"))
    job.updated_at = parse_datetime(job_data.get("updated_at"))
    job.collected_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(job)

    return job