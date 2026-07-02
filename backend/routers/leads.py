from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas import LeadCreate, LeadUpdate, LeadResponse, DashboardStats
import crud
from services.ai_service import qualify_lead, personalize_email
from services.email_service import send_acknowledgement_email
from services.dashboard import get_dashboard_stats

router = APIRouter(prefix="/leads", tags=["Leads"])


def process_new_lead_background(lead_id: int, industry: str, company_size: str,
                                  budget: float, description: str,
                                  name: str, email: str, db: Session):
    """
    Runs AFTER the response is already sent to the user, so the form
    doesn't have to wait for AI + email to finish.
    Does: AI scoring -> save result -> send personalized email.
    """
    # 1. AI Qualification
    ai_result = qualify_lead(industry, company_size, budget, description)
    crud.update_lead_ai_result(
        db, lead_id,
        score=ai_result["score"],
        temperature=ai_result["temperature"],
        confidence=ai_result["confidence"],
        reasoning=ai_result["reasoning"],
        next_action=ai_result["next_action"],
    )

    # 2. AI-personalized email (bonus feature) + send
    personalized_body = personalize_email(name, industry, description)
    sent = send_acknowledgement_email(email, name, personalized_body)
    if sent:
        crud.mark_email_sent(db, lead_id)


@router.post("", response_model=LeadResponse)
def submit_lead(lead: LeadCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    STEP 1 & onwards combined:
    - Saves the new lead to the database
    - Triggers AI qualification + email sending in the background
    - Returns immediately so the user doesn't wait
    """
    new_lead = crud.create_lead(db, lead)

    background_tasks.add_task(
        process_new_lead_background,
        new_lead.id, lead.industry, lead.company_size, lead.budget,
        lead.description, lead.name, lead.email, db,
    )

    return new_lead


@router.get("", response_model=List[LeadResponse])
def list_leads(db: Session = Depends(get_db)):
    """Returns all leads - used by the CRM Dashboard."""
    return crud.get_all_leads(db)


@router.get("/stats", response_model=DashboardStats)
def dashboard_stats(db: Session = Depends(get_db)):
    """Returns the 4 dashboard card counts."""
    return get_dashboard_stats(db)


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    """Returns a single lead's full detail - used by the Lead Detail page."""
    lead = crud.get_lead_by_id(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.put("/{lead_id}", response_model=LeadResponse)
def update_lead(lead_id: int, update_data: LeadUpdate, db: Session = Depends(get_db)):
    """Updates status, notes, owner, or follow-up date for a lead."""
    lead = crud.update_lead_crm_fields(db, lead_id, update_data)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead
