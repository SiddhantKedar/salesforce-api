from flask import Flask, render_template, request, jsonify
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
    url = "https://dev.api.mysma.de/staging/e-error-resolution/api/v1/suggest"
    headers = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "Content-Type": "application/json"
    }
    try:
        res = requests.post(url, headers=headers, json={"query": query, "language": "en"})
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/search", methods=["POST"])
def search():
    data = request.json
    text = request.json.get("text", "")
    attribute = data.get("attribute")
    payload = {
        text: text,
        "language": "en-US"
    }

    if attribute:
        payload["attribute"] = attribute
    url = "https://dev.api.mysma.de/staging/e-error-resolution/api/v1/search"
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
    id = request.args.get("id")
    if not id:
        return "Mising Id", 400
    
    try:
        url = f"https://dev.api.mysma.de/staging/e-error-resolution/api/v1/{id}/download"
        headers = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = "utf-8"
        html = res.text
        return html
    except Exception as e:
        return f"<h2> Error fetching document :</h2><pre>{str(e)}</pre>", 500

if __name__ == "__main__":
    app.run(debug=True)
