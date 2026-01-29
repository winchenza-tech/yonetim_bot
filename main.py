import os
import logging
import asyncio
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

# --- FLASK AYARLARI (Render için gerekli) ---
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot aktif ve calisiyor!"

def run_flask():
    # Render genellikle PORT environment variable'ını otomatik atar
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# --- BOT AYARLARI ---

# Token ve ID'leri Environment Variable'dan çekiyoruz
TOKEN = os.getenv("TELEGRAM_TOKEN")
TARGET_GROUP_ID = os.getenv("TARGET_GROUP_ID") 

# Loglama
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

async def copy_channel_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Kanaldan gelen mesajı yakalar ve hedefe kopyalar.
    """
    try:
        # Eğer hedef grup ID'si girilmemişse işlem yapma
        if not TARGET_GROUP_ID:
            print("HATA: Hedef Grup ID (TARGET_GROUP_ID) ayarlanmamış!")
            return

        chat_id = update.effective_chat.id
        message_id = update.effective_message.id
        
        print(f"Kanaldan mesaj geldi: {message_id}")

        # Mesajı kopyala (İletildi etiketi olmadan)
        await context.bot.copy_message(
            chat_id=int(TARGET_GROUP_ID), # Env'den string gelir, int'e çevirdik
            from_chat_id=chat_id,
            message_id=message_id
        )
        print("Mesaj başarıyla kopyalandı.")

    except Exception as e:
        print(f"Kopyalama hatası: {e}")

def main():
    # Token kontrolü
    if not TOKEN:
        print("HATA: TELEGRAM_TOKEN bulunamadı!")
        return

    # Application oluştur
    application = Application.builder().token(TOKEN).build()

    # Sadece KANAL mesajlarını dinle
    handler = MessageHandler(filters.ChatType.CHANNEL, copy_channel_message)
    application.add_handler(handler)

    # Botu başlat
    print("Bot polling başlatılıyor...")
    application.run_polling()

if __name__ == "__main__":
    # Flask'ı ayrı bir thread'de başlat (Render health check için)
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    
    # Botu ana thread'de başlat
    main()