import telebot
import os
import yt_dlp
from flask import Flask
from threading import Thread
from supabase import create_client

# الإعدادات
TOKEN = os.environ.get('BOT_TOKEN')
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
CHANNEL_ID = "@your_channel_username" # ضع يوزر قناتك هنا

bot = telebot.TeleBot(TOKEN)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
app = Flask(__name__)

# التحقق من الاشتراك
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# أمر البدء
@bot.message_handler(commands=['start'])
def start(message):
    if is_subscribed(message.from_user.id):
        # تسجيل المستخدم في القاعدة
        try:
            supabase.table("users").insert({"user_id": message.from_user.id, "username": message.from_user.username}).execute()
        except:
            pass
        bot.reply_to(message, "أهلاً بك! أرسل رابط فيديو إنستقرام (Reels) وسأقوم بتحميله لك.")
    else:
        bot.reply_to(message, f"عذراً، يجب عليك الاشتراك في القناة أولاً للوصول للبوت:\n{CHANNEL_ID}")

# استقبال الروابط وتحميلها
@bot.message_handler(func=lambda message: "instagram.com" in message.text)
def handle_link(message):
    if not is_subscribed(message.from_user.id):
        bot.reply_to(message, "يرجى الاشتراك في القناة أولاً لاستخدام البوت.")
        return
    
    bot.reply_to(message, "جاري التحميل... يرجى الانتظار.")
    try:
        # كود التحميل البسيط
        url = message.text
        ydl_opts = {'format': 'best', 'outtmpl': 'video.mp4'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        with open('video.mp4', 'rb') as video:
            bot.send_video(message.chat.id, video)
    except Exception as e:
        bot.reply_to(message, "حدث خطأ أثناء التحميل، تأكد من صحة الرابط.")

# تشغيل البوت والويب سيرفر
@app.route('/')
def home(): return "Bot is running"

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
    bot.polling(none_stop=True)
