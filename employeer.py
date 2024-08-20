import os
from dotenv import load_dotenv
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Load environment variables from .env file
load_dotenv()

EMPLOYER_API_KEY = os.getenv('EMPLOYER_API_KEY')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')
CHANNEL_ID = '@go_sira'  # Replace with the actual channel ID

if not EMPLOYER_API_KEY:
    raise ValueError("No API key provided. Please set the EMPLOYER_API_KEY environment variable in the .env file.")
if not ADMIN_CHAT_ID:
    raise ValueError("No Admin chat ID provided. Please set the ADMIN_CHAT_ID environment variable in the .env file.")

bot = telebot.TeleBot(EMPLOYER_API_KEY)

employer_steps = {}
employer_info = {}
job_info = {}
pending_job_posts = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_message = ("Welcome, Employer! Please follow the instructions below to register and post jobs:\n\n"
                       "/employee_profile_start - Begin the registration process with Employer profile.\n\n"
                       "/postjob - Post a job.\n\n"
                    #    "/myjob - View and manage your job post.\n"
                       )
    bot.reply_to(message, welcome_message)

def request_first_name(message):
    bot.reply_to(message, "Please enter your first name:")
    employer_steps[message.chat.id] = 'awaiting_first_name'

@bot.message_handler(commands=['employee_profile_start'])
def employee_profile_start(message):
    request_first_name(message)

@bot.message_handler(func=lambda message: employer_steps.get(message.chat.id) in [
    'awaiting_first_name', 'awaiting_father_name', 'awaiting_dob'
])
def handle_employer_info(message):
    chat_id = message.chat.id

    if employer_steps.get(chat_id) == 'awaiting_first_name':
        first_name = message.text.strip()
        if first_name:
            bot.send_message(chat_id, "Enter your father's name:")
            employer_info[chat_id] = {'first_name': first_name}
            employer_steps[chat_id] = 'awaiting_father_name'
        else:
            bot.send_message(chat_id, "Please enter a valid first name.")
    
    elif employer_steps.get(chat_id) == 'awaiting_father_name':
        father_name = message.text.strip()
        if father_name:
            bot.send_message(chat_id, "Enter your date of birth or your age:")
            employer_info[chat_id]['father_name'] = father_name
            employer_steps[chat_id] = 'awaiting_dob'
        else:
            bot.send_message(chat_id, "Please enter a valid father's name.")
    
    elif employer_steps.get(chat_id) == 'awaiting_dob':
        dob = message.text.strip()
        if dob:
            bot.send_message(chat_id, f"Registration successful! Hello {employer_info[chat_id]['first_name']}, welcome to Go-Sira.\n"
                                      "/postjob - Post a job.\n"
                                      "/myjob - View and manage your job post.\n")
            employer_info[chat_id]['dob'] = dob
            employer_steps[chat_id] = None
            # Notify admin
            bot.send_message(ADMIN_CHAT_ID, 
                             f"New employer registration:\n\n"
                             f"First Name: {employer_info[chat_id]['first_name']}\n"
                             f"Father's Name: {employer_info[chat_id]['father_name']}\n"
                             f"Date of Birth/Age: {employer_info[chat_id]['dob']}")
        else:
            bot.send_message(chat_id, "Please enter a valid date of birth or age.")

