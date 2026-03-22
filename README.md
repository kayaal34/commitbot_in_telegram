# 🚀 GitHub-Telegram Notification Bot

Bu proje, belirlenen GitHub depolarında (repository) gerçekleşen her **commit** ve **push** olayını anında bir **Telegram Botu** aracılığıyla kullanıcıya bildiren hafif (lightweight) bir Webhook servisidir.

## ✨ Özellikler
* **Anlık Bildirim:** GitHub Webhook'ları sayesinde saniyeler içinde bildirim gönderir.
* **Çoklu Proje Desteği:** Tek bir bot üzerinden sınırsız sayıda depoyu takip edebilir.
* **Güvenli Yapı:** API Token ve Chat ID gibi hassas bilgiler `Environment Variables` (Ortam Değişkenleri) üzerinden yönetilir.
* **Detaylı Mesaj İçeriği:** Bildirim; repo adı, commit mesajı, push yapan kullanıcı ve commit detayına giden doğrudan bağlantıyı içerir.

## 🛠 Kullanılan Teknolojiler
* **Python 3.x**
* **Flask** (Web Framework)
* **Gunicorn** (WSGI HTTP Server)
* **Requests** (HTTP Library)
* **GitHub Webhooks API**
* **Telegram Bot API**

## 🚀 Kurulum ve Dağıtım

### 1. Yerel Kurulum
1. Projeyi klonlayın: `git clone https://github.com/kayaal34/github-telegram-bot.git`
2. Gereksinimleri yükleyin: `pip install -r requirements.txt`
3. `.env` dosyası oluşturun ve bilgilerinizi girin:
   ```env
   TELEGRAM_TOKEN=your_bot_token
   TELEGRAM_CHAT_ID=your_chat_id