from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

DATA_FILE = os.path.join(os.path.dirname(__file__), "whitelist.json")

def load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {"entries": [], "total": 0}

def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/submit", methods=["POST"])
def submit():
    try:
        body = request.get_json(force=True)
        wallet = body.get("wallet", "").strip()
        tweet = body.get("tweet", "").strip()

        if not wallet or not tweet:
            return jsonify({"error": "wallet and tweet required"}), 400

        if not wallet.startswith("0x") or len(wallet) < 40:
            return jsonify({"error": "invalid wallet"}), 400

        if "twitter.com" not in tweet and "x.com" not in tweet:
            return jsonify({"error": "invalid tweet url"}), 400

        data = load()

        # Check duplicate
        for entry in data["entries"]:
            if entry["wallet"].lower() == wallet.lower():
                return jsonify({"error": "duplicate", "status": entry["status"]}), 409

        entry = {
            "wallet": wallet,
            "tweet": tweet,
            "time": request.json.get("time", ""),
            "status": "pending"
        }
        data["entries"].append(entry)
        data["total"] = len(data["entries"])
        save(data)

        return jsonify({"ok": True, "total": data["total"]}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/submissions", methods=["GET"])
def submissions():
    data = load()
    return jsonify(data)

@app.route("/", methods=["GET"])
def health():
    data = load()
    return jsonify({"status": "ok", "total": data["total"]})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
