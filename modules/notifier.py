import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os

def send_email(to_email, subject, body, attachments=None):
    msg = MIMEMultipart()
    msg["From"] = os.getenv("EMAIL_FROM")
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    if attachments:
        for file_path in attachments:
            with open(file_path, "rb") as f:
                part = MIMEApplication(f.read(), Name=file_path)
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                msg.attach(part)

    try:
        smtp_server = "smtp-relay.brevo.com"
        smtp_port = 587
        smtp_user = os.getenv("EMAIL_FROM")
        smtp_pass = os.getenv("BREVO_SMTP_KEY")

        with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as smtp:
            smtp.starttls()
            smtp.login(smtp_user, smtp_pass)
            smtp.send_message(msg)

        return True, "Email sent successfully!"
    except Exception as e:
        return False, f"Error sending email: {str(e)}"
