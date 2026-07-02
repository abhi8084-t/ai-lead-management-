# Free Deployment Guide

Recommended stack:

- Database: Aiven MySQL
- Backend: Render Web Service
- Frontend: Streamlit Community Cloud

## 1. Push Code to GitHub

Do not commit local secrets or virtual environments.

Required files:

- `backend/requirements.txt`
- `frontend/requirements.txt`
- `runtime.txt`
- `backend/`
- `frontend/`
- `README.md`

Ignored files:

- `.env`
- `venv/`
- `.streamlit/`

## 2. Create Aiven MySQL

1. Create a free Aiven MySQL service.
2. Open the service connection details.
3. Copy:
   - host
   - port
   - user
   - password
   - database name
4. If Aiven gives you a CA certificate, download it for local testing.

For Render, use environment variables instead of committing certificates or credentials.

## 3. Deploy Backend on Render

Create a new Render Web Service from the GitHub repo.

Python version:

```text
python-3.11.9
```

This is pinned in `runtime.txt`. Do not use Python 3.14 for this project because some dependencies may try to compile from source during deployment.

Build command:

```bash
pip install -r backend/requirements.txt
```

Start command:

```bash
uvicorn --app-dir backend main:app --host 0.0.0.0 --port $PORT
```

Backend environment variables:

```env
DB_HOST=mysql-24d0a320-abhishektiwari45788-581c.j.aivencloud.com
DB_PORT=13672
DB_USER=avnadmin
DB_PASSWORD=your-aiven-password
DB_NAME=defaultdb
DB_SSL_REQUIRED=true

GROQ_API_KEY=your-groq-api-key

EMAIL_SENDER=your-email@gmail.com
EMAIL_APP_PASSWORD=your-gmail-app-password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

Alternative database config:

```env
DATABASE_URL=mysql+pymysql://avnadmin:PASSWORD@mysql-24d0a320-abhishektiwari45788-581c.j.aivencloud.com:13672/defaultdb
DB_SSL_REQUIRED=true
```

Use this only if your password does not contain URL-breaking characters, or URL-encode the password first.

After deploy, test:

```text
https://your-render-backend.onrender.com/docs
```

## 4. Deploy Frontend on Streamlit Community Cloud

1. Create a new Streamlit app from the GitHub repo.
2. Main file path:

```text
frontend/Home.py
```

Streamlit will install dependencies from the repo. If it asks for a requirements file, use:

```text
frontend/requirements.txt
```

3. Add this secret/environment variable:

```env
BACKEND_URL=https://your-render-backend.onrender.com
```

4. Deploy and open the Streamlit URL.

## 5. Final Test

1. Open the Streamlit frontend.
2. Submit one lead from Home.
3. Open Dashboard.
4. Confirm:
   - lead is saved
   - AI score appears after a few seconds
   - status can be updated
   - backend `/docs` opens

## Common Issues

### Backend deploys but form cannot submit

Check `BACKEND_URL` in Streamlit Cloud. It must be the Render backend URL without a trailing slash.

### Backend cannot connect to Aiven

Check Aiven credentials and make sure `DB_NAME` matches the Aiven database name.

### Email is not sent

Use a Gmail App Password, not your normal Gmail password.

### AI score stays pending

Check the Render logs for Groq API key or model errors.
