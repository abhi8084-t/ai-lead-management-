from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Date
from sqlalchemy.sql import func
from database import Base


class Lead(Base):
    """
    Represents a single lead captured from the website form.
    This maps directly to the 'leads' table in MySQL.
    """
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Fields from the lead capture form
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    company = Column(String(100), nullable=True)
    industry = Column(String(50), nullable=True)
    company_size = Column(String(20), nullable=True)
    budget = Column(Float, nullable=True)
    description = Column(Text, nullable=False)

    # AI qualification output
    score = Column(Integer, nullable=True)
    temperature = Column(String(10), nullable=True)   # Hot / Warm / Cold
    confidence = Column(Integer, nullable=True)        # 0-100
    reasoning = Column(Text, nullable=True)
    next_action = Column(Text, nullable=True)

    # CRM managed fields
    status = Column(String(20), default="New")         # New / Qualified / Lost
    notes = Column(Text, nullable=True)
    owner = Column(String(100), nullable=True)
    follow_up_date = Column(Date, nullable=True)

    # Email tracking
    email_sent = Column(String(5), default="No")        # Yes / No

    created_at = Column(DateTime(timezone=True), server_default=func.now())
