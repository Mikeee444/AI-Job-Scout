import re

from app.config.profile import PROFILE
from app.database.models import Job


# =========================================================
# JOB CATEGORIES
# =========================================================

JOB_CATEGORIES = {
    "SOFTWARE": [
        "software developer",
        "softwareentwickler",
        "software engineer",
        "softwareentwicklung",
        "software development",
    ],

    "TESTING": [
        "test engineer",
        "testingenieur",
        "software tester",
        "testing",
        "verification",
        "quality engineer",
        "qa engineer",
        "test & verification",
    ],

    "EMBEDDED": [
        "embedded",
        "firmware",
        "microcontroller",
        "embedded software",
    ],

    "DATABASE": [
        "database developer",
        "database engineer",
        "sql developer",
        "database",
        "datenbank",
        "erp",
    ],

    "INDUSTRIAL_AUTOMATION": [
        "industrial security",
        "industrial automation",
        "automation",
        "automatisierung",
        "scada",
        "sps",
        "plc",
    ],

    "ELECTRICAL": [
        "elektrotechnik",
        "elektrotechniker",
        "elektriker",
        "elektrik",
        "elektro-installationstechniker",
        "schaltschrank",
        "msr",
        "gebäudesicherheit",
    ],

    "MECHATRONICS": [
        "mechatroniker",
        "mechatronik",
    ],

    "MAINTENANCE": [
        "instandhaltung",
        "wartung",
        "wartungstechniker",
    ],

    "FIELD_SERVICE": [
        "field service",
        "servicetechniker",
        "service-techniker",
        "kundendiensttechniker",
        "inbetriebnahmetechniker",
    ],

    "MECHANICAL": [
        "mechanik",
        "zerspanung",
        "fräser",
        "kfz",
        "montage",
    ],
}
CATEGORY_WEIGHTS = {
    "SOFTWARE": 1.15,
    "TESTING": 1.15,
    "EMBEDDED": 1.10,
    "DATABASE": 1.10,
    "SYSTEM_INTEGRATION": 1.10,
    "INDUSTRIAL_AUTOMATION": 1.05,
    "IT_SUPPORT": 1.00,
    "ELECTRICAL": 0.90,
    "MECHATRONICS": 0.85,
    "FIELD_SERVICE": 0.75,
    "MAINTENANCE": 0.65,
    "MECHANICAL": 0.55,
    "OTHER": 0.50,
}

# =========================================================
# PRIMARY ROLES
# =========================================================

# Strongest signals: these are the roles we actually want.
PRIMARY_ROLES = {
    "test engineer": 40,
    "testingenieur": 40,
    "test & verification": 40,
    "verification engineer": 40,
    "software developer": 38,
    "softwareentwickler": 38,
    "embedded systems": 40,
    "embedded software": 40,
    "firmware": 35,
    "software tester": 35,
    "qa engineer": 35,
    "quality engineer": 30,
    "system engineer": 32,
    "database developer": 30,
    "database engineer": 30,
}


# =========================================================
# SECONDARY ROLES
# =========================================================

# Good secondary matches.
SECONDARY_ROLES = {
    "requirements engineer": 25,
    "requirements engineering": 22,
    "system integration": 25,
    "systemintegration": 25,
    "technical support": 20,
    "application support": 20,
    "2nd-level support": 20,
    "automation": 20,
    "automatisierung": 20,
    "industrial security": 20,
    "scada": 15,
    "sps": 15,
    "plc": 15,
    "elektrotechnik": 15,
    "elektronik": 15,
    "mechatronik": 15,
}


# =========================================================
# IRRELEVANT ROLES
# =========================================================

# Roles that should never rank highly just because their
# descriptions happen to contain technical words.
IRRELEVANT_ROLES = {
    "reinigungskraft",
    "verkaufsmitarbeiter",
    "verkäufer",
    "einzelhandel",
    "sales manager",
    "sales",
    "vertrieb",
    "buchhaltung",
    "wirtschaftsprüfung",
    "steuerberater",
    "pflege",
    "spedition",
    "seefracht",
    "rezeption",
    "fräser",
    "zerspanung",
    "lüftungstechniker",
    "gebäudetechnik",
    "wäschereimitarbeiter",
    "kassierer",
    "kassier",
    "koch",
    "küche",
    "servicekraft",
    "zimmermädchen",
}


