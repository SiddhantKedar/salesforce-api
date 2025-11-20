from flask import Flask, render_template, request, jsonify, redirect
import requests
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

@app.route("/")
def index():
    return render_template("search.html")

@app.route("/api/suggest", methods=["POST"])
def suggest():
    query = request.json.get("query", "")
    url = "https://prod.api.mysma.de/production/e-error-resolution/api/v1/suggest"
    headers = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "Content-Type": "application/json"
    }
    try:
        res = requests.post(url, headers=headers, json={"query": query})
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/search", methods=["POST"])
def search():
    data = request.json
    text = request.json.get("text", "")
    attribute = data.get("attribute")
    payload = {
        "text": text,
        "filter" : {
            "Language": "en",
            "iirdsRole": "https://metadata.sma.com/iirds#10857875979",
            "DocumentType": [
            "Document",
            "Topic",
            "CustomDocumentType1"
            ],
        },
        "limit" : 5
    }

    if attribute:
        payload["attribute"] = attribute
    url = "https://prod.api.mysma.de/production/e-error-resolution/api/v1/search"
    headers = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "Content-Type": "application/json"
    }
    try:
        res = requests.post(url, headers=headers, json=payload)
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route("/view")
def view():
    doc_id = request.args.get("id")
    if not doc_id:
        return "Missing id", 400

    guest_token = os.getenv("GUEST_TOKEN")
    if not guest_token:
        return "Guest token missing in .env", 500

    # Build final working Empolis link
    empolis_url = (
        f"https://esc-eu-central-1.empolisservices.com/gatekeeper/guesttokens/580/"
        f"{guest_token}?app="
        f"https://esc-eu-central-1.empolisservices.com/service-express/portal/project1_p/document/{doc_id}"
    )

    # Redirect user straight to the Empolis document
    return redirect(empolis_url, code=302)


if __name__ == "__main__":
    app.run(debug=True)
