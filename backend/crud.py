from sqlalchemy.orm import Session
from models import Lead
from schemas import LeadCreate, LeadUpdate


def create_lead(db: Session, lead_data: LeadCreate) -> Lead:
    """Insert a new lead into the database."""
    new_lead = Lead(
        name=lead_data.name,
        email=lead_data.email,
        phone=lead_data.phone,
        company=lead_data.company,
        industry=lead_data.industry,
        company_size=lead_data.company_size,
        budget=lead_data.budget,
        description=lead_data.description,
        status="New",
    )
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)
    return new_lead


def get_all_leads(db: Session):
    """Fetch every lead, most recent first."""
    return db.query(Lead).order_by(Lead.created_at.desc()).all()


def get_lead_by_id(db: Session, lead_id: int):
    """Fetch a single lead by its ID."""
    return db.query(Lead).filter(Lead.id == lead_id).first()


def update_lead_ai_result(db: Session, lead_id: int, score: int, temperature: str,
                           confidence: int, reasoning: str, next_action: str):
    """Save the AI qualification result onto a lead."""
    lead = get_lead_by_id(db, lead_id)
    if not lead:
        return None
    lead.score = score
    lead.temperature = temperature
    lead.confidence = confidence
    lead.reasoning = reasoning
    lead.next_action = next_action

    # Auto-mark as Qualified if AI thinks it's a strong lead
    if temperature == "Hot":
        lead.status = "Qualified"

    db.commit()
    db.refresh(lead)
    return lead


def update_lead_crm_fields(db: Session, lead_id: int, update_data: LeadUpdate):
    """Update CRM-managed fields: status, notes, owner, follow_up_date."""
    lead = get_lead_by_id(db, lead_id)
    if not lead:
        return None

    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(lead, field, value)

    db.commit()
    db.refresh(lead)
    return lead


def mark_email_sent(db: Session, lead_id: int):
    """Mark that the acknowledgement email was sent for this lead."""
    lead = get_lead_by_id(db, lead_id)
    if lead:
        lead.email_sent = "Yes"
        db.commit()
        db.refresh(lead)
    return lead