# =========================================================
# HIGH-VALUE SKILLS
# =========================================================

HIGH_VALUE_SKILLS = {
    "testing": 10,
    "software testing": 12,
    "system testing": 12,
    "integration testing": 12,
    "end-to-end testing": 12,
    "manual testing": 10,
    "test cases": 8,
    "quality assurance": 10,
    "istqb": 8,
    "verification": 10,
    "c#": 10,
    "java": 8,
    "c": 8,
    "embedded c": 10,
    "embedded systems": 10,
    "firmware": 10,
    "microcontrollers": 8,
    "sql": 8,
    "pl/sql": 8,
    "mysql": 6,
    "mariadb": 6,
    "database": 7,
    "datenbank": 7,
    "linux": 8,
    "centos": 6,
    "shell": 6,
    "bash": 6,
    "modbus": 6,
    "m-bus": 6,
    "knx": 6,
    "industrial automation": 8,
    "industrial security": 8,
    "ot": 6,
    "plc": 6,
    "sps": 6,
    "api": 6,
    "rest": 6,
    "system integration": 8,
}


# =========================================================
# EDUCATION
# =========================================================

EDUCATION = {
    "htl": 8,
    "informatik": 8,
    "informationstechnik": 8,
    "elektrotechnik": 8,
    "elektronik": 6,
    "wirtschaftsinformatik": 8,
    "systemintegration": 6,
}


# =========================================================
# EXPERIENCE RISK
# =========================================================

# Requirements that may indicate a gap between the job
# and the profile.
EXPERIENCE_RISK = {
    "mehrjährige berufserfahrung": 8,
    "mehrjährige erfahrung": 8,
    "fundierte kenntnisse": 5,
    "sehr gute kenntnisse": 5,
    "mehrjährige": 6,

    # Leadership/seniority is a weaker risk than a hard
    # experience requirement.
    "senior": 6,
    "lead": 8,
    "leiter": 10,
    "teamleiter": 10,
}


# =========================================================
# TEXT HELPERS
# =========================================================

def contains(text: str, keyword: str) -> bool:
    """Case-insensitive whole-word/phrase search."""

    return re.search(
        rf"\b{re.escape(keyword.lower())}\b",
        text.lower(),
    ) is not None

def matches_category_keyword(text: str, keyword: str) -> bool:
    """Match category keywords as whole words or word prefixes."""
    text = text.lower()
    keyword = keyword.lower()

    return re.search(
        rf"\b{re.escape(keyword)}",
        text,
    ) is not None


# =========================================================
# JOB CLASSIFICATION
# =========================================================

def classify_job(job: Job) -> str:
    """
    Classify a job based primarily on its title.

    The first matching category wins.
    """

    title = (job.title or "").lower()

    for category, keywords in JOB_CATEGORIES.items():
        for keyword in keywords:
            if matches_category_keyword(title, keyword):
                return category

    return "OTHER"


# =========================================================
# IRRELEVANCE
# =========================================================

def is_irrelevant(job: Job) -> bool:
    """Return True for clearly unrelated job categories."""

    title = (job.title or "").lower()

    for keyword in IRRELEVANT_ROLES:
        if contains(title, keyword):
            return True

    return False


# =========================================================
# MATCH SCORE
# =========================================================

