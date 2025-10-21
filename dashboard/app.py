from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
import os, json
from datetime import datetime
import pandas as pd
import logging

from modules.ai_summary import generate_summary
from modules.report_gen import create_pdf_report
from modules.notifier import send_email
from modules.logger import LOG, LOGS_FOLDER 

# --- Path setup ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
REPORTS_FOLDER = os.path.join(BASE_DIR, "reports")

app = Flask(__name__)
app.secret_key = "supersecret"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure all directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)
os.makedirs(LOGS_FOLDER, exist_ok=True)

# Load sensitive values from environment variables (set in Render Dashboard)
CONFIG = {
    "email_from": os.getenv("EMAIL_FROM"),
    "app_password": os.getenv("APP_PASSWORD"),
    "gemini_api_key": os.getenv("GEMINI_API_KEY"),
}

# Optional safety check (log if missing)
missing = [k for k, v in CONFIG.items() if not v]
if missing:
    LOG.warning(f"⚠️ Missing environment variables: {', '.join(missing)}")

@app.route("/")
def index():
    # Show uploaded CSVs and generated PDFs
    uploads = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(".csv")]
    reports = [f for f in os.listdir(REPORTS_FOLDER) if f.endswith(".pdf")]
    return render_template("index.html", uploads=uploads, reports=reports)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files.get("file")
        client_name = request.form.get("client_name", "").strip()
        client_email = request.form.get("client_email", "").strip()
        
        if file and client_name and file.filename != '':
            filename = f"{client_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            
            try:
                file.save(path)
                LOG.info(f"File uploaded successfully: {filename} for client: {client_name}")
                flash("✅ File uploaded successfully!", "success")

                # --- Automatic Report Generation ---
                df = pd.read_csv(path)
                LOG.info(f"Starting report generation for {client_name}...")
                
                summary = generate_summary(df, CONFIG["gemini_api_key"], "professional")
                pdf_path = create_pdf_report(summary, "Automated Progress Report", client_name)
                
                LOG.info(f"PDF report created at: {pdf_path}")

                # --- Email Sending ---
                # Get client name and email from the form
                client_name = request.form.get("client_name")
                client_email = request.form.get("client_email")

                # Send the generated report via Brevo
                send_success, send_message = send_email(
                    to_email=client_email,
                    subject=f"Report for {client_name}",
                    body="Here’s your automated performance report.",
                    attachments=[pdf_path]
                )

                # Check the return value of send_email
                if not send_success:
                    # Manually raise an exception if the email function failed silently
                    # Use the specific message returned by the notifier function
                    base_error = "Email delivery failed. Please check SMTP configuration and credentials."
                    if send_message:
                        full_error = f"{base_error} Specific error: {send_message}"
                    else:
                        full_error = base_error

                    raise Exception(full_error)


                LOG.info(f"Report successfully generated and emailed to {client_email} for {client_name}")
                flash(f"Report generated and emailed for {client_name}", "success")
            
            except Exception as e:
                LOG.error(f"Critical error during upload/report/email process for {client_name}: {e}", exc_info=True)
                flash(f"Error: {e}", "danger")

            return redirect(url_for("index"))

        LOG.warning("Upload attempted with missing file or client name.")
        flash("Missing file or client name", "danger")

    return render_template("upload.html")


@app.route("/logs")
def logs():
    if not os.path.exists(LOGS_FOLDER):
        return "No logs folder found."

    log_files = [f for f in os.listdir(LOGS_FOLDER) if f.endswith(".txt")]
    if not log_files:
        return "No log files yet."

    # Find the latest log file based on modification time
    latest_log = max(log_files, key=lambda x: os.path.getmtime(os.path.join(LOGS_FOLDER, x)))
    log_path = os.path.join(LOGS_FOLDER, latest_log)

    try:
        with open(log_path, "r") as f:
            lines = f.read().splitlines()[-50:]
    except Exception as e:
        return f"Error reading log file {latest_log}: {e}"

    # Display logs.html template with the last 50 lines
    return render_template("logs.html", logs=lines, log_file=latest_log)


@app.route("/reports/<filename>")
def download_report(filename):
    return send_from_directory(REPORTS_FOLDER, filename)


if __name__ == "__main__":
    #if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        #LOG.info(f"--- Application started in BASE_DIR: {BASE_DIR} ---")
  
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    app.run(debug=True)
