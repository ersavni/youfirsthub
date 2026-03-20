from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# ---------------------------
# HOME PAGE
# ---------------------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------------------
# FORM SUBMISSION
# ---------------------------
@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    phone = request.form.get("phone")
    email = request.form.get("email")
    postcode = request.form.get("postcode")
    property_type = request.form.get("property_type")
    service_type = request.form.get("service_type")

    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            email TEXT,
            postcode TEXT,
            property_type TEXT,
            service_type TEXT
        )
    """)

    cursor.execute("""
        INSERT INTO leads (name, phone, email, postcode, property_type, service_type)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, phone, email, postcode, property_type, service_type))

    conn.commit()
    conn.close()

    return redirect("/thank-you")


# ---------------------------
# THANK YOU PAGE
# ---------------------------
@app.route("/thank-you")
def thank_you():
    return render_template("thankyou.html")


# ---------------------------
# PRIVACY POLICY (IMPORTANT)
# ---------------------------
@app.route("/privacy-policy")
def privacy_policy():
    return render_template("privacy.html")


# ---------------------------
# RUN APP
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)