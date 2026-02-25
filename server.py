import os
import json
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

BAN_FILE = "/var/data/bans.json"
WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_HERE"

# Ensure ban file exists
if not os.path.exists(BAN_FILE):
    with open(BAN_FILE, "w") as f:
        json.dump([], f)

def read_bans():
    with open(BAN_FILE, "r") as f:
        return json.load(f)

def write_bans(bans):
    with open(BAN_FILE, "w") as f:
        json.dump(bans, f, indent=2)

def send_webhook(action, moderator, target_user_id, target_username, reason):
    mod_profile = f"https://www.roblox.com/users/{moderator['userId']}/profile"
    target_profile = f"https://www.roblox.com/users/{target_user_id}/profile"

    color = 16711680 if action == "Ban" else 16753920 if action == "Kick" else 65280

    data = {
        "embeds": [{
            "title": f"Moderation Action: {action}",
            "color": color,
            "fields": [
                {"name": "Moderator", "value": f"{moderator['name']}\nUserId: {moderator['userId']}\nProfile: {mod_profile}", "inline": False},
                {"name": "Target", "value": f"{target_username}\nUserId: {target_user_id}\nProfile: {target_profile}", "inline": False},
                {"name": "Reason", "value": reason or "No reason provided", "inline": False}
            ],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }]
    }
    try:
        requests.post(WEBHOOK_URL, json=data)
    except:
        pass

@app.route("/ban", methods=["POST"])
def ban_user():
    data = request.json
    user_id = data["userId"]
    username = data.get("username", "Unknown")
    reason = data.get("reason")
    moderator = data.get("moderator", {"name": "Unknown", "userId": 0})

    bans = read_bans()
    if not any(b["userId"] == user_id for b in bans):
        bans.append({
            "userId": user_id,
            "username": username,
            "reason": reason,
            "moderatorId": moderator["userId"],
            "timestamp": int(time.time())
        })
        write_bans(bans)
    
    send_webhook("Ban", moderator, user_id, username, reason)
    return jsonify({"success": True})

@app.route("/unban", methods=["POST"])
def unban_user():
    data = request.json
    user_id = data["userId"]

    bans = read_bans()
    bans = [b for b in bans if b["userId"] != user_id]
    write_bans(bans)

    send_webhook("Unban", {"name": "System", "userId": 0}, user_id, "Unknown", None)
    return jsonify({"success": True})

@app.route("/bans/<int:user_id>", methods=["GET"])
def get_bans(user_id):
    bans = [b for b in read_bans() if b["userId"] == user_id]
    return jsonify(bans)

@app.route("/healthz", methods=["GET"])
def health():
    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)