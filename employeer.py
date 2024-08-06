import os
from dotenv import load_dotenv
import telebot
import re

# Load environment variables from .env file
load_dotenv()

EMPLOYER_API_KEY = os.getenv('EMPLOYER_API_KEY')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

if not EMPLOYER_API_KEY:
    raise ValueError("No API key provided. Please set the EMPLOYER_API_KEY environment variable in the .env file.")
if not ADMIN_CHAT_ID:
    raise ValueError("No Admin chat ID provided. Please set the ADMIN_CHAT_ID environment variable in the .env file.")

bot = telebot.TeleBot(EMPLOYER_API_KEY)

employer_steps = {}
employer_info = {}
job_info = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_message = ("Welcome, Employer! Please follow the instructions below to register and post jobs:\n\n"
                    #    "/start - to start the bot\n"
                       "/employee_profile_start - Begin the registration process with Employer profile.\n"
                       "/postjob - Post a job.\n"
                       "/myjob - View and manage your job post.\n")
    bot.reply_to(message, welcome_message)
    request_first_name(message)

def request_first_name(message):
    bot.reply_to(message, "Please enter your first name:")
    employer_steps[message.chat.id] = 'awaiting_first_name'

@bot.message_handler(commands=['employee_profile_start'])
def employee_profile_start(message):
    request_first_name(message)

@bot.message_handler(func=lambda message: employer_steps.get(message.chat.id) in [
    'awaiting_first_name', 'awaiting_father_name', 'awaiting_dob', 'awaiting_company_name', 
    'awaiting_company_website', 'awaiting_company_email', 'awaiting_job_title', 'awaiting_job_description',
    'awaiting_job_site', 'awaiting_experience_level', 'awaiting_salary', 'awaiting_working_country', 
    'awaiting_working_city', 'awaiting_vacancy_number', 'awaiting_applicant_gender', 'awaiting_job_close_date'
])
def handle_employer_info(message):
    chat_id = message.chat.id

    if employer_steps.get(chat_id) == 'awaiting_first_name':
        first_name = message.text.strip()
        if re.match(r'^[a-zA-Z]+$', first_name):
            bot.send_message(chat_id, "Enter your father's name:")
            employer_info[chat_id] = {'first_name': first_name}
            employer_steps[chat_id] = 'awaiting_father_name'
        else:
            bot.send_message(chat_id, "Please enter a valid first name.")
    
    elif employer_steps.get(chat_id) == 'awaiting_father_name':
        father_name = message.text.strip()
        if re.match(r'^[a-zA-Z]+$', father_name):
            bot.send_message(chat_id, "Enter your date of birth or your age:")
            employer_info[chat_id]['father_name'] = father_name
            employer_steps[chat_id] = 'awaiting_dob'
        else:
            bot.send_message(chat_id, "Please enter a valid father's name.")
    
    elif employer_steps.get(chat_id) == 'awaiting_dob':
        dob = message.text.strip()
        if re.match(r'^\d{4}-\d{2}-\d{2}$', dob) or dob.isdigit():
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
            bot.send_message(chat_id, "Please enter a valid date of birth (YYYY-MM-DD) or age (number).")

