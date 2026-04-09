import os
from flask import Flask, request
import requests

app = Flask(__name__)

# Çevre değişkenlerinden (Environment Variables) token ve chat ID'yi alıyoruz
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- 1. BEBEK ADIMI: Render ve UptimeRobot için "Ben Hayattayım" Kapısı ---
@app.route('/', methods=['GET'])
def home():
    return "Bot ayakta ve GitHub commit'lerini bekliyor!", 200

# --- GITHUB WEBHOOK KAPISI ---
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

# --- UYGULAMAYI BAŞLATMA ---
if __name__ == '__main__':
    # Render'ın verdiği portu kullan, vermezse 10000 kullan
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)