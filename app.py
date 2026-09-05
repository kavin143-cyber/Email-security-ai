from flask import Flask, render_template, request, jsonify
from datetime import datetime
import re

app = Flask(__name__)

history = []


# -----------------------------
# EMAIL THREAT ANALYZER
# -----------------------------
def analyze_email(sender, subject, body):

    text = f"{sender} {subject} {body}".lower()

    risk = 0
    reasons = []
    threat_types = []

    # Suspicious keywords
    keyword_rules = {
        "urgent": 8,
        "immediately": 7,
        "verify your account": 12,
        "verify account": 10,
        "password": 6,
        "otp": 8,
        "click here": 10,
        "login": 7,
        "winner": 12,
        "congratulations": 8,
        "prize": 10,
        "free money": 15,
        "claim now": 12,
        "limited time": 8,
        "bank account": 10,
        "credit card": 10,
        "suspended": 10,
        "security alert": 8
    }

    for keyword, points in keyword_rules.items():
        if keyword in text:
            risk += points
            reasons.append(f"Suspicious phrase: {keyword}")

    # URL detection
    urls = re.findall(r'https?://[^\s]+', text)

    if urls:
        risk += 15
        reasons.append("Email contains an external link")

        for url in urls:
            if any(x in url for x in [
                "bit.ly",
                "tinyurl",
                "t.co",
                "goo.gl"
            ]):
                risk += 10
                reasons.append("Shortened URL detected")

    # Sender checks
    suspicious_domains = [
        "tempmail",
        "mailinator",
        "example",
        "fake"
    ]

    for domain in suspicious_domains:
        if domain in sender.lower():
            risk += 20
            reasons.append("Unusual sender domain detected")

    # Sender validation
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", sender):
        risk += 20
        reasons.append("Sender email format looks invalid")

    # Excessive capital letters
    if len(body) > 20:
        capital_count = sum(1 for c in body if c.isupper())
        letters = sum(1 for c in body if c.isalpha())

        if letters > 0:
            capital_ratio = capital_count / letters

            if capital_ratio > 0.45:
                risk += 8
                reasons.append("Unusual use of capital letters")

    # Excessive exclamation marks
    if body.count("!") >= 4:
        risk += 6
        reasons.append("Excessive urgency/exclamation marks")

    risk = min(risk, 99)

    # Threat classification
    if risk >= 70:
        result = "HIGH RISK"
        category = "Phishing / Scam"
        status = "danger"
        threat_types.append("High Risk")

    elif risk >= 40:
        result = "SUSPICIOUS"
        category = "Potentially Dangerous"
        status = "warning"
        threat_types.append("Suspicious")

    else:
        result = "LIKELY SAFE"
        category = "Low Risk"
        status = "safe"
        threat_types.append("Safe")

    # Additional threat type
    scam_words = [
        "prize",
        "winner",
        "free money",
        "claim now"
    ]

    if any(word in text for word in scam_words):
        category = "Possible Scam"

    if any(word in text for word in [
        "verify your account",
        "verify account",
        "login",
        "password"
    ]):
        if risk >= 40:
            category = "Possible Phishing"

    # Reason fallback
    if not reasons:
        reasons.append("No major suspicious indicators detected")

    # Recommendation
    if risk >= 70:
        recommendation = (
            "Do not click links, open unknown attachments, "
            "or share passwords, OTPs, or banking information."
        )

    elif risk >= 40:
        recommendation = (
            "Be cautious. Verify the sender independently "
            "before responding or clicking links."
        )

    else:
        recommendation = (
            "No major threat indicators were detected. "
            "Still verify unexpected requests."
        )

    return {
        "result": result,
        "risk": risk,
        "category": category,
        "status": status,
        "reasons": reasons,
        "recommendation": recommendation
    }


# -----------------------------
# HOME
# -----------------------------
@app.route("/")
def home():

    total = len(history)

    high_risk = sum(
        1 for item in history
        if item["risk"] >= 70
    )

    safe = sum(
        1 for item in history
        if item["risk"] < 40
    )

    return render_template(
        "index.html",
        total=total,
        high_risk=high_risk,
        safe=safe
    )


# -----------------------------
# ANALYZE PAGE
# -----------------------------
@app.route("/analyze")
def analyze_page():
    return render_template("analyze.html")


# -----------------------------
# HISTORY PAGE
# -----------------------------
@app.route("/history")
def history_page():

    high_risk = sum(
        1 for item in history
        if item["risk"] >= 70
    )

    suspicious = sum(
        1 for item in history
        if 40 <= item["risk"] < 70
    )

    safe = sum(
        1 for item in history
        if item["risk"] < 40
    )

    return render_template(
        "history.html",
        history=history,
        high_risk=high_risk,
        suspicious=suspicious,
        safe=safe,
        total=len(history)
    )


# -----------------------------
# ANALYZE API
# -----------------------------
@app.route("/analyze_email", methods=["POST"])
def analyze_email_api():

    data = request.get_json()

    sender = data.get("sender", "").strip()
    subject = data.get("subject", "").strip()
    body = data.get("body", "").strip()

    if not sender or not subject or not body:
        return jsonify({
            "error": "Please fill all fields."
        }), 400

    analysis = analyze_email(
        sender,
        subject,
        body
    )

    item = {
        "sender": sender,
        "subject": subject,
        "result": analysis["result"],
        "risk": analysis["risk"],
        "category": analysis["category"],
        "time": datetime.now().strftime(
            "%d-%m-%Y %I:%M %p"
        )
    }

    history.insert(0, item)

    # Keep latest 50 records
    if len(history) > 50:
        history.pop()

    return jsonify(analysis)


# -----------------------------
# CLEAR HISTORY
# -----------------------------
@app.route("/clear_history", methods=["POST"])
def clear_history():

    history.clear()

    return jsonify({
        "success": True
    })


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
      )
