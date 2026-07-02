import os
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def submit_lead(lead_data: dict):
    """Sends a new lead to the backend. Returns (success, data_or_error)."""
    try:
        response = requests.post(f"{BACKEND_URL}/leads", json=lead_data, timeout=15)
        if response.status_code == 200:
            return True, response.json()
        return False, response.text
    except requests.exceptions.RequestException as e:
        return False, str(e)


def get_all_leads():
    """Fetches all leads for the dashboard."""
    try:
        response = requests.get(f"{BACKEND_URL}/leads", timeout=15)
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.RequestException:
        return []


def get_dashboard_stats():
    """Fetches the 4 dashboard card counts."""
    try:
        response = requests.get(f"{BACKEND_URL}/leads/stats", timeout=15)
        if response.status_code == 200:
            return response.json()
        return {"total_leads": 0, "new_leads": 0, "qualified_leads": 0, "lost_leads": 0}
    except requests.exceptions.RequestException:
        return {"total_leads": 0, "new_leads": 0, "qualified_leads": 0, "lost_leads": 0}


def get_lead_by_id(lead_id: int):
    """Fetches a single lead's full detail."""
    try:
        response = requests.get(f"{BACKEND_URL}/leads/{lead_id}", timeout=15)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None


def update_lead(lead_id: int, update_data: dict):
    """Updates status/notes/owner/follow_up_date for a lead."""
    try:
        response = requests.put(f"{BACKEND_URL}/leads/{lead_id}", json=update_data, timeout=15)
        if response.status_code == 200:
            return True, response.json()
        return False, response.text
    except requests.exceptions.RequestException as e:
        return False, str(e)
