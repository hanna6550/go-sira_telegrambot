import os
from dotenv import load_dotenv
import telebot

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv('API_KEY')
if not API_KEY:
    raise ValueError("No API key provided. Please set the API_KEY environment variable in the .env file.")

bot = telebot.TeleBot(API_KEY)

# Create directories to save the uploaded files
if not os.path.exists('uploads'):
    os.makedirs('uploads/cv')
    os.makedirs('uploads/coverletter')

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    welcome_message = ("Welcome! Please follow the instructions below to submit your documents:\n\n"
                       "/Start - Hello! Please Upload your Cover Letter and CV (PDF format) to apply.\n "
                       "/coverletter - Upload your cover letter (PDF format).\n"
                       "/cv - Upload your CV (PDF format).\n"
                       "When uploading, please ensure the document has the appropriate caption ('coverletter' or 'cv').")
    bot.reply_to(message, welcome_message)

@bot.message_handler(commands=['start'])
def request_start(message):
    bot.reply_to(message, "Hello! Please Upload your Cover Letter and CV (PDF format) to apply.")

@bot.message_handler(commands=['coverletter'])
def request_coverletter(message):
    bot.reply_to(message, "Please upload your cover letter PDF file and add the caption 'coverletter'.")

@bot.message_handler(commands=['cv'])
def request_cv(message):
    bot.reply_to(message, "Please upload your CV PDF file and add the caption 'cv'.")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    if message.document.mime_type != 'application/pdf':
        bot.reply_to(message, "Please upload a PDF file.")
        return

    file_info = bot.get_file(message.document.file_id)
    file = bot.download_file(file_info.file_path)

    file_name = message.document.file_name
    file_extension = os.path.splitext(file_name)[1]

    if file_extension == '.pdf':
        if message.caption and message.caption.lower() == 'coverletter':
            save_path = os.path.join('uploads', 'coverletter', file_name)
        elif message.caption and message.caption.lower() == 'cv':
            save_path = os.path.join('uploads', 'cv', file_name)
        else:
            bot.reply_to(message, "Please specify whether this is a 'coverletter' or 'cv' in the caption.")
            return

        with open(save_path, 'wb') as f:
            f.write(file)

        bot.reply_to(message, f"Your {message.caption.lower()} has been saved successfully!")
    else:
        bot.reply_to(message, "Please upload a PDF file.")
        
# Delete webhook (if any) and start polling
bot.remove_webhook()
bot.polling()
