import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import google.generativeai as genai
from dotenv import load_dotenv

# Keys load karna
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini AI Setup
genai.configure(api_key=GEMINI_API_KEY)

# 🛑 FINAL FIX: Model ko 'gemini-pro' kar diya hai jo hamesha chalega!
model = genai.GenerativeModel('gemini-pro') 

# Bot Setup (Multi-threading on for fast processing)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=True, num_threads=20)
bot_info = bot.get_me()
bot_username = bot_info.username

def get_gemini_reply(user_text):
    try:
        # Safety filters ko off kar rahe hain taaki API faltu mein block na kare
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        response = model.generate_content(user_text, safety_settings=safety_settings)
        return response.text

    except Exception as e:
        # Ab error aayega toh seedha chat mein dikhega
        return f"System Error: {e}"

# ✨ Start Command with Colored Emojis Buttons
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_name = message.from_user.first_name
    
    welcome_text = (
        f"👋 Hello *{user_name}*!\n\n"
        f"Main ek Superfast AI Chat Bot hoon. ⚡\n\n"
        f"Aap mujhse private chat mein kuch bhi pooch sakte hain, ya group mein mujhe mention (`@{bot_username}`) karke baat kar sakte hain!\n\n"
        f"Niche diye gaye buttons se humare channels join karein 👇"
    )
    
    markup = InlineKeyboardMarkup()
    # Yahan apne asli links daal dijiyega baad mein
    support_url = "https://t.me/ApnaSupportUsername"
    update_url = "https://t.me/ApnaUpdateChannel"
    
    btn_support = InlineKeyboardButton("🔵 Support", url=support_url)
    btn_update = InlineKeyboardButton("🟢 Updates", url=update_url)
    
    markup.row(btn_support, btn_update)
    bot.reply_to(message, welcome_text, reply_markup=markup, parse_mode="Markdown")

# 1. Private Chat Handler
@bot.message_handler(func=lambda message: message.chat.type == 'private')
def handle_private_message(message):
    if message.text.startswith('/'):
        return
        
    bot.send_chat_action(message.chat.id, 'typing')
    reply = get_gemini_reply(message.text)
    bot.reply_to(message, reply)

# 2. Group Chat Handler
@bot.message_handler(func=lambda message: message.chat.type in ['group', 'supergroup'])
def handle_group_message(message):
    user_text = message.text
    if not user_text:
        return

    is_reply_to_bot = message.reply_to_message and message.reply_to_message.from_user.id == bot_info.id
    is_mentioned = f"@{bot_username}" in user_text

    if is_reply_to_bot or is_mentioned:
        clean_text = user_text.replace(f"@{bot_username}", "").strip()
        
        if clean_text:
            bot.send_chat_action(message.chat.id, 'typing')
            reply = get_gemini_reply(clean_text)
            bot.reply_to(message, reply)

print(f"🚀 Bot @{bot_username} Gemini-Pro ke sath start ho gaya hai!")
bot.infinity_polling(timeout=10, long_polling_timeout=5)
