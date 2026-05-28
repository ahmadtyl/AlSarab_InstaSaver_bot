import os
import telebot
from flask import Flask, request
from supabase import create_client
from telebot import types

# 1. الاتصال بقاعدة البيانات
supabase = create_client(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_KEY'))

# 2. إنشاء "نسختين" من البوت
bot_insta = telebot.TeleBot(os.environ.get('BOT_TOKEN_INSTA'))
bot_bac = telebot.TeleBot(os.environ.get('BOT_TOKEN_BAC'))

# 3. نظام التوزيع (الموزع الذي يقرأ التوكنات)
app = Flask(__name__)

@app.route('/' + os.environ.get('BOT_TOKEN_INSTA'), methods=['POST'])
def webhook_insta():
    bot_insta.process_new_updates([types.Update.de_json(request.get_data().decode('utf-8'))])
    return "!", 200

@app.route('/' + os.environ.get('BOT_TOKEN_BAC'), methods=['POST'])
def webhook_bac():
    bot_bac.process_new_updates([types.Update.de_json(request.get_data().decode('utf-8'))])
    return "!", 200

@app.route('/')
def home():
    return "نظام البوتات يعمل!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
