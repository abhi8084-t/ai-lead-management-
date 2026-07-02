from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime


# ---------- INPUT: what the lead form sends to the backend ----------
class LeadCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    phone: str = Field(..., min_length=7)
    company: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    budget: Optional[float] = None
    description: str = Field(..., min_length=1)


# ---------- INPUT: what the CRM sends when updating a lead ----------
class LeadUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    owner: Optional[str] = None
    follow_up_date: Optional[date] = None


# ---------- OUTPUT: what the backend sends back for a lead ----------
class LeadResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    company: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    budget: Optional[float] = None
    description: str

    score: Optional[int] = None
    temperature: Optional[str] = None
    confidence: Optional[int] = None
    reasoning: Optional[str] = None
    next_action: Optional[str] = None

    status: str
    notes: Optional[str] = None
    owner: Optional[str] = None
    follow_up_date: Optional[date] = None

    email_sent: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # allows creating this from an SQLAlchemy object


# ---------- OUTPUT: dashboard stats ----------
class DashboardStats(BaseModel):
    total_leads: int
    new_leads: int
    qualified_leads: int
    lost_leads: int
