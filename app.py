from flask import Flask, render_template, request, redirect, url_for
import csv
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

CSV_FILE = "leads.csv"

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
LEAD_TO = os.getenv("LEAD_TO")


def create_csv_if_not_exists():
    file_exists = os.path.exists(CSV_FILE)
    file_is_empty = not file_exists or os.path.getsize(CSV_FILE) == 0

    if file_is_empty:
        with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                "timestamp",
                "name",
                "phone",
                "postcode",
                "property_type",
                "service",
                "message"
            ])


def save_lead_to_csv(timestamp, name, phone, postcode, property_type, service, message):
    create_csv_if_not_exists()

    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            timestamp,
            name,
            phone,
            postcode,
            property_type,
            service,
            message
        ])


def send_lead_email(timestamp, name, phone, postcode, property_type, service, message):
    if not EMAIL_USER or not EMAIL_PASS or not LEAD_TO:
        print("Email settings are missing in .env file.")
        return

    email_body = f"""
New lead received from YouFirstHub

Time: {timestamp}
Name: {name}
Phone: {phone}
Postcode: {postcode}
Property Type: {property_type}
Service Needed: {service}
Message: {message if message else 'No extra details provided'}
"""

    msg = EmailMessage()
    msg["Subject"] = f"New Pest Control Lead - {name} - {postcode}"
    msg["From"] = EMAIL_USER
    msg["To"] = LEAD_TO
    msg.set_content(email_body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    phone = request.form.get("phone")
    postcode = request.form.get("postcode")
    property_type = request.form.get("property_type")
    service = request.form.get("service")
    message = request.form.get("message")

    if not name or not phone or not postcode or not property_type or not service:
        return "Please fill in all required fields", 400

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    save_lead_to_csv(timestamp, name, phone, postcode, property_type, service, message)

    try:
        send_lead_email(timestamp, name, phone, postcode, property_type, service, message)
    except Exception as e:
        print(f"Email failed to send: {e}")

    return redirect(url_for("thank_you"))


@app.route("/thank-you")
def thank_you():
    return render_template("thankyou.html")


if __name__ == "__main__":
    create_csv_if_not_exists()
    app.run(debug=True)