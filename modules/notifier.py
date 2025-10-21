import os
import base64
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException


def send_email(to_email, subject, body="See attached report.", attachments=None):
    """
    Sends an email with optional attachments using Brevo (Sendinblue) API.
    """

    try:
        # --- Configure Brevo client ---
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY")

        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )

        # --- Build base email ---
        email_data = {
            "sender": {
                "name": "Automation Dashboard",
                "email": os.getenv("EMAIL_FROM"),
            },
            "to": [{"email": to_email}],
            "subject": subject,
            "html_content": f"<p>{body}</p>",
        }

        # --- Attach PDF files correctly (Base64-encoded text) ---
        if attachments:
            email_data["attachment"] = []
            for path in attachments:
                try:
                    with open(path, "rb") as file:
                        encoded_content = base64.b64encode(file.read()).decode("utf-8")
                        email_data["attachment"].append({
                            "name": os.path.basename(path),
                            "content": encoded_content
                        })
                except Exception as e:
                    print(f"⚠️ Could not attach file {path}: {e}")

        # --- Send via Brevo ---
        email = sib_api_v3_sdk.SendSmtpEmail(**email_data)
        api_instance.send_transac_email(email)

        print(f"📨 Email with attachment sent successfully to {to_email}")
        return True, "Email sent successfully with attachment!"

    except ApiException as e:
        print(f"❌ Brevo API error: {e}")
        return False, f"Brevo API error: {e}"

    except Exception as e:
        print(f"❌ General error sending email: {e}")
        return False, str(e)
