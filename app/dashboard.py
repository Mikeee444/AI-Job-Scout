import streamlit as st
from datetime import datetime, timedelta, timezone

from app.database.database import SessionLocal
from app.database.models import Job
from app.services.job_scorer import (
    calculate_match_score,
    calculate_requirement_risk,
    classify_job,
)

st.set_page_config(
    page_title="AI Job Scout",
    layout="wide",
)

st.title("AI Job Scout")

db = SessionLocal()

jobs = (
    db.query(Job)
    .order_by(Job.score.desc())
    .all()
)

# Minimum score filter
min_score = st.slider(
    "Minimum score",
    min_value=0,
    max_value=100,
    value=0,
    step=5,
)

# Time filter
time_period = st.selectbox(
    "Time period",
    [
        "All",
        "Since yesterday",
        "Last 2 days",
        "Last 7 days",
        "Last 14 days",
        "Last 30 days",
    ],
)

# Category filter
categories = sorted(
    {
        classify_job(job)
        for job in jobs
    }
)

category = st.selectbox(
    "Category",
    ["ALL"] + categories,
)

# Apply minimum score
jobs = [
    job
    for job in jobs
    if (job.score or 0) >= min_score
]

# Apply time filter
if time_period != "All":
    days = {
        "Since yesterday": 1,
        "Last 2 days": 2,
        "Last 7 days": 7,
        "Last 14 days": 14,
        "Last 30 days": 30,
    }[time_period]

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    def is_recent(job):
        date = job.collected_at

        if date is None:
            return False

        if date.tzinfo is None:
            date = date.replace(tzinfo=timezone.utc)

        return date >= cutoff

    jobs = [job for job in jobs if is_recent(job)]

# Apply category filter
if category != "ALL":
    jobs = [
        job
        for job in jobs
        if classify_job(job) == category
    ]

st.write(f"**{len(jobs)} jobs match the filter**")

for job in jobs:
    match_score = calculate_match_score(job)
    risk = calculate_requirement_risk(job)
    job_category = classify_job(job)

    st.subheader(
        f"{job.score}/100 - {job.title}"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Match", f"{match_score}/100")

    with col2:
        st.metric("Requirement risk", risk)

    with col3:
        st.metric("Category", job_category)

    st.write(
        f"**{job.company}** - "
        f"{job.location or 'Unknown'}"
    )

    if job.url:
        st.link_button(
            "View job posting",
            job.url,
        )

db.close()