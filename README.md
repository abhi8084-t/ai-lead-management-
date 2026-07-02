# AI Lead Management System

An AI-powered lead management system built for the Delipat AI Engineer Internship assessment. It captures leads from a public form, stores them in a CRM, qualifies them with AI, and triggers an automated acknowledgement email.

```text
Website Form -> CRM Database -> AI Qualification -> Automated Email -> Sales Follow-up
```

## Live Links

- Frontend: `https://ai-lead-management.streamlit.app/`
- Backend API: `https://ai-lead-management.onrender.com`
- API Docs: `https://ai-lead-management.onrender.com/docs`

## Core Features

- Landing page with lead capture form
- Required field validation for name, email, phone, and project description
- CRM dashboard with total, new, qualified, and lost lead counts
- Search and filters for status, temperature, and industry
- Row-level `View` action for reviewing a lead without manually typing an ID
- Lead detail view with editable status, notes, owner, and follow-up date
- AI lead scoring with score, temperature, confidence, reasoning, and next action
- Automated acknowledgement email after lead creation
- AI-personalized email body
- CSV export for filtered leads

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit |
| Backend | FastAPI |
| Database | Aiven MySQL / local MySQL |
| ORM | SQLAlchemy |
| AI | Groq API |
| Email | SMTP, Gmail app password supported |
| Backend Deployment | Render |
| Frontend Deployment | Streamlit Community Cloud |

## Architecture

```text
frontend/                                  backend/

Home.py --------------------- POST /leads -> routers/leads.py
Lead capture form                            |
                                             v
pages/Dashboard.py ---------- GET /leads -> crud.py <-> database.py <-> MySQL
CRM dashboard                                |
                                             v
pages/Lead_Details.py ------- PUT /leads -> services/
Lead management                              |-- ai_service.py
                                             |-- email_service.py
                                             |-- dashboard.py
```

When a lead is submitted:

1. The frontend sends lead details to the FastAPI backend.
2. The backend saves the lead with status `New`.
3. A background task asks Groq to qualify the lead.
4. The AI result is saved back to the lead.
5. Hot leads are automatically marked `Qualified`.
6. The email service sends an acknowledgement email.
7. The dashboard displays the full CRM and AI result.

## Project Structure

```text
ai-lead-management/
|-- backend/
|   |-- main.py
|   |-- database.py
|   |-- models.py
|   |-- schemas.py
|   |-- crud.py
|   |-- requirements.txt
|   |-- routers/
|   |   |-- leads.py
|   |-- services/
|   |   |-- ai_service.py
|   |   |-- dashboard.py
|   |   |-- email_service.py
|   |-- utils/
|       |-- config.py
|
|-- frontend/
|   |-- Home.py
|   |-- api.py
|   |-- requirements.txt
|   |-- pages/
|       |-- Dashboard.py
|       |-- Lead_Details.py
|
|-- DEPLOYMENT.md
|-- runtime.txt
|-- run.py
|-- README.md
```

## Local Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=lead_management
DB_SSL_REQUIRED=false

GROQ_API_KEY=your_groq_api_key

EMAIL_SENDER=youremail@gmail.com
EMAIL_APP_PASSWORD=your_gmail_app_password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587

BACKEND_URL=http://localhost:8000
```

For Aiven MySQL, set `DB_SSL_REQUIRED=true`.

### 4. Run Backend

From the project root:

```bash
uvicorn --app-dir backend main:app --reload --port 8000
```

Or use:

```powershell
.\start_backend.ps1
```

### 5. Run Frontend

Open another terminal:

```bash
streamlit run frontend/Home.py
```

Frontend runs at:

```text
http://localhost:8501
```

Backend docs run at:

```text
http://localhost:8000/docs
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API health message |
| POST | `/leads` | Submit a new lead |
| GET | `/leads` | List all leads |
| GET | `/leads/stats` | Get CRM dashboard counts |
| GET | `/leads/{id}` | Get one lead |
| PUT | `/leads/{id}` | Update CRM fields |

## AI Prompts Used

### Lead Qualification Prompt

The backend sends the lead's industry, company size, budget, and project description to Groq with instructions to return strict JSON:

```json
{
  "score": "integer 0-100",
  "temperature": "Hot, Warm, or Cold",
  "confidence": "integer 0-100",
  "reasoning": "short explanation",
  "next_action": "recommended next step"
}
```

The app validates and clamps the AI response before saving it.

### Email Personalization Prompt

The backend asks Groq to write a short, warm, professional acknowledgement email tailored to the lead's name, industry, and project description.

If AI fails, the system falls back to a generic acknowledgement email.

## Deployment

Deployment instructions are documented in [DEPLOYMENT.md](DEPLOYMENT.md).

Current deployment stack:

- Database: Aiven MySQL
- Backend: Render
- Frontend: Streamlit Community Cloud

Render backend:

```bash
pip install -r backend/requirements.txt
uvicorn --app-dir backend main:app --host 0.0.0.0 --port $PORT
```

Streamlit main file:

```text
frontend/Home.py
```

Streamlit secret:

```toml
BACKEND_URL = "https://ai-lead-management.onrender.com"
```

## Demo Walkthrough

For a 5-7 minute demo video:

1. Open the Streamlit frontend.
2. Submit a new lead from the Home page.
3. Open Dashboard and show the lead in the pipeline.
4. Wait a few seconds and refresh to show AI score, temperature, confidence, reasoning, and next action.
5. Open the lead review section and update status, owner, notes, or follow-up date.
6. Show backend `/docs` and API endpoints.
7. Explain the AI prompts and tools used during development.

## Assessment Coverage

| Requirement | Status |
|-------------|--------|
| Landing page and lead form | Complete |
| Form validation | Complete |
| CRM dashboard cards | Complete |
| Lead detail and CRM editing | Complete |
| AI lead qualification | Complete |
| Structured AI result | Complete |
| Automated acknowledgement email | Complete |
| AI-personalized email | Complete |
| Search and filters | Complete |
| Dashboard charts/summary | Complete |
| CSV export | Complete |

## Notes

- `.env` is ignored by git and must not be committed.
- Render free instances may sleep after inactivity, so the first request can be slow.
- If the Groq API fails, the app uses a safe fallback lead score so the CRM still works.
- If email credentials are missing or invalid, lead creation still succeeds and email status remains pending/not sent.
