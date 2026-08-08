from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from .database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String)

    latitude = Column(Float)
    longitude = Column(Float)
    distance_km = Column(Float)

    salary = Column(String)

    url = Column(String, unique=True, nullable=False)

    description = Column(Text)

    source = Column(String)
    source_job_id = Column(String)

    published_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))

    collected_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    score = Column(Integer, default=0)