@bot.message_handler(commands=['postjob'])
def postjob(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Please enter the name of your company:')
    employer_steps[chat_id] = 'awaiting_company_name'

@bot.message_handler(func=lambda message: employer_steps.get(message.chat.id) in [
    'awaiting_company_name', 'awaiting_company_website', 'awaiting_company_email', 'awaiting_job_title', 
    'awaiting_job_description', 'awaiting_job_site', 'awaiting_experience_level', 'awaiting_salary', 
    'awaiting_working_country', 'awaiting_working_city', 'awaiting_vacancy_number', 'awaiting_applicant_gender', 
    'awaiting_job_close_date'
])
def handle_job_info(message):
    chat_id = message.chat.id

    if employer_steps.get(chat_id) == 'awaiting_company_name':
        company_name = message.text.strip()
        bot.send_message(chat_id, 'Received company name: ' + company_name)  # Debugging message
        if company_name:
            bot.send_message(chat_id, 'Please enter a link to your company\'s website (if any):')
            employer_steps[chat_id] = 'awaiting_company_website'
            job_info[chat_id] = {'company_name': company_name}
        else:
            bot.send_message(chat_id, 'Please enter a valid company name.')
    
    elif employer_steps.get(chat_id) == 'awaiting_company_website':
        company_website = message.text.strip()
        bot.send_message(chat_id, 'Received company website: ' + company_website)  # Debugging message
        bot.send_message(chat_id, 'Please enter the email address of your company (if any):')
        employer_steps[chat_id] = 'awaiting_company_email'
        job_info[chat_id]['company_website'] = company_website
    
    elif employer_steps.get(chat_id) == 'awaiting_company_email':
        company_email = message.text.strip()
        bot.send_message(chat_id, 'Received company email: ' + company_email)  # Debugging message
        bot.send_message(chat_id, 'Successfully registered your company. Now, enter the job title:')
        employer_steps[chat_id] = 'awaiting_job_title'
        job_info[chat_id]['company_email'] = company_email
    
    elif employer_steps.get(chat_id) == 'awaiting_job_title':
        job_title = message.text.strip()
        bot.send_message(chat_id, 'Received job title: ' + job_title)  # Debugging message
        bot.send_message(chat_id, 'Please enter the job description (minimum 50 characters):')
        employer_steps[chat_id] = 'awaiting_job_description'
        job_info[chat_id]['job_title'] = job_title
    
    elif employer_steps.get(chat_id) == 'awaiting_job_description':
        job_description = message.text.strip()
        bot.send_message(chat_id, 'Received job description: ' + job_description)  # Debugging message
        if len(job_description) >= 50:
            bot.send_message(chat_id, 'Please enter the job site:')
            employer_steps[chat_id] = 'awaiting_job_site'
            job_info[chat_id]['job_description'] = job_description
        else:
            bot.send_message(chat_id, 'Job description must be at least 50 characters long.')
    
    elif employer_steps.get(chat_id) == 'awaiting_job_site':
        job_site = message.text.strip()
        bot.send_message(chat_id, 'Received job site: ' + job_site)  # Debugging message
        bot.send_message(chat_id, 'Please enter the experience level:')
        employer_steps[chat_id] = 'awaiting_experience_level'
        job_info[chat_id]['job_site'] = job_site
    
    elif employer_steps.get(chat_id) == 'awaiting_experience_level':
        experience_level = message.text.strip()
        bot.send_message(chat_id, 'Received experience level: ' + experience_level)  # Debugging message
        bot.send_message(chat_id, 'Please enter the salary/compensation (you can skip by typing "skip"):')
        employer_steps[chat_id] = 'awaiting_salary'
        job_info[chat_id]['experience_level'] = experience_level
    
    elif employer_steps.get(chat_id) == 'awaiting_salary':
        salary = message.text.strip()
        bot.send_message(chat_id, 'Received salary: ' + salary)  # Debugging message
        bot.send_message(chat_id, 'Please enter the working country:')
        employer_steps[chat_id] = 'awaiting_working_country'
        job_info[chat_id]['salary'] = salary
    
    elif employer_steps.get(chat_id) == 'awaiting_working_country':
        working_country = message.text.strip()
        bot.send_message(chat_id, 'Received working country: ' + working_country)  # Debugging message
        bot.send_message(chat_id, 'Please enter the working city:')
        employer_steps[chat_id] = 'awaiting_working_city'
        job_info[chat_id]['working_country'] = working_country
    
    elif employer_steps.get(chat_id) == 'awaiting_working_city':
        working_city = message.text.strip()
        bot.send_message(chat_id, 'Received working city: ' + working_city)  # Debugging message
        bot.send_message(chat_id, 'Please enter the vacancy number:')
        employer_steps[chat_id] = 'awaiting_vacancy_number'
        job_info[chat_id]['working_city'] = working_city
    
    elif employer_steps.get(chat_id) == 'awaiting_vacancy_number':
        vacancy_number = message.text.strip()
        bot.send_message(chat_id, 'Received vacancy number: ' + vacancy_number)  # Debugging message
        bot.send_message(chat_id, 'Please enter the preferred gender of the applicant:')
        employer_steps[chat_id] = 'awaiting_applicant_gender'
        job_info[chat_id]['vacancy_number'] = vacancy_number
    
    elif employer_steps.get(chat_id) == 'awaiting_applicant_gender':
        applicant_gender = message.text.strip()
        bot.send_message(chat_id, 'Received applicant gender: ' + applicant_gender)  # Debugging message
        bot.send_message(chat_id, 'Please enter the job/application close date (YYYY-MM-DD):')
        employer_steps[chat_id] = 'awaiting_job_close_date'
        job_info[chat_id]['applicant_gender'] = applicant_gender
    
    elif employer_steps.get(chat_id) == 'awaiting_job_close_date':
        job_close_date = message.text.strip()
        bot.send_message(chat_id, 'Received job close date: ' + job_close_date)  # Debugging message
        job_info[chat_id]['job_close_date'] = job_close_date
        bot.send_message(chat_id, 'You have successfully submitted your job post. Please wait patiently until our approval.')
        employer_steps[chat_id] = None
        # Notify admin
        bot.send_message(ADMIN_CHAT_ID, 
                         f"New job post submitted for approval:\n\n"
                         f"Company Name: {job_info[chat_id]['company_name']}\n"
                         f"Job Title: {job_info[chat_id]['job_title']}\n"
                         f"Job Description: {job_info[chat_id]['job_description']}\n"
                         f"Job Site: {job_info[chat_id]['job_site']}\n"
                         f"Experience Level: {job_info[chat_id]['experience_level']}\n"
                         f"Salary: {job_info[chat_id]['salary']}\n"
                         f"Working Country: {job_info[chat_id]['working_country']}\n"
                         f"Working City: {job_info[chat_id]['working_city']}\n"
                         f"Vacancy Number: {job_info[chat_id]['vacancy_number']}\n"
                         f"Applicant Gender: {job_info[chat_id]['applicant_gender']}\n"
                         f"Job/Application Close Date: {job_info[chat_id]['job_close_date']}")

bot.remove_webhook()
bot.polling()
