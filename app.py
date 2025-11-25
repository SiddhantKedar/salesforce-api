from flask import Flask, render_template, request, jsonify, redirect
import requests
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

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

@app.route("/api/summarize", methods=["POST"])
def summarize():
    data = request.json
    doc_id = data.get("id")

    if not doc_id:
        return jsonify({"error": "Missing document id"}), 400

    try:
        token = os.getenv("BEARER_TOKEN")
        if not token:
            return jsonify({"error": "Bearer token missing in .env"}), 500

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        # Plain text
        text_url = (
            f"https://esc-eu-central-1.empolisservices.com/service-express/"
            f"api/v1/environments/project1_p/documents/{doc_id}/text"
        )

        text_res = requests.get(text_url, headers=headers)
        if text_res.status_code == 401:
            return jsonify({"error": "Bearer token expired"}), 401
        
        text_json = text_res.json()

        content_blocks = text_json.get("content", [])
        full_text = "\n".join(content_blocks)

        if not full_text.strip():
            return jsonify({"error": "Document contains no text"}), 500

        # Custom Summarizer
        summarize_url = (
            "https://esc-eu-central-1.empolisservices.com/api/rag/0.1/"
            "functions/sma.summarizer.v1/invoke"
        )

        sum_res = requests.post(
            summarize_url, 
            json={"text": full_text},
            headers=headers
        )
        if sum_res.status_code == 401:
            return jsonify({"error": "Bearer token expired"}), 401
        
        sum_json = sum_res.json()

        summary_text = sum_json.get("text")

        return jsonify({"summary": summary_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
