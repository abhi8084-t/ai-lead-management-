# AI Lead Management System

An AI-powered lead management system that takes a visitor from a website form through CRM storage, AI qualification, and automated email.

**Flow:** Website Form -> MySQL Database (CRM) -> AI Qualification (Groq) -> Automated Email

---

## Architecture

```text
frontend/ (Streamlit)                         backend/ (FastAPI)

Home.py -------------------- HTTP ----------> routers/leads.py
Landing page + lead form                       |
                                               v
pages/Dashboard.py -------- HTTP ----------> crud.py <-> database.py
pages/Lead_Details.py                          |
                                               v
                                      services/ai_service.py
                                      services/email_service.py
                                      services/dashboard.py
                                               |
                                               v
                                         MySQL Database
```

When a lead is submitted:

1. The form data is validated and saved to MySQL immediately with status `New`.
2. In the background, Groq analyzes the lead's industry, company size, budget, and description.
3. The AI result is saved back to the lead with a score, temperature, confidence, reasoning, and next action.
4. The dashboard shows summary cards, charts, searchable lead rows, AI results, and editable CRM fields on one screen.
5. If the lead is `Hot`, its status is automatically updated to `Qualified`.
6. A personalized acknowledgement email is generated and sent automatically.

---

## Tech Stack

| Layer    | Technology               |
|----------|--------------------------|
| Frontend | Streamlit                |
| Backend  | FastAPI                  |
| Database | MySQL with SQLAlchemy    |
| AI       | Groq API                 |
| Email    | SMTP, typically Gmail    |

---

## Project Structure

```text
ai-lead-management/
|-- backend/
|   |-- main.py                   # FastAPI entry point
|   |-- database.py               # MySQL connection and table setup
|   |-- models.py                 # Lead table schema
|   |-- schemas.py                # Pydantic request/response models
|   |-- crud.py                   # Database operations
|   |-- routers/
|   |   |-- leads.py              # All /leads API endpoints
|   |-- services/
|   |   |-- ai_service.py         # Groq-powered lead scoring
|   |   |-- email_service.py      # SMTP email sending
|   |   |-- dashboard.py          # Dashboard stat calculations
|   |-- utils/
|       |-- config.py             # Environment variable loader
|
|-- frontend/
|   |-- Home.py                   # Landing page and lead form
|   |-- api.py                    # Backend API calls
|   |-- pages/
|       |-- Dashboard.py          # CRM dashboard
|       |-- Lead_Details.py       # Lead detail and edit page
|
|-- run.py                        # Starts backend and frontend together
|-- .env                          # Local environment variables
|-- README.md
```

---

## Setup Instructions

For free deployment with Aiven MySQL, Render, and Streamlit Community Cloud, see `DEPLOYMENT.md`.

### 1. Prerequisites

- Python 3.10+
- MySQL server running locally or in the cloud
- A Groq API key from `https://console.groq.com`
- A Gmail account with an app password if you want SMTP email sending

### 2. Install Dependencies

From the project root:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### 3. Configure Environment Variables

Create or edit `.env` in the project root:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=lead_management

GROQ_API_KEY=your_groq_api_key_here

EMAIL_SENDER=youremail@gmail.com
EMAIL_APP_PASSWORD=your_gmail_app_password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587

BACKEND_URL=http://localhost:8000
```

The backend creates the configured MySQL database and `leads` table automatically when it starts, as long as the MySQL user has permission to create databases.

### 4. Run the Project

Start both the backend and frontend together:

```bash
python run.py
```

This starts:

- Backend API at `http://localhost:8000`
- FastAPI docs at `http://localhost:8000/docs`
- Streamlit frontend at `http://localhost:8501`

Or run them separately:

```bash
# Terminal 1, from the project root
uvicorn --app-dir backend main:app --reload --port 8000

# Terminal 2
cd frontend
streamlit run Home.py
```

You can also start the backend from inside the `backend` folder:

```bash
cd backend
uvicorn main:app --reload --port 8000
```

---

## API Endpoints

| Method | Endpoint      | Description                         |
|--------|---------------|-------------------------------------|
| POST   | `/leads`      | Submit a new lead                   |
| GET    | `/leads`      | Get all leads                       |
| GET    | `/leads/stats`| Get dashboard counts                |
| GET    | `/leads/{id}` | Get a single lead                   |
| PUT    | `/leads/{id}` | Update status, notes, owner, follow-up |

---

## AI Behavior

The lead qualification prompt in `backend/services/ai_service.py` sends the lead's industry, company size, budget, and project description to Groq. It expects a JSON response with:

- `score`
- `temperature`
- `confidence`
- `reasoning`
- `next_action`

The email personalization prompt asks Groq to write a short acknowledgement email tailored to the lead's name, industry, and project description.

---

## Frontend Highlights

- Dashboard cards for total, new, qualified, and lost leads.
- Search and filters for status, temperature, and industry.
- Row-level `View` action to open a lead without manually typing an ID.
- AI qualification panel with score progress, confidence, reasoning, and recommended action.
- CSV export for filtered lead data.
- Lead Details page automatically opens the selected dashboard lead.

---

## Notes

- AI calls and email sending happen as background tasks after the lead is saved.
- If the Groq API call fails, the system falls back to a default `Warm` score so the app keeps working.
- `.env` is excluded from version control. Do not commit real credentials.
