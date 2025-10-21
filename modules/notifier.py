import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

def send_email(to_email, subject, body="See attached report.", attachments=None):
    """
    Sends an email using the Brevo API (Sendinblue).
    """
    try:
        # Configure Brevo client
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY")

        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )

        # Build the email
        email = sib_api_v3_sdk.SendSmtpEmail(
            sender={"name": "Automation Dashboard", "email": os.getenv("EMAIL_FROM")},
            to=[{"email": to_email}],
            subject=subject,
            html_content=f"<p>{body}</p>"
        )

        # Attach files if present
        if attachments:
            email.attachment = []
            for path in attachments:
                with open(path, "rb") as f:
                    file_data = f.read()
                email.attachment.append({
                    "name": os.path.basename(path),
                    "content": file_data.encode("base64") if hasattr(file_data, "encode") else file_data
                })

        # Send the email
        api_instance.send_transac_email(email)
        print(f"📨 Email sent successfully to {to_email}")
        return True, "Email sent successfully!"

    except ApiException as e:
        print(f"❌ Brevo API error: {e}")
        return False, f"Brevo API error: {e}"
    except Exception as e:
        print(f"❌ General error sending email: {e}")
        return False, str(e)
