import telebot
import os
import yt_dlp
from flask import Flask
from threading import Thread
from supabase import create_client
from telebot import types

# الإعدادات - يتم سحبها من المتغيرات في Render
TOKEN = os.environ.get('BOT_TOKEN')
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
CHANNEL_ID = os.environ.get('CHANNEL_ID')
CHANNEL_URL = os.environ.get('CHANNEL_URL')
ADMIN_ID = 8469650487 

bot = telebot.TeleBot(TOKEN)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
app = Flask(__name__)

# --- التحقق من الاشتراك ---
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

# --- أوامر الأدمين ---
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        users = supabase.table("users").select("*").execute()
        count = len(users.data)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 إرسال إذاعة", callback_data="broadcast"))
        bot.reply_to(message, f"🛠 أهلاً أدمين، عدد المشتركين في القاعدة: {count}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "broadcast")
def start_broadcast(call):
    msg = bot.send_message(call.message.chat.id, "أرسل الرسالة التي تريد إذاعتها لجميع المشتركين:")
    bot.register_next_step_handler(msg, perform_broadcast)

def perform_broadcast(message):
    users = supabase.table("users").select("user_id").execute()
    count = 0
    for user in users.data:
        try: 
            bot.send_message(user['user_id'], message.text)
            count += 1
        except: pass
    bot.reply_to(message, f"✅ تم إرسال الإذاعة بنجاح إلى {count} مستخدم.")

# --- الأوامر العامة والأزرار ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 اشترك بالقناة", url=CHANNEL_URL))
    markup.add(types.InlineKeyboardButton("👨‍💻 تواصل مع المطور", url="https://t.me/trweeed"))
    
    if message.text == '/start':
        try: supabase.table("users").insert({"user_id": message.from_user.id, "username": message.from_user.username}).execute()
        except: pass
        bot.reply_to(message, "أهلاً بك! أرسل رابط فيديو إنستقرام (Reels) وسأقوم بتحميله لك.", reply_markup=markup)
    else:
        bot.reply_to(message, "طريقة الاستخدام:\n1. اشترك في القناة.\n2. أرسل رابط الفيديو مباشرة وسأقوم بتحميله.", reply_markup=markup)

# --- معالجة الروابط ---
@bot.message_handler(func=lambda message: "instagram.com" in message.text)
def handle_link(message):
    if not is_subscribed(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 اشترك بالقناة الآن", url=CHANNEL_URL))
        bot.reply_to(message, "⚠️ يجب الاشتراك في القناة أولاً لتتمكن من التحميل!\n\nاضغط على الزر بالأسفل للاشتراك:", reply_markup=markup)
        return
    
    bot.reply_to(message, "📥 جاري التحميل، انتظر قليلاً...")
    try:
        ydl_opts = {'format': 'best', 'outtmpl': 'video.mp4'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([message.text])
        with open('video.mp4', 'rb') as video:
            bot.send_video(message.chat.id, video)
    except: 
        bot.reply_to(message, "❌ حدث خطأ أثناء التحميل، تأكد من صحة الرابط.")

@app.route('/')
def home(): return "Bot is Active"

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
    bot.infinity_polling(none_stop=True)
