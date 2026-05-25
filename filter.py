import re
from psu_data import PSU_NAMES_FOR_FILTER

CSE_KEYWORDS = [
    "computer science", "information technology", "cse", "it",
    "software", "computer", "informatics", "computer engineering",
    "computer science & engineering", "cs/it", "it/cs",
    "information science", "computer science and engineering",
    "b.e. cse", "b.tech cse", "b.e. it", "b.tech it",
    "computer application", "bca", "mca",
]

ROLE_KEYWORDS = [
    "engineer trainee", "graduate engineer", "trainee engineer",
    "management trainee", "executive trainee",
    "scientist", "technical trainee",
    "junior engineer", "je", "graduate apprentice",
    "engineer trainee", "get", "graduate engineer trainee",
    "assistant engineer", "assistant officer",
    "software engineer", "software developer",
    "it officer", "it executive",
    "programmer", "system analyst",
    "technical assistant", "research trainee",
    "information technology trainee",
    "officer trainee", "project trainee",
    "intern", "apprentice",
]

GATE_EXCLUDE_PATTERNS = [
    r"gate\s+(score|qualified|required|mandatory|compulsory)",
    r"gate\s+20\d{2}",
    r"gate\s+based",
    r"gate\s+examination",
    r"valid\s+gate",
    r"gate\s+2025",
    r"gate\s+2026",
    r"through\s+gate",
    r"gate\s+gate",
]

BATCH_YEARS = ["2023", "2024", "2025", "2026", "2027"]
BATCH_KEYWORDS = [
    "2023", "2024", "2025", "2026", "2027",
    "fresher", "recent graduate", "recent pass",
    "passing year", "batch", "fresh graduate",
    "final year", "recently graduated",
]


def is_cse_role(job):
    text = " ".join([
        job.get("title", "").lower(),
        job.get("description", "").lower(),
        job.get("eligibility", "").lower(),
        ",".join(job.get("tags", [])).lower()
    ])
    return any(kw in text for kw in CSE_KEYWORDS)


def is_trainee_role(job):
    text = " ".join([
        job.get("title", "").lower(),
        job.get("description", "").lower()
    ])
    return any(kw in text for kw in ROLE_KEYWORDS)


def is_non_gate(job):
    text = " ".join([
        job.get("selection_process", "").lower(),
        job.get("description", "").lower(),
        job.get("title", "").lower()
    ])
    for pattern in GATE_EXCLUDE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return False
    if job.get("is_non_gate") is False:
        return False
    return True


def is_recent_batch(job):
    text = " ".join([
        job.get("description", "").lower(),
        job.get("eligibility", "").lower(),
        job.get("title", "").lower()
    ])
    batch_years = job.get("batch_years", [])
    if isinstance(batch_years, str):
        batch_years = batch_years.split(",")
    for year in BATCH_YEARS:
        if year in text or year in batch_years:
            return True
    return any(kw in text for kw in BATCH_KEYWORDS)


def is_psu(job):
    org = job.get("organization", "").lower()
    return any(psu in org for psu in PSU_NAMES_FOR_FILTER)


def filter_job(job):
    if not is_cse_role(job):
        return False
    if not is_trainee_role(job):
        return False
    if not is_non_gate(job):
        return False
    if not is_recent_batch(job):
        return False
    if not is_psu(job):
        return False
    return True


def filter_jobs(jobs):
    return [job for job in jobs if filter_job(job)]
