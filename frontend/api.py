import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

DEFAULT_BACKEND_URL = "https://ai-lead-management.onrender.com"
LOCAL_BACKEND_URLS = ["http://localhost:8000", "http://127.0.0.1:8000"]


def get_backend_urls() -> list[str]:
    try:
        secret_url = st.secrets.get("BACKEND_URL")
    except Exception:
        secret_url = None

    configured_url = (secret_url or os.getenv("BACKEND_URL") or "").strip().rstrip("/")
    candidates = []

    if DEFAULT_BACKEND_URL not in candidates:
        candidates.append(DEFAULT_BACKEND_URL)

    if configured_url and configured_url not in candidates:
        candidates.append(configured_url)

    # Add common localhost values as fallback candidates only when they are not already configured.
    for local_url in LOCAL_BACKEND_URLS:
        if local_url not in candidates:
            candidates.append(local_url)

    return [url for url in candidates if url]


def _request_backend(method: str, path: str, **kwargs):
    last_error = None
    for base_url in get_backend_urls():
        try:
            response = requests.request(method, f"{base_url}{path}", timeout=15, **kwargs)
            if response.status_code < 500:
                return response
            last_error = RuntimeError(f"{response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            last_error = e

    if last_error is None:
        raise requests.exceptions.RequestException("Unable to reach the backend")
    raise last_error


def submit_lead(lead_data: dict):
    """Sends a new lead to the backend. Returns (success, data_or_error)."""
    try:
        response = _request_backend("post", "/leads", json=lead_data)
        if response.status_code == 200:
            return True, response.json()
        return False, response.text
    except requests.exceptions.RequestException as e:
        return False, str(e)


def get_all_leads():
    """Fetches all leads for the dashboard."""
    try:
        response = _request_backend("get", "/leads")
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.RequestException:
        return []


def get_dashboard_stats():
    """Fetches the 4 dashboard card counts."""
    try:
        response = _request_backend("get", "/leads/stats")
        if response.status_code == 200:
            return response.json()
        return {"total_leads": 0, "new_leads": 0, "qualified_leads": 0, "lost_leads": 0}
    except requests.exceptions.RequestException:
        return {"total_leads": 0, "new_leads": 0, "qualified_leads": 0, "lost_leads": 0}


def get_lead_by_id(lead_id: int):
    """Fetches a single lead's full detail."""
    try:
        response = _request_backend("get", f"/leads/{lead_id}")
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None


def update_lead(lead_id: int, update_data: dict):
    """Updates status/notes/owner/follow_up_date for a lead."""
    try:
        response = _request_backend("put", f"/leads/{lead_id}", json=update_data)
        if response.status_code == 200:
            return True, response.json()
        return False, response.text
    except requests.exceptions.RequestException as e:
        return False, str(e)
