import resend
import os

resend.api_key = os.getenv("RESEND_API_KEY")

def send_email(to_email, subject, body, attachments=None):
    try:
        params = {
            "from": f"Automation Project <{os.getenv('EMAIL_FROM')}>",
            "to": [to_email],
            "subject": subject,
            "text": body,
        }

        if attachments:
            params["attachments"] = [
                {"path": path} for path in attachments
            ]

        resend.Emails.send(params)
        return True, "Email sent successfully!"
    except Exception as e:
        return False, f"Error sending email: {str(e)}"
