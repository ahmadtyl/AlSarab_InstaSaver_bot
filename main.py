import os
import telebot
import yt_dlp
import json
import time
import uuid
from flask import Flask, request
from supabase import create_client
from telebot import types

# --- الإعدادات الأساسية ---
app = Flask(__name__)
supabase = create_client(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_KEY'))

bot_insta = telebot.TeleBot(os.environ.get('BOT_TOKEN_INSTA'))
bot_bac = telebot.TeleBot(os.environ.get('BOT_TOKEN_BAC'))

# --- كود بوت التحميل ---
@bot_insta.message_handler(commands=['start'])
def start_insta(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🚀 ابدأ الآن", callback_data="start_bot"))
    bot_insta.reply_to(message, "أهلاً بك في بوت تحميل الإنستقرام، اضغط للبدء.", reply_markup=markup)

@bot_insta.message_handler(func=lambda message: "instagram.com" in message.text)
def handle_insta_link(message):
    bot_insta.reply_to(message, "📥 جاري التحميل...")
    # هنا كود التحميل البسيط
    try:
        file_id = str(uuid.uuid4())
        filename = f"{file_id}.mp4"
        ydl_opts = {'format': 'best', 'outtmpl': filename, 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([message.text])
        with open(filename, 'rb') as video:
            bot_insta.send_video(message.chat.id, video)
        os.remove(filename)
    except Exception as e:
        bot_insta.reply_to(message, f"❌ خطأ: {str(e)}")

# --- كود بوت البكالوريا ---
@bot_bac.message_handler(commands=['start'])
def start_bac(message):
    bot_bac.reply_to(message, os.environ.get("BOT_DESCRIPTION", "أهلاً بك في بوت البكالوريا 2026"))

@bot_bac.message_handler(func=lambda message: True)
def handle_bac_messages(message):
    # إذا أردت إضافة أوامر البكالوريا القديمة، ضعها هنا لاحقاً
    bot_bac.reply_to(message, "تم استلام رسالتك في بوت البكالوريا.")

# --- نظام الموزع (Webhooks) ---
@app.route('/' + os.environ.get('BOT_TOKEN_INSTA'), methods=['POST'])
def webhook_insta():
    bot_insta.process_new_updates([types.Update.de_json(request.get_data().decode('utf-8'))])
    return "!", 200

@app.route('/' + os.environ.get('BOT_TOKEN_BAC'), methods=['POST'])
def webhook_bac():
    bot_bac.process_new_updates([types.Update.de_json(request.get_data().decode('utf-8'))])
    return "!", 200

@app.route('/')
def home(): return "النظام يعمل!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
