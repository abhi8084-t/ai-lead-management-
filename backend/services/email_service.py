import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.config import settings


def send_acknowledgement_email(to_email: str, name: str, body_text: str | None = None):
    """
    Sends an automatic acknowledgement email to a new lead.
    If body_text is provided (AI-personalized), it is used.
    Otherwise a default generic message is sent.

    Returns True if sent successfully, False otherwise (never raises,
    so a failed email never breaks lead creation).
    """

    if not settings.EMAIL_SENDER or not settings.EMAIL_APP_PASSWORD:
        print("Email credentials not configured - skipping email send.")
        return False

    subject = "Thank you for reaching out!"

    if not body_text:
        body_text = (
            f"Hi {name},\n\n"
            f"Thank you for contacting us! We've received your project details "
            f"and our team will reach out to you shortly to discuss next steps.\n\n"
            f"Best regards,\nThe Team"
        )

    try:
        msg = MIMEMultipart()
        msg["From"] = settings.EMAIL_SENDER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body_text, "plain"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.EMAIL_SENDER, settings.EMAIL_APP_PASSWORD)
            server.sendmail(settings.EMAIL_SENDER, to_email, msg.as_string())

        return True

    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
