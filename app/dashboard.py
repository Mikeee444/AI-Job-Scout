import streamlit as st
from datetime import datetime, timedelta, timezone

from app.database.database import SessionLocal
from app.database.models import Job
from app.services.job_scorer import (
    calculate_match_score,
    calculate_requirement_risk,
    classify_job,
    explain_score,
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Job Scout",
    layout="wide",
)

st.title("AI Job Scout")


# =========================================================
# DATABASE
# =========================================================

db = SessionLocal()

try:
    # Always load jobs from highest score to lowest score.
    all_jobs = (
        db.query(Job)
        .order_by(Job.score.desc())
        .all()
    )

    # =====================================================
    # FILTERS
    # =====================================================

    # -----------------------------------------------------
    # Minimum score
    # -----------------------------------------------------

    min_score = st.slider(
        "Minimum score",
        min_value=0,
        max_value=100,
        value=0,
        step=5,
    )

    # -----------------------------------------------------
    # Time period
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Category
    # -----------------------------------------------------

    categories = sorted(
        {
            classify_job(job)
            for job in all_jobs
        }
    )

    category = st.selectbox(
        "Category",
        ["ALL"] + categories,
    )

    # -----------------------------------------------------
    # Search
    # -----------------------------------------------------

    search_text = st.text_input(
        "Search jobs",
        placeholder="Search by job title or company...",
    )

    # =====================================================
    # APPLY FILTERS
    # =====================================================

    jobs = all_jobs

    # -----------------------------------------------------
    # Minimum score
    # -----------------------------------------------------

    jobs = [
        job
        for job in jobs
        if (job.score or 0) >= min_score
    ]

    # -----------------------------------------------------
    # Time period
    # -----------------------------------------------------

    if time_period != "All":

        days = {
            "Since yesterday": 1,
            "Last 2 days": 2,
            "Last 7 days": 7,
            "Last 14 days": 14,
            "Last 30 days": 30,
        }[time_period]

        cutoff = (
            datetime.now(timezone.utc)
            - timedelta(days=days)
        )

        def is_recent(job):
            date = job.collected_at

            if date is None:
                return False

            if date.tzinfo is None:
                date = date.replace(
                    tzinfo=timezone.utc
                )

            return date >= cutoff

        jobs = [
            job
            for job in jobs
            if is_recent(job)
        ]

    # -----------------------------------------------------
    # Category
    # -----------------------------------------------------

    if category != "ALL":

        jobs = [
            job
            for job in jobs
            if classify_job(job) == category
        ]

    # -----------------------------------------------------
    # Search
    # -----------------------------------------------------

    if search_text.strip():

        search = search_text.strip().lower()

        jobs = [
            job
            for job in jobs
            if (
                search in (job.title or "").lower()
                or search in (job.company or "").lower()
            )
        ]

    # =====================================================
    # RESULT COUNT
    # =====================================================

    st.write(
        f"**{len(jobs)} jobs match the filter**"
    )

    # =====================================================
    # JOB RESULTS
    # =====================================================

    for job in jobs:

        # -------------------------------------------------
        # Calculate scores
        # -------------------------------------------------

        match_score = calculate_match_score(job)
        requirement_risk = calculate_requirement_risk(job)
        job_category = classify_job(job)
        score_explanation = explain_score(job)

        # -------------------------------------------------
        # Job title
        # -------------------------------------------------

        st.subheader(
            f"{job.score}/100 - {job.title}"
        )

        # -------------------------------------------------
        # Metrics
        # -------------------------------------------------

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Match",
                f"{match_score}/100",
            )

        with col2:
            st.metric(
                "Requirement risk",
                requirement_risk,
            )

        with col3:
            st.metric(
                "Category",
                job_category,
            )

        # -------------------------------------------------
        # Company / location
        # -------------------------------------------------

        st.write(
            f"**{job.company or 'Unknown'}**"
            f" - "
            f"{job.location or 'Unknown'}"
        )

        # -------------------------------------------------
        # Inserted / Updated date
        # -------------------------------------------------

        if job.published_at:

            published_at = job.published_at

            if published_at.tzinfo is None:
                published_at = published_at.replace(
                    tzinfo=timezone.utc
                )

            st.caption(
                "Inserted / Updated: "
                f"{published_at.strftime('%d.%m.%Y %H:%M')}"
            )

        # -------------------------------------------------
        # Score explanation
        # -------------------------------------------------

        with st.expander("Why this score?"):

            st.write(
                f"**Base score:** "
                f"{score_explanation['base_score']}/100"
            )

            st.write(
                f"**Category:** "
                f"{score_explanation['category']}"
            )

            st.write(
                f"**Category weight:** "
                f"{score_explanation['category_weight']:.2f}"
            )

            st.write(
                f"**Final score:** "
                f"**{score_explanation['final_score']}/100**"
            )

            # -------------------------------------------------
            # Positive signals
            # -------------------------------------------------

            if score_explanation["positive"]:

                st.markdown("### Positive signals")

                for reason, points in score_explanation["positive"]:

                    if points > 0:
                        st.write(
                            f"**+{points}** - {reason}"
                        )
                    else:
                        st.write(reason)

            # -------------------------------------------------
            # Risks / deductions
            # -------------------------------------------------

            if score_explanation["risks"]:

                st.markdown("### Risk / deductions")

                for reason, points in score_explanation["risks"]:

                    st.write(
                        f"**-{points}** - {reason}"
                    )

        # -------------------------------------------------
        # Job description
        # -------------------------------------------------

        if job.description:

            with st.expander("Job description"):

                st.write(job.description)

        # -------------------------------------------------
        # Job posting
        # -------------------------------------------------

        if job.url:

            st.link_button(
                "View job posting",
                job.url,
            )

finally:
    db.close()