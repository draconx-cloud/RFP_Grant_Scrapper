# grants_fetcher.py

import json
import os
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Any
from Grant_Json_Cleanup import clean_grants_json

URL = "https://micro.grants.gov/rest/opportunities/search_export_Mark2"
OUT_DIR = "grants_exports"

PAYLOAD: dict[str, Any] = {
    "keyword": None,
    "cfda": None,
    "agencies": None,
    "sortBy": "openDate|desc",
    "rows": 5000,
    "eligibilities": None,
    "fundingCategories": None,
    "fundingInstruments": None,
    "dateRange": "",
    "oppStatuses": "forecasted|posted",
}

# 1) Start minimal; 2) if denied, add Origin/Referer as a fallback
HEADER_VARIANTS = [
    {  # minimal
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "python-requests/2.x (data-fetcher)",
    },
    {  # fallback with web headers if server complains
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://www.grants.gov",
        "Referer": "https://www.grants.gov/",
        "User-Agent": "python-requests/2.x (data-fetcher)",
    },
]

def make_session(max_retries: int = 5, backoff_factor: float = 1.0) -> requests.Session:
    status_forcelist = (429, 500, 502, 503, 504)
    retry = Retry(
        total=max_retries,
        read=max_retries,
        connect=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods={"POST"},
        raise_on_status=False,
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
    s = requests.Session()
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    return s

def post_with_fallbacks(url: str, json_payload: dict[str, Any], timeout: tuple[int, int] = (15, 500)) -> requests.Response:
    session = make_session()
    last_exc = None
    for hdrs in HEADER_VARIANTS:
        try:
            resp = session.post(url, json=json_payload, headers=hdrs, timeout=timeout)
            if resp.status_code in (401, 403, 415):
                last_exc = RuntimeError(f"HTTP {resp.status_code} with headers variant; trying next.")
                continue
            return resp
        except requests.RequestException as e:
            last_exc = e
            continue
    if last_exc:
        raise last_exc
    raise RuntimeError("Request failed for unknown reasons.")

def fetch_grants(payload: dict[str, Any] = PAYLOAD, timeout_read_seconds: int = 500) -> dict[str, Any]:
    resp = post_with_fallbacks(URL, payload, timeout=(15, timeout_read_seconds))
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        snippet = (resp.text or "")[:500]
        raise RuntimeError(f"HTTP {resp.status_code} error from server: {snippet}") from e
    try:
        return resp.json()
    except ValueError as e:
        raise RuntimeError("Response was not valid JSON.") from e

def save_json(data: dict[str, Any], out_dir: str = OUT_DIR) -> str:
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    json_path = os.path.join(out_dir, f"grants_{ts}.json")
    cleaned_json_path = os.path.join(out_dir, f"grants_{ts}_cleaned.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    clean_grants_json(input_json_path=json_path, output_json_path=cleaned_json_path)
    return cleaned_json_path

def fetch_and_save(payload: dict[str, Any] = PAYLOAD, timeout_read_seconds: int = 500) -> str:
    """Fetch grants and save both raw and cleaned JSON. Returns cleaned JSON path."""
    data = fetch_grants(payload, timeout_read_seconds)
    return save_json(data)

if __name__ == "__main__":
    try:
        out_path = fetch_and_save()
        print(f"Saved to {out_path}")
    except Exception as exc:
        print(f"Failed: {exc}")
