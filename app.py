from flask import Flask, render_template, request, redirect
import joblib
import pandas as pd
import sqlite3
from urllib.parse import urlparse

from feature_extraction import extract_features

app = Flask(__name__)

# Load trained model
model = joblib.load("model.pkl")


# -----------------------------
# Database Functions
# -----------------------------

def init_db():
    conn = sqlite3.connect("predictions.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            result TEXT NOT NULL,
            confidence REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def save_prediction(url, result, confidence):
    conn = sqlite3.connect("predictions.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO predictions (url, result, confidence)
        VALUES (?, ?, ?)
    """, (url, result, confidence))

    conn.commit()
    conn.close()


def get_history():
    conn = sqlite3.connect("predictions.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT url, result, confidence, created_at
        FROM predictions
        ORDER BY id DESC
    """)

    history = cursor.fetchall()

    conn.close()

    return history


def get_statistics():
    conn = sqlite3.connect("predictions.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM predictions")
    total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM predictions
        WHERE result = ?
    """, ("Phishing URL",))

    phishing = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM predictions
        WHERE result = ?
    """, ("Legitimate URL",))

    legitimate = cursor.fetchone()[0]

    conn.close()

    return total, phishing, legitimate


# -----------------------------
# URL Validation
# -----------------------------

def is_valid_url(url):
    """
    Check whether the entered text is a properly formatted URL.
    """

    try:
        parsed_url = urlparse(url)

        return (
            parsed_url.scheme in ["http", "https"]
            and parsed_url.netloc != ""
            and "." in parsed_url.netloc
        )

    except Exception:
        return False


# Create database
init_db()


# -----------------------------
# Main Route
# -----------------------------

@app.route("/", methods=["GET", "POST"])
def home():

    result = None
    result_class = None
    confidence = None
    url = ""
    features = None
    error = None

    if request.method == "POST":

        # Get URL from form
        url = request.form.get("url", "").strip()

        # Validate URL
        if not is_valid_url(url):

            error = (
                "Please enter a valid website URL "
                "starting with http:// or https://."
            )

        else:

            # Extract URL features
            features = extract_features(url)

            # Prepare model input
            feature_values = [[
                features["url_length"],
                features["dot_count"],
                features["hyphen_count"],
                features["special_char_count"],
                features["has_at_symbol"],
                features["uses_https"],
                features["has_ip"],
                features["subdomain_count"],
                features["suspicious_word_count"]
            ]]

            # Feature names
            feature_names = [
                "url_length",
                "dot_count",
                "hyphen_count",
                "special_char_count",
                "has_at_symbol",
                "uses_https",
                "has_ip",
                "subdomain_count",
                "suspicious_word_count"
            ]

            # Convert to DataFrame
            feature_values = pd.DataFrame(
                feature_values,
                columns=feature_names
            )

            # Make prediction
            prediction = model.predict(feature_values)[0]

            # Prediction probabilities
            probabilities = model.predict_proba(feature_values)[0]

            # Determine result
            if prediction == 0:

                result = "Phishing URL"
                result_class = "phishing"
                confidence = probabilities[0] * 100

            else:

                result = "Legitimate URL"
                result_class = "legitimate"
                confidence = probabilities[1] * 100

            # Round confidence
            confidence = round(confidence, 2)

            # Save prediction
            save_prediction(
                url,
                result,
                confidence
            )

    # Get history
    history = get_history()

    # Get statistics
    total, phishing, legitimate = get_statistics()

    return render_template(
        "index.html",
        result=result,
        result_class=result_class,
        confidence=confidence,
        url=url,
        features=features,
        history=history,
        total=total,
        phishing=phishing,
        legitimate=legitimate,
        error=error
    )


# -----------------------------
# Clear History
# -----------------------------

@app.route("/clear-history", methods=["POST"])
def clear_history():

    conn = sqlite3.connect("predictions.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM predictions")

    conn.commit()
    conn.close()

    return redirect("/")


# -----------------------------
# Run Application
# -----------------------------

if __name__ == "__main__":
    app.run(debug=True)
