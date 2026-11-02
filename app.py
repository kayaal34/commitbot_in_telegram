import hashlib
import hmac
import html
import os
from flask import Flask, abort, request
import requests

app = Flask(__name__)

# Çevre değişkenlerinden (Environment Variables) token ve chat ID'yi alıyoruz
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
# GitHub webhook ayarındaki "Secret" alanı. Boşsa imza kontrolü yapılmaz.
WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")

TELEGRAM_TIMEOUT = 10


def valid_signature(body, header):
    """GitHub'ın X-Hub-Signature-256 başlığını gövdeyle karşılaştırır."""
    if not WEBHOOK_SECRET:
        return True
    if not header or not header.startswith("sha256="):
        return False
    expected = hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest("sha256=" + expected, header)


def format_commit(repo_name, pusher, commit):
    """Commit mesajını Telegram'ın HTML biçimine güvenli şekilde çevirir."""
    msg = (commit.get("message") or "").split("\n", 1)[0]
    url = commit.get("url") or ""
    return (f"🛠 <b>Yeni Commit!</b>\n\n"
            f"📂 <b>Repo:</b> {html.escape(repo_name or '')}\n"
            f"👤 <b>Yapan:</b> {html.escape(pusher or '')}\n"
            f"📝 <b>Mesaj:</b> {html.escape(msg)}\n\n"
            f"🔗 <a href=\"{html.escape(url)}\">Detayları Gör</a>")


def send_message(text):
    """Telegram'a gönderir; hata olursa loglar, webhook'u düşürmez."""
    try:
        response = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                                 json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"},
                                 timeout=TELEGRAM_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as error:
        # Token URL içinde olduğu için hatanın kendisini değil, türünü yazıyoruz
        app.logger.error("Telegram'a gönderilemedi: %s", type(error).__name__)
        return False
    return True


# --- 1. BEBEK ADIMI: Render ve UptimeRobot için "Ben Hayattayım" Kapısı ---
@app.route('/', methods=['GET'])
def home():
    return "Bot ayakta ve GitHub commit'lerini bekliyor!", 200

# --- GITHUB WEBHOOK KAPISI ---
@app.route('/webhook', methods=['POST'])
def github_webhook():
    if not valid_signature(request.get_data(), request.headers.get("X-Hub-Signature-256")):
        abort(401)

    data = request.get_json(silent=True) or {}

    # Sadece 'push' (commit) olaylarını yakala
    if 'commits' in data:
        repo_name = data.get("repository", {}).get("name")
        pusher = data.get("pusher", {}).get("name")

        for commit in data.get("commits", []):
            send_message(format_commit(repo_name, pusher, commit))

    return "OK", 200

# --- UYGULAMAYI BAŞLATMA ---
if __name__ == '__main__':
    # Render'ın verdiği portu kullan, vermezse 10000 kullan
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
