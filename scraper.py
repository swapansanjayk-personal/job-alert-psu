import requests
import logging
import concurrent.futures
import time
import random
from datetime import datetime
from bs4 import BeautifulSoup
from seed_data import SEED_JOBS
from filter import filter_jobs
from psu_data import ALL_PSUS

logger = logging.getLogger(__name__)

SCRAPE_TIMEOUT = 15
MAX_WORKERS = 3
RETRY_DELAY = 2

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

try:
    import cloudscraper
    CLOUDSCRAPER = cloudscraper.create_scraper()
    logger.info("cloudscraper available for Cloudflare bypass")
except ImportError:
    CLOUDSCRAPER = None
    logger.info("cloudscraper not installed, will only use requests")

JOB_KEYWORDS = [
    "engineer", "trainee", "recruit", "career", "notification",
    "vacancy", "job", "advertisement", "graduate", "executive",
    "scientist", "apprentice", "intern", "officer", "technician",
    "it", "computer", "software", "programmer",
    "cse", "information", "technology"
]


def _fetch(url):
    session = requests.Session()
    session.headers.update({"User-Agent": random.choice(USER_AGENTS)})
    session.headers.update({
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    })
    return session.get(url, timeout=SCRAPE_TIMEOUT)


def safe_scrape(url):
    if not url:
        return None

    # Method 1: Try requests
    for attempt in range(2):
        try:
            resp = _fetch(url)
            if resp.status_code == 200 and len(resp.text) > 200:
                return BeautifulSoup(resp.text, "html.parser")
            if resp.status_code in (403, 503):
                logger.debug(f"Blocked ({resp.status_code}) on attempt {attempt+1} for {url}")
                if attempt == 0:
                    time.sleep(RETRY_DELAY)
                    continue
            else:
                resp.raise_for_status()
        except requests.Timeout:
            logger.debug(f"Timeout on attempt {attempt+1} for {url}")
            time.sleep(RETRY_DELAY)
        except Exception as e:
            logger.debug(f"Failed on attempt {attempt+1} for {url}: {e}")
            time.sleep(RETRY_DELAY)

    # Method 2: Try cloudscraper if available (bypasses Cloudflare)
    if CLOUDSCRAPER:
        try:
            logger.debug(f"Trying cloudscraper for {url}")
            resp = CLOUDSCRAPER.get(url, timeout=SCRAPE_TIMEOUT)
            if resp.status_code == 200 and len(resp.text) > 200:
                logger.info(f"cloudscraper succeeded for {url}")
                return BeautifulSoup(resp.text, "html.parser")
        except Exception as e:
            logger.debug(f"cloudscraper failed for {url}: {e}")

    return None


def extract_jobs_from_soup(soup, psu_info):
    jobs = []
    if not soup:
        return jobs
    seen_links = set()
    for tag in soup.find_all(["a", "h1", "h2", "h3", "h4", "div", "span", "li"]):
        text = tag.get_text(strip=True)
        lower_text = text.lower()
        if not any(kw in lower_text for kw in JOB_KEYWORDS):
            continue
        if len(text) < 5:
            continue
        link_tag = tag if tag.name == "a" else tag.find("a")
        href = ""
        if link_tag and link_tag.name == "a" and link_tag.get("href"):
            href = link_tag["href"]
            if href.startswith("/"):
                base = psu_info.get("url", "")
                base_domain = "/".join(base.split("/")[:3])
                href = base_domain + href
            elif not href.startswith("http"):
                base = psu_info.get("url", "")
                base_dir = base.rstrip("/")
                href = base_dir + "/" + href
        link_key = href or text
        if link_key in seen_links:
            continue
        seen_links.add(link_key)
        if len(text) > 10:
            jobs.append({
                "title": text,
                "url": href,
                "text_snippet": text[:200]
            })
    return jobs


def build_job_entry(item, psu_info):
    short_name = psu_info.get("short", "").lower().split()[0] if psu_info.get("short") else "psu"
    now = datetime.now()
    ts = now.strftime("%Y%m%d_%H%M%S")
    job_id = f"{short_name}_scrape_{ts}_{abs(hash(item['title'])) % 10000}"
    org_full = psu_info.get("name", "PSU")
    desc = f"{org_full} career opportunity: {item['title']}"
    if item.get("text_snippet"):
        desc = item["text_snippet"]
    return {
        "job_id": job_id,
        "title": item["title"],
        "organization": org_full,
        "location": "India",
        "eligibility": "B.E/B.Tech CSE/IT",
        "selection_process": "Own Exam + Interview",
        "posted_date": now.strftime("%Y-%m-%d"),
        "deadline": "",
        "apply_url": item.get("url", psu_info.get("url", "")),
        "description": desc,
        "is_non_gate": True,
        "tags": ["PSU", org_full.split("(")[0].strip()],
        "batch_years": ["2023", "2024", "2025", "2026"],
        "source": "scrape"
    }


def scrape_psu(psu_info):
    url = psu_info.get("url", "")
    name = psu_info.get("name", "Unknown")
    if not url:
        return []
    soup = safe_scrape(url)
    if not soup:
        return []
    raw_items = extract_jobs_from_soup(soup, psu_info)
    jobs = []
    for item in raw_items[:8]:
        jobs.append(build_job_entry(item, psu_info))
    logger.debug(f"Scraped {len(jobs)} items from {name}")
    return jobs


def run_scrapers():
    all_jobs = []
    psu_list = [p for p in ALL_PSUS if p.get("url")]
    logger.info(f"Starting scrape of {len(psu_list)} PSUs with {MAX_WORKERS} workers...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_psu = {executor.submit(scrape_psu, psu): psu for psu in psu_list}
        for future in concurrent.futures.as_completed(future_to_psu):
            psu = future_to_psu[future]
            try:
                jobs = future.result()
                if jobs:
                    all_jobs.extend(jobs)
                    logger.info(f"Scraped {len(jobs)} items from {psu['name']}")
            except Exception as e:
                logger.warning(f"Error scraping {psu['name']}: {e}")
    logger.info(f"Total scraped items before filter: {len(all_jobs)}")
    return all_jobs


def run_scan():
    scraped = run_scrapers()
    filtered_scraped = filter_jobs(scraped)
    logger.info(f"Filtered scraped jobs: {len(filtered_scraped)}")
    all_filtered = list(filtered_scraped)
    seed_jobs_with_source = []
    for job in SEED_JOBS:
        j = dict(job)
        j["source"] = "seed"
        seed_jobs_with_source.append(j)
    filtered_seed = filter_jobs(seed_jobs_with_source)
    logger.info(f"Filtered seed jobs: {len(filtered_seed)}")
    existing_ids = {j.get("job_id") for j in all_filtered}
    for job in filtered_seed:
        if job["job_id"] not in existing_ids:
            all_filtered.append(job)
    logger.info(f"Total jobs after merge: {len(all_filtered)}")
    return all_filtered
