from sqlalchemy.orm import Session
from models import Lead


def get_dashboard_stats(db: Session) -> dict:
    """
    Calculates the 4 dashboard metrics by querying the leads table.
    """
    total = db.query(Lead).count()
    new = db.query(Lead).filter(Lead.status == "New").count()
    qualified = db.query(Lead).filter(Lead.status == "Qualified").count()
    lost = db.query(Lead).filter(Lead.status == "Lost").count()

    return {
        "total_leads": total,
        "new_leads": new,
        "qualified_leads": qualified,
        "lost_leads": lost,
    }