@bot.message_handler(commands=['postjob'])
def postjob(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Please enter the name of your company:')
    employer_steps[chat_id] = 'awaiting_company_name'

@bot.message_handler(func=lambda message: employer_steps.get(message.chat.id) == 'awaiting_company_name')
def handle_company_name(message):
    chat_id = message.chat.id
    company_name = message.text.strip()
    if company_name:
        job_info[chat_id] = {'company_name': company_name}
        bot.send_message(chat_id, 'Please enter a link to your company\'s website (if any):')
        employer_steps[chat_id] = 'awaiting_company_website'
    else:
        bot.send_message(chat_id, 'Please enter a valid company name.')

@bot.message_handler(func=lambda message: employer_steps.get(message.chat.id) == 'awaiting_company_website')
def handle_company_website(message):
    chat_id = message.chat.id
    company_website = message.text.strip()
    job_info[chat_id]['company_website'] = company_website
    bot.send_message(chat_id, 'Please enter the email address of your company (if any):')
    employer_steps[chat_id] = 'awaiting_company_email'

@bot.message_handler(func=lambda message: employer_steps.get(message.chat.id) == 'awaiting_company_email')
def handle_company_email(message):
    chat_id = message.chat.id
    company_email = message.text.strip()
    job_info[chat_id]['company_email'] = company_email
    bot.send_message(chat_id, 'Successfully registered your company. Now, enter the job title:')
    employer_steps[chat_id] = 'awaiting_job_title'

@bot.message_handler(func=lambda message: employer_steps.get(message.chat.id) == 'awaiting_job_title')
def handle_job_title(message):
    chat_id = message.chat.id
    job_title = message.text.strip()
    job_info[chat_id]['job_title'] = job_title
    bot.send_message(chat_id, 'Please enter the job description (minimum 50 characters):')
    employer_steps[chat_id] = 'awaiting_job_description'

@bot.message_handler(func=lambda message: employer_steps.get(message.chat.id) == 'awaiting_job_description')
def handle_job_description(message):
    chat_id = message.chat.id
    job_description = message.text.strip()
    if len(job_description) >= 50:
        job_info[chat_id]['job_description'] = job_description
        bot.send_message(chat_id, 'Please enter the job site (On-site, Remote, Hybrid):')
        employer_steps[chat_id] = 'awaiting_education_qualification'
    else:
        bot.send_message(chat_id, 'Job description must be at least 50 characters long.')

@bot.message_handler(func=lambda message: employer_steps.get(message.chat.id) == 'awaiting_education_qualification')
def handle_education_qualification(message):
    chat_id = message.chat.id
    education_qualification = message.text.strip()
    job_info[chat_id]['education-qualification'] = education_qualification
    bot.send_message(chat_id, 'Please enter the Education qualification (Diploma, Bachelor Degree, Masters Degree, Not Required, other):')
    employer_steps[chat_id] = 'awaiting_job_site'

@bot.message_handler(func=lambda message: employer_steps.get(message.chat.id) == 'awaiting_job_site')
def handle_job_site(message):
    chat_id = message.chat.id
    job_site = message.text.strip()
    job_info[chat_id]['job_site'] = job_site
    bot.send_message(chat_id, 'Please enter the experience level (Beginner, Intermediate, Senior, Expert):')
    employer_steps[chat_id] = 'awaiting_experience_level'

@bot.message_handler(func=lambda message: employer_steps.get(message.chat.id) == 'awaiting_experience_level')
def handle_experience_level(message):
    chat_id = message.chat.id
    experience_level = message.text.strip()
    job_info[chat_id]['experience_level'] = experience_level
    bot.send_message(chat_id, 'Please enter the salary/compensation (Monthly, Fixed(One-time) Negotiable, ):')
    employer_steps[chat_id] = 'awaiting_salary'

@bot.message_handler(func=lambda message: employer_steps.get(message.chat.id) == 'awaiting_salary')
def handle_salary(message):
    chat_id = message.chat.id
    salary = message.text.strip()
    job_info[chat_id]['salary'] = salary
    bot.send_message(chat_id, 'Please enter the working country:')
    employer_steps[chat_id] = 'awaiting_working_country'

@bot.message_handler(func=lambda message: employer_steps.get(message.chat.id) == 'awaiting_working_country')
def handle_working_country(message):
    chat_id = message.chat.id
    working_country = message.text.strip()
    job_info[chat_id]['working_country'] = working_country
    bot.send_message(chat_id, 'Please enter the working city:')
    employer_steps[chat_id] = 'awaiting_working_city'

@bot.message_handler(func=lambda message: employer_steps.get(message.chat.id) == 'awaiting_working_city')
def handle_working_city(message):
    chat_id = message.chat.id
    working_city = message.text.strip()
    job_info[chat_id]['working_city'] = working_city
    bot.send_message(chat_id, 'Please enter the vacancy number:')
    employer_steps[chat_id] = 'awaiting_vacancy_number'

@bot.message_handler(func=lambda message: employer_steps.get(message.chat.id) == 'awaiting_vacancy_number')
def handle_vacancy_number(message):
    chat_id = message.chat.id
    vacancy_number = message.text.strip()
    job_info[chat_id]['vacancy_number'] = vacancy_number
    bot.send_message(chat_id, 'Please enter the preferred gender of the applicant (Female, Male, Both, Any):')
    employer_steps[chat_id] = 'awaiting_applicant_gender'

@bot.message_handler(func=lambda message: employer_steps.get(message.chat.id) == 'awaiting_applicant_gender')
def handle_applicant_gender(message):
    chat_id = message.chat.id
    applicant_gender = message.text.strip()
    job_info[chat_id]['applicant_gender'] = applicant_gender
    bot.send_message(chat_id, 'Please enter the job/application close date (YYYY-MM-DD):')
    employer_steps[chat_id] = 'awaiting_job_close_date'

@bot.message_handler(func=lambda message: employer_steps.get(message.chat.id) == 'awaiting_job_close_date')
def handle_job_close_date(message):
    chat_id = message.chat.id
    job_close_date = message.text.strip()
    job_info[chat_id]['job_close_date'] = job_close_date
    bot.send_message(chat_id, 'Job post received. The admin will review and respond it shortly.')

    send_welcome(message)
    
    employer_steps[chat_id] = None

    pending_job_posts[chat_id] = job_info[chat_id]
    notify_admin_for_approval(chat_id)

def notify_admin_for_approval(chat_id):
    job_details = pending_job_posts[chat_id]
    job_summary = (f"New job post submission:\n\n"
                   f"Company Name: {job_details['company_name']}\n\n"
                   f"Job Title: {job_details['job_title']}\n\n"
                   f"Description: {job_details['job_description']}\n\n"
                   f"Site: {job_details['job_site']}\n\n"
                   f"Education Qualifcaiton: {job_details['education-qualification']}\n\n"
                   f"Experience Level: {job_details['experience_level']}\n\n"
                   f"Salary: {job_details['salary']}\n\n"
                   f"Working Country: {job_details['working_country']}\n\n"
                   f"Working City: {job_details['working_city']}\n\n"
                   f"Vacancy Number: {job_details['vacancy_number']}\n\n"
                   f"Applicant Gender: {job_details['applicant_gender']}\n\n"
                   f"Close Date: {job_details['job_close_date']}\n\n\n"
                   f"Chat ID: {chat_id}\n"
                   "Approve or Reject?")
    
    markup = InlineKeyboardMarkup()
    approve_button = InlineKeyboardButton('Approve', callback_data=f'approve_{chat_id}')
    reject_button = InlineKeyboardButton('Reject', callback_data=f'reject_{chat_id}')
    markup.add(approve_button, reject_button)

    bot.send_message(ADMIN_CHAT_ID, job_summary, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_'))
def approve_job(call):
    chat_id = int(call.data.split('_')[1])
    job_details = pending_job_posts.pop(chat_id, None)

    if job_details:
        post_to_channel(job_details)
        bot.send_message(chat_id, 'Your job post has been approved and posted to the channel.')
        # send_welcome(message)
        bot.send_message(ADMIN_CHAT_ID, f"Job post for chat ID {chat_id} has been approved.")
    else:
        bot.send_message(call.message.chat.id, "No pending job found to approve.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('reject_'))
def reject_job(call):
    chat_id = int(call.data.split('_')[1])
    job_details = pending_job_posts.pop(chat_id, None)

    if job_details:
        bot.send_message(chat_id, 'Your job post has been rejected by the admin. Please review and try again with valid input.')
        # send_welcome(message)
        bot.send_message(ADMIN_CHAT_ID, f"Job post for chat ID {chat_id} has been rejected.")
    else:
        bot.send_message(call.message.chat.id, "No pending job found to reject.")

def post_to_channel(job_details):
    channel_post = (
                    # f"🚨 New Job Posting 🚨\n\n"
                    f"Job Title: {job_details['job_title']}\n\n"
                    f"Company: {job_details['company_name']}\n\n"
                    f"Education Qualifcaiton: {job_details['education-qualification']}\n\n"
                    f"Experience Level: {job_details['experience_level']}\n\n"
                    f"Preferred Gender: {job_details['applicant_gender']}\n\n"
                    f"Location: {job_details['working_country']}, {job_details['working_city']}\n\n"
                    f"Vacancy Number: {job_details['vacancy_number']}\n\n"
                    f"Job Description: {job_details['job_description']}\n\n"
                    f"Salary: {job_details['salary']}\n\n"
                    f"Application Deadline: {job_details['job_close_date']}\n\n"
                    # f"Apply on Bot: @bot1sirabot"
                    )

    markup = InlineKeyboardMarkup()
    apply_button = InlineKeyboardButton("Apply on Bot", url="https://t.me/bot1sirabot")
    markup.add(apply_button)

    bot.send_message(CHANNEL_ID, channel_post, reply_markup=markup)

@bot.message_handler(commands=['myjob'])
def myjob(message):
    chat_id = message.chat.id
    if chat_id in job_info:
        job_details = job_info[chat_id]
        job_summary = (f"Your current job post:\n\n"
                       f"Company Name: {job_details['company_name']}\n"
                       f"Job Title: {job_details['job_title']}\n"
                       f"Description: {job_details['job_description']}\n"
                       f"Site: {job_details['job_site']}\n"
                       f"Experience Level: {job_details['experience_level']}\n"
                       f"Salary: {job_details['salary']}\n"
                       f"Working Country: {job_details['working_country']}\n"
                       f"Working City: {job_details['working_city']}\n"
                       f"Vacancy Number: {job_details['vacancy_number']}\n"
                       f"Applicant Gender: {job_details['applicant_gender']}\n"
                       f"Close Date: {job_details['job_close_date']}")
        bot.send_message(chat_id, job_summary)
    else:
        bot.send_message(chat_id, 'You have no active job posts.')

bot.infinity_polling()
