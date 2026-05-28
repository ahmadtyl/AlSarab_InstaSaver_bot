import os
import telebot
import yt_dlp
import json
import uuid
from flask import Flask, request
from supabase import create_client
from telebot import types

# الإعدادات
app = Flask(__name__)
supabase = create_client(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_KEY'))

# البوتات
bot_insta = telebot.TeleBot(os.environ.get('BOT_TOKEN_INSTA'))
bot_bac = telebot.TeleBot(os.environ.get('BOT_TOKEN_BAC'))

# --- قسم بوت البكالوريا (الذي أرسلته لي) ---
DATA_FILE = "users_data.json"
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@bot_bac.message_handler(commands=['start', 'help'])
def start_bac(message):
    bot_bac.reply_to(message, "أهلاً بك في بوت البكالوريا 2026. (هذا هو الكود المدمج)")

# --- قسم بوت التحميل (الذي أرسلته لي) ---
@bot_insta.message_handler(func=lambda message: "instagram.com" in message.text)
def handle_insta(message):
    bot_insta.reply_to(message, "📥 جاري التحميل...")
    try:
        filename = f"{uuid.uuid4()}.mp4"
        ydl_opts = {'format': 'best', 'outtmpl': filename, 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([message.text])
        with open(filename, 'rb') as video: bot_insta.send_video(message.chat.id, video)
        os.remove(filename)
    except Exception as e: bot_insta.reply_to(message, f"❌ خطأ: {e}")

# --- الموزع (لا تلمس هذا الجزء) ---
@app.route('/' + os.environ.get('BOT_TOKEN_INSTA'), methods=['POST'])
def web_insta():
    bot_insta.process_new_updates([types.Update.de_json(request.get_data().decode('utf-8'))])
    return "!", 200

@app.route('/' + os.environ.get('BOT_TOKEN_BAC'), methods=['POST'])
def web_bac():
    bot_bac.process_new_updates([types.Update.de_json(request.get_data().decode('utf-8'))])
    return "!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
