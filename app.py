import os
from flask import Flask, request
import requests

app = Flask(__name__)

TOKEN = os.getenv("8713558550:AAHj7OLCm6U_CGDH2hw1fVqWvKE_4p9pB88")
CHAT_ID = os.getenv("5245230833")

@app.route('/webhook', methods=['POST'])
def github_webhook():
    data = request.json
    
    # Sadece 'push' (commit) olaylarını yakala
    if 'commits' in data:
        repo_name = data.get("repository", {}).get("name")
        pusher = data.get("pusher", {}).get("name")
        
        for commit in data.get("commits", []):
            msg = commit.get("message")
            url = commit.get("url")
            
            text = (f"🛠 **Yeni Commit!**\n\n"
                    f"📂 **Repo:** {repo_name}\n"
                    f"👤 **Yapan:** {pusher}\n"
                    f"📝 **Mesaj:** {msg}\n\n"
                    f"🔗 [Detayları Gör]({url})")
            
            # Telegram'a gönder
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                          json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
    
    return "OK", 200