def calculate_match_score(job: Job) -> int:
    """Calculate how strongly the job matches the user's profile."""

    title = (job.title or "").lower()
    description = (job.description or "").lower()

    score = 0

    # ---------------------------------------------------------
    # 1. Clearly irrelevant roles
    # ---------------------------------------------------------

    if is_irrelevant(job):
        return 0

    # ---------------------------------------------------------
    # 2. Preferred roles from profile
    # ---------------------------------------------------------

    preferred_roles = PROFILE["preferred_roles"]

    for role in preferred_roles:
        if contains(title, role):
            score += 15

    # ---------------------------------------------------------
    # 3. Strong role signals
    # ---------------------------------------------------------

    for keyword, points in PRIMARY_ROLES.items():
        if contains(title, keyword):
            score += points

    # ---------------------------------------------------------
    # 4. Secondary role signals
    # ---------------------------------------------------------

    for keyword, points in SECONDARY_ROLES.items():
        if contains(title, keyword):
            score += points

    # ---------------------------------------------------------
    # 5. High-value technical skills
    # ---------------------------------------------------------

    skill_points = 0

    for keyword, points in HIGH_VALUE_SKILLS.items():
        if contains(description, keyword):
            skill_points += points

    # Don't let many generic skills dominate the score.
    score += min(skill_points, 40)

    # ---------------------------------------------------------
    # 6. Education
    # ---------------------------------------------------------

    education_points = 0

    for keyword, points in EDUCATION.items():
        if contains(description, keyword):
            education_points += points

    score += min(education_points, 15)

    # ---------------------------------------------------------
    # 7. Location
    # ---------------------------------------------------------

    if job.location and "graz" in job.location.lower():
        score += 5

    return max(0, min(score, 100))


# =========================================================
# SKILL GAP RISK
# =========================================================

def calculate_skill_gap_risk(job: Job) -> int:
    """
    Estimate risk when a job explicitly requires substantial
    experience in a specific technology or domain.
    """

    description = (job.description or "").lower()

    risk = 0

    # Technologies/domains where professional experience
    # matters more than simply having basic knowledge.
    experience_requirements = {
        "t-sql": 5,
        "erp": 5,
        "oracle": 4,
        "database administration": 5,
        "datenbankadministration": 5,
        "c#": 3,
        "java": 3,
        "python": 3,
        "sps": 3,
        "scada": 3,
    }

    for keyword, points in experience_requirements.items():
        if contains(description, keyword):
            if (
                "erfahrung" in description
                or "kenntnisse" in description
                or "entwicklung" in description
                or "programmierung" in description
            ):
                risk += points

    return min(risk, 15)


# =========================================================
# REQUIREMENT RISK
# =========================================================

def calculate_requirement_risk(job: Job) -> int:
    """
    Estimate requirements that may be difficult to satisfy.

    This does not reject a job; it only reduces the score.
    """

    title = (job.title or "").lower()
    description = (job.description or "").lower()

    risk = 0

    # ---------------------------------------------------------
    # 1. General experience requirements
    # ---------------------------------------------------------

    for keyword, points in EXPERIENCE_RISK.items():
        if contains(description, keyword) or contains(title, keyword):
            risk += points

    # ---------------------------------------------------------
    # 2. Specific technology/domain experience gaps
    # ---------------------------------------------------------

    risk += calculate_skill_gap_risk(job)

    # ---------------------------------------------------------
    # 3. ERP/database experience
    # ---------------------------------------------------------

    if "erp" in description and "datenbank" in description:
        risk += 8

    # ---------------------------------------------------------
    # 4. Large travel requirements
    # ---------------------------------------------------------

    if "50%" in description and "reise" in description:
        risk += 5

    if "weltweit" in description and "reise" in description:
        risk += 3

    return min(risk, 30)


# =========================================================
# FINAL SCORE
# =========================================================

def calculate_score(job: Job) -> int:
    """
    Calculate final 0-100 job score.

    Final score = profile match - requirement risk.
    """

    match_score = calculate_match_score(job)
    requirement_risk = calculate_requirement_risk(job)

    # Clearly irrelevant jobs stay at zero.
    if is_irrelevant(job):
        return 0

    base_score = max(
    0,
    min(match_score - requirement_risk, 100),
    )

    category = classify_job(job)
    category_weight = CATEGORY_WEIGHTS.get(category, 0.50)

    weighted_score = round(base_score * category_weight)

    return max(0, min(weighted_score, 100)
    )