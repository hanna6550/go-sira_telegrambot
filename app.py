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
                       "When uploading, please ensure the document has the appropriate filename ('firstname_lastname_cv.pdf' or 'firstname_lastname_coverletter.pdf').")
    bot.reply_to(message, welcome_message)
    request_full_name(message)

def request_full_name(message):
    bot.reply_to(message, "Hello! Please enter your full name (first name and last name) to start the application process.")
    user_steps[message.chat.id] = 'awaiting_full_name'

@bot.message_handler(func=lambda message: message.text and message.text.lower() not in ['/start', '/coverletter', '/cv', '/hello'])
def handle_full_name(message):
    if user_steps.get(message.chat.id) == 'awaiting_full_name':
        full_name = message.text.strip()
        if re.match(r'^[a-zA-Z]+ [a-zA-Z]+$', full_name):
            users[message.chat.id] = {'full_name': full_name}
            user_steps[message.chat.id] = 'awaiting_job_title'
            bot.reply_to(message, "Thank you. Please enter your job title.")
        else:
            bot.reply_to(message, "Please enter a valid full name (first name and last name).")
    elif user_steps.get(message.chat.id) == 'awaiting_job_title':
        job_title = message.text.strip()
        users[message.chat.id]['job_title'] = job_title
        user_steps[message.chat.id] = 'awaiting_dob'
        bot.reply_to(message, "Please enter your date of birth (YYYY-MM-DD).")
    elif user_steps.get(message.chat.id) == 'awaiting_dob':
        dob = message.text.strip()
        if re.match(r'^\d{4}-\d{2}-\d{2}$', dob):
            users[message.chat.id]['dob'] = dob
            user_steps[message.chat.id] = 'awaiting_gender'
            bot.reply_to(message, "Please enter your gender (e.g., Male, Female, Other).")
        else:
            bot.reply_to(message, "Please enter a valid date of birth in the format YYYY-MM-DD.")
    elif user_steps.get(message.chat.id) == 'awaiting_gender':
        gender = message.text.strip()
        if gender.lower() in ['male', 'female']:
            users[message.chat.id]['gender'] = gender
            user_steps[message.chat.id] = 'awaiting_residence'
            bot.reply_to(message, "Please enter your residence location.")
        else:
            bot.reply_to(message, "Please enter a valid gender (Male, Female, Other).")
    elif user_steps.get(message.chat.id) == 'awaiting_residence':
        residence = message.text.strip()
        if residence:
            users[message.chat.id]['residence'] = residence
            user_steps[message.chat.id] = 'awaiting_phone'
            bot.reply_to(message, "Please enter your phone number.")
        else:
            bot.reply_to(message, "Please enter a valid residence location.")
    elif user_steps.get(message.chat.id) == 'awaiting_phone':
        phone = message.text.strip()
        if re.match(r'^\+?\d{10,15}$', phone):
            users[message.chat.id]['phone'] = phone
            user_steps[message.chat.id] = 'awaiting_coverletter'
            bot.reply_to(message, f"Thank you. Now, please upload your cover letter (PDF format) with the filename format '{users[message.chat.id]['full_name'].lower().replace(' ', '_')}_coverletter.pdf'.")
        else:
            bot.reply_to(message, "Please enter a valid phone number (10 digits).")

@bot.message_handler(commands=['coverletter'])
def request_coverletter(message):
    if message.chat.id in users:
        bot.reply_to(message, f"Please upload your cover letter PDF file and add the filename format '{users[message.chat.id]['full_name'].lower().replace(' ', '_')}_coverletter.pdf'.")
        user_steps[message.chat.id] = 'awaiting_coverletter'
    else:
        bot.reply_to(message, "Please provide your full name first by sending it as a message.")

@bot.message_handler(commands=['cv'])
def request_cv(message):
    if message.chat.id in users:
        if user_steps.get(message.chat.id) == 'coverletter_uploaded':
            bot.reply_to(message, f"Please upload your CV PDF file and add the filename format '{users[message.chat.id]['full_name'].lower().replace(' ', '_')}_cv.pdf'.")
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

    full_name = users[message.chat.id]['full_name']
    first_name, last_name = full_name.split()

    file_id = message.document.file_id
    file_name = message.document.file_name

    if 'cv' in file_name.lower():
        expected_filename = f"{first_name.lower()}_{last_name.lower()}_cv.pdf"
        if expected_filename in file_name.lower():
            if user_steps.get(message.chat.id) == 'coverletter_uploaded':
                user_files[message.chat.id]['cv'] = file_id
                bot.reply_to(message, "Your CV has been received successfully! Thank you for completing your application.")
                user_steps[message.chat.id] = 'cv_uploaded'

                # Notify the admin with both documents and additional information
                bot.send_message(ADMIN_CHAT_ID, 
                                 f"New application received:\n\n"
                                 f"Full Name: {full_name}\n"
                                 f"Job Title: {users[message.chat.id]['job_title']}\n"
                                 f"Date of Birth: {users[message.chat.id]['dob']}\n"
                                 f"Gender: {users[message.chat.id]['gender']}\n"
                                 f"Residence Location: {users[message.chat.id]['residence']}\n"
                                 f"Phone Number: {users[message.chat.id]['phone']}")
                bot.send_document(ADMIN_CHAT_ID, user_files[message.chat.id]['coverletter'])
                bot.send_document(ADMIN_CHAT_ID, user_files[message.chat.id]['cv'])
            else:
                bot.reply_to(message, "Please upload your cover letter first with the filename format '{first_name.lower()}_{last_name.lower()}_coverletter.pdf'.")
        else:
            bot.reply_to(message, f"Please upload your CV with the filename format '{first_name.lower()}_{last_name.lower()}_cv.pdf'.")
    elif 'coverletter' in file_name.lower():
        expected_filename = f"{first_name.lower()}_{last_name.lower()}_coverletter.pdf"
        if expected_filename in file_name.lower():
            if user_steps.get(message.chat.id) == 'awaiting_coverletter':
                user_files[message.chat.id] = {'coverletter': file_id}
                bot.reply_to(message, f"Your cover letter has been received successfully! Now, please upload your CV (PDF format) with the filename format '{first_name.lower()}_{last_name.lower()}_cv.pdf'.")
                user_steps[message.chat.id] = 'coverletter_uploaded'
            else:
                bot.reply_to(message, f"You have already uploaded your cover letter. Please upload your CV with the filename format '{first_name.lower()}_{last_name.lower()}_cv.pdf'.")
        else:
            bot.reply_to(message, f"Please upload your cover letter with the filename format '{first_name.lower()}_{last_name.lower()}_coverletter.pdf'.")
    else:
        bot.reply_to(message, f"Please specify whether this is a '{first_name.lower()}_{last_name.lower()}_coverletter.pdf' or '{first_name.lower()}_{last_name.lower()}_cv.pdf' in the filename.")

# Delete webhook (if any) and start polling
bot.remove_webhook()
bot.polling()
