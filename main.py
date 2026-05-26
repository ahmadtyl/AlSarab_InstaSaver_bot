import telebot
from flask import Flask
from threading import Thread
import os

# 1. الإعدادات الأساسية
TOKEN = os.environ.get('BOT_TOKEN') # سنضع التوكين في Render لاحقاً
CHANNEL_ID = "@your_channel_username" # ضع يوزر قناتك هنا
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 2. إعداد UptimeRobot (نقطة الاتصال)
@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

# 3. دالة التحقق من الاشتراك
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        # الحالات التي تعني أن المستخدم مشترك
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# 4. أوامر البوت
@bot.message_handler(commands=['start'])
def start(message):
    if is_subscribed(message.from_user.id):
        bot.reply_to(message, "أهلاً بك في Al-Sarab | InstaSaver!\nأرسل رابط فيديو إنستقرام للبدء.")
    else:
        bot.reply_to(message, f"عذراً، يجب عليك الاشتراك في قناتنا أولاً لاستخدام البوت:\n{CHANNEL_ID}")

# 5. تشغيل البوت مع الويب سيرفر
if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.polling(none_stop=True)
