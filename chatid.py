import telebot
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv('API_KEY')
if not API_KEY:
    raise ValueError("No API key provided. Please set the API_KEY environment variable in the .env file.")

bot = telebot.TeleBot(API_KEY)

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, f"Hello! Your chat ID is {message.chat.id}")

# Start polling
bot.polling()