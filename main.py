import telebot
import os
import yt_dlp
import flask
import uuid
from flask import Flask, request
from supabase import create_client
from telebot import types

# الإعدادات
TOKEN = os.environ.get('BOT_TOKEN')
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
CHANNEL_ID = os.environ.get('CHANNEL_ID')
CHANNEL_URL = os.environ.get('CHANNEL_URL')
ADMIN_ID = 8469650487 

bot = telebot.TeleBot(TOKEN)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
app = Flask(__name__)

# --- وظائف مساعدة ---
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

def register_user(message):
    try:
        supabase.table("users").upsert({
            "user_id": message.from_user.id, 
            "username": message.from_user.username or "none"
        }).execute()
    except Exception as e:
        print(f"DEBUG: خطأ في التسجيل: {e}")

# --- الأوامر الأساسية ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    register_user(message)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🚀 ابدأ الآن", callback_data="start_bot"))
    
    welcome_text = (
        f"👋 أهلاً بك يا {message.from_user.first_name} في بوت:\n\n"
        "✨ **Al-sarab | السراب** ✨\n\n"
        "بوت متخصص في تحميل فيديوهات والريلز من إنستقرام بجودة عالية وسرعة فائقة.\n\n"
        "اضغط على الزر أدناه للبدء."
    )
    bot.reply_to(message, welcome_text, reply_markup=markup, parse_mode="Markdown")

# --- معالجة الأزرار ---
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    bot.answer_callback_query(call.id)
    if call.data == "start_bot":
        show_subscription_menu(call.message)
    elif call.data == "check_sub":
        if is_subscribed(call.from_user.id):
            bot.send_message(call.message.chat.id, "✅ **أنت مشترك بالفعل!**\nأرسل رابط الفيديو الآن للتحميل.")
        else:
            show_subscription_menu(call.message, "⚠️ **عذراً، لم تشترك بعد.**\nاشترك في القناة ثم اضغط على التحقق.")
    elif call.data == "count_users":
        try:
            users_data = supabase.table("users").select("user_id").execute()
            count = len(users_data.data)
            bot.send_message(call.message.chat.id, f"📊 عدد المشتركين في البوت: {count}")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"خطأ في الوصول للقاعدة: {e}")
    elif call.data == "broadcast":
        msg = bot.send_message(call.message.chat.id, "أرسل رسالة الإذاعة:")
        bot.register_next_step_handler(msg, perform_broadcast)

def show_subscription_menu(message, text="للاستمرار، يرجى الاشتراك في القناة أولاً:"):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 اشترك في القناة", url=CHANNEL_URL))
    markup.add(types.InlineKeyboardButton("🔄 التحقق من الاشتراك", callback_data="check_sub"))
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

# --- تحميل الفيديو ---
@bot.message_handler(func=lambda message: "instagram.com" in message.text)
def handle_link(message):
    if not is_subscribed(message.from_user.id):
        show_subscription_menu(message, "⚠️ **يجب الاشتراك في القناة أولاً لتتمكن من التحميل!**")
        return
    
    bot.reply_to(message, "📥 **جاري المعالجة...**")
    
    file_id = str(uuid.uuid4())
    filename = f"{file_id}.mp4"
    
    try:
        ydl_opts = {
            'format': 'best', 
            'outtmpl': filename, 
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([message.text])
        
        with open(filename, 'rb') as video:
            bot.send_video(message.chat.id, video)
            
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ أثناء التحميل: {str(e)}")
    
    finally:
        if os.path.exists(filename):
            os.remove(filename)

# --- الإدارة ---
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📊 الإحصائيات", callback_data="count_users"))
        markup.add(types.InlineKeyboardButton("📢 إذاعة", callback_data="broadcast"))
        bot.reply_to(message, "🛠 **لوحة التحكم**", reply_markup=markup)

def perform_broadcast(message):
    users = supabase.table("users").select("user_id").execute().data
    count = 0
    for user in users:
        try: 
            bot.send_message(user['user_id'], message.text)
            count += 1
        except: pass
    bot.reply_to(message, f"✅ تم الإرسال لـ {count} مستخدم.")

# --- Webhook & Flask ---
@app.route('/')
def home(): return "Bot is Active"

@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url="https://alsarabinstasaver.onrender.com/" + TOKEN)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
