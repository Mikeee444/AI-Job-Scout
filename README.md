# AI Job Scout

AI Job Scout is an AI-powered job search assistant that collects job postings,
stores them in a local database, and evaluates how well each position matches
the user's skills and experience.

## Features

- Collect job postings from multiple sources
- Normalize job data into a common format
- Store jobs in SQLite
- Detect duplicate job postings
- Analyze job descriptions with AI
- Calculate a job-to-CV match score
- Explain why a job is a good or bad match
- Identify missing or desirable skills
- Filter and rank jobs through a web dashboard

## Project Architecture

```text
Job Sources
     │
     ▼
Collectors
     │
     ▼
Normalized Job Data
     │
     ▼
Database
     │
     ▼
AI Job Matching
     │
     ▼
Dashboard