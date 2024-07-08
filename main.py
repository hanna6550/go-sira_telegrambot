import os
from dotenv import load_dotenv
import telebot
import re

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv('API_KEY')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

if not API_KEY:
    raise ValueError("No API key provided. Please set the API_KEY environment variable in the .env file.")
if not ADMIN_CHAT_ID:
    raise ValueError("No Admin chat ID provided. Please set the ADMIN_CHAT_ID environment variable in the .env file.")

bot = telebot.TeleBot(API_KEY)

users = {}
user_steps = {}
user_files = {}

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    welcome_message = ("Welcome! Please follow the instructions below to submit your documents:\n\n"
                       "/start - Begin the application process.\n"
                       "/coverletter - Upload your cover letter (PDF format).\n"
                       "/cv - Upload your CV (PDF format).\n"
                       "When uploading, please ensure the document has the appropriate caption ('coverletter' or 'cv').")
    bot.reply_to(message, welcome_message)
    request_full_name(message)

def request_full_name(message):
    bot.reply_to(message, "Hello! Please enter your full name (first name and last name) to start the application process.")

@bot.message_handler(func=lambda message: message.text and message.text.lower() not in ['/start', '/coverletter', '/cv', '/hello'])
def handle_full_name(message):
    full_name = message.text.strip()
    if re.match(r'^[a-zA-Z]+ [a-zA-Z]+$', full_name):
        users[message.chat.id] = full_name
        user_steps[message.chat.id] = 'awaiting_coverletter'
        bot.reply_to(message, f"Thank you, {full_name}. Now, please upload your cover letter (PDF format) with the caption 'coverletter'.")
    else:
        bot.reply_to(message, "Please enter a valid full name (first name and last name).")

@bot.message_handler(commands=['coverletter'])
def request_coverletter(message):
    if message.chat.id in users:
        bot.reply_to(message, "Please upload your cover letter PDF file and add the caption 'coverletter'.")
        user_steps[message.chat.id] = 'awaiting_coverletter'
    else:
        bot.reply_to(message, "Please provide your full name first by sending it as a message.")

@bot.message_handler(commands=['cv'])
def request_cv(message):
    if message.chat.id in users:
        if user_steps.get(message.chat.id) == 'coverletter_uploaded':
            bot.reply_to(message, "Please upload your CV PDF file and add the caption 'cv'.")
            user_steps[message.chat.id] = 'awaiting_cv'
        else:
            bot.reply_to(message, "Please upload your cover letter first.")
    else:
        bot.reply_to(message, "Please provide your full name first by sending it as a message.")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    if message.document.mime_type != 'application/pdf':
        bot.reply_to(message, "Please upload a PDF file.")
        return

    if message.chat.id not in users:
        bot.reply_to(message, "Please provide your full name first by sending it as a message.")
        return

    file_id = message.document.file_id
    file_name = message.document.file_name

    if message.caption and message.caption.lower() == 'coverletter':
        if user_steps.get(message.chat.id) == 'awaiting_coverletter':
            user_files[message.chat.id] = {'coverletter': file_id}
            bot.reply_to(message, "Your cover letter has been received successfully! Now, please upload your CV (PDF format) with the caption 'cv'.")
            user_steps[message.chat.id] = 'coverletter_uploaded'
        else:
            bot.reply_to(message, "You have already uploaded your cover letter. Please upload your CV with the caption 'cv'.")
    elif message.caption and message.caption.lower() == 'cv':
        if user_steps.get(message.chat.id) == 'coverletter_uploaded':
            user_files[message.chat.id]['cv'] = file_id
            bot.reply_to(message, "Your CV has been received successfully! Thank you for completing your application.")
            user_steps[message.chat.id] = 'cv_uploaded'

            # Notify the admin with both documents
            full_name = users[message.chat.id]
            bot.send_message(ADMIN_CHAT_ID, f"New application received:\n\nFull Name: {full_name}")
            bot.send_document(ADMIN_CHAT_ID, user_files[message.chat.id]['coverletter'])
            bot.send_document(ADMIN_CHAT_ID, user_files[message.chat.id]['cv'])
        else:
            bot.reply_to(message, "Please upload your cover letter first with the caption 'coverletter'.")
    else:
        bot.reply_to(message, "Please specify whether this is a 'coverletter' or 'cv' in the caption.")

# Delete webhook (if any) and start polling
# bot.remove_webhook()
bot.polling()
