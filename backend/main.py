from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routers import leads

app = FastAPI(
    title="AI Lead Management System",
    description="Backend API for capturing, scoring, and managing leads using AI.",
    version="1.0.0",
)

# Allow the Streamlit frontend (running on a different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all /leads routes
app.include_router(leads.router)


@app.on_event("startup")
def on_startup():
    """Creates the leads table automatically if it doesn't exist."""
    init_db()


@app.get("/")
def root():
    return {"message": "AI Lead Management API is running", "docs": "/docs"}
