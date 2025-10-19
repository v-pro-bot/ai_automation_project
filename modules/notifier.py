import smtplib
from email.message import EmailMessage
import os

def send_email(subject, to_email, from_email, app_password, body="See attached report.", attachments=None):
    """
    Sends an email with attachments and handles exceptions explicitly.
    
    Returns: (bool, str) -> (Success/Failure status, Error message or empty string)
    """
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    msg.set_content(body)

    if attachments:
        for file_path in attachments:
            try:
                # Use os.path.basename for safe filename extraction
                file_name = os.path.basename(file_path)
                with open(file_path, "rb") as f:
                    # Assuming attachments are PDF files
                    msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=file_name)
            except FileNotFoundError:
                return False, f"Attachment file not found: {file_path}"

    try:
        # Connect to Gmail SMTP server using SSL with a 60-second timeout
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=60) as smtp:
            smtp.login(from_email, app_password)
            
            # send_message returns a dict of refused recipients
            refused_recipients = smtp.send_message(msg)
            
            if refused_recipients:
                # If the dictionary is not empty, at least one recipient was refused delivery
                refused_list = ", ".join(refused_recipients.keys())
                error_message = f"SMTP Server refused delivery to recipients: {refused_list}. Check recipient addresses and spam policies."
                return False, error_message
            
            # Success: Message was accepted by the SMTP server with no immediate refusal
            return True, ""
            
    except smtplib.SMTPAuthenticationError:
        # Error: Credentials rejected
        error_message = "Authentication failed. Check if your 'app_password' is correct and if you need to use Google's App Password feature."
        return False, error_message
    
    except smtplib.SMTPSenderRefused as e:
        # Error: Server refused the sender address (common with policy issues)
        error_message = f"Sender address refused by server. Check 'from_email' and server policies. Detail: {e}"
        return False, error_message
        
    except Exception as e:
        # Catch any other SMTP or general connection/timeout errors
        error_message = f"Failed to connect, timeout, or general error: {e}"
        return False, error_message
