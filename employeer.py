import os
from dotenv import load_dotenv
import telebot

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
pending_job_posts = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_message = ("Welcome, Employer! Please follow the instructions below to register and post jobs:\n\n"
                       "/employee_profile_start - Begin the registration process with Employer profile.\n"
                       "/postjob - Post a job.\n"
                       "/myjob - View and manage your job post.\n")
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
        bot.send_message(chat_id, 'Please enter the job site:')
        employer_steps[chat_id] = 'awaiting_job_site'
    else:
        bot.send_message(chat_id, 'Job description must be at least 50 characters long.')

@bot.message_handler(func=lambda message: employer_steps.get(message.chat.id) == 'awaiting_job_site')
def handle_job_site(message):
    chat_id = message.chat.id
    job_site = message.text.strip()
    job_info[chat_id]['job_site'] = job_site
    bot.send_message(chat_id, 'Please enter the experience level:')
    employer_steps[chat_id] = 'awaiting_experience_level'

@bot.message_handler(func=lambda message: employer_steps.get(message.chat.id) == 'awaiting_experience_level')
def handle_experience_level(message):
    chat_id = message.chat.id
    experience_level = message.text.strip()
    job_info[chat_id]['experience_level'] = experience_level
    bot.send_message(chat_id, 'Please enter the salary/compensation (you can skip by typing "skip"):')
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
    bot.send_message(chat_id, 'Please enter the preferred gender of the applicant:')
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
    pending_job_posts[chat_id] = job_info[chat_id]  # Add job post to pending list
    bot.send_message(chat_id, 'You have successfully submitted your job post. Please wait patiently for approval.')
    employer_steps[chat_id] = None

    # Notify admin
    bot.send_message(ADMIN_CHAT_ID, 
                     f"New job post submitted for approval:\n\n\n"
                     f"Company Name: {job_info[chat_id]['company_name']}\n\n"
                     f"Job Title: {job_info[chat_id]['job_title']}\n\n"
                     f"Vacancy Number: {job_info[chat_id]['vacancy_number']}\n\n"
                     f"Applicant Gender: {job_info[chat_id]['applicant_gender']}\n\n"
                     f"Job Description: {job_info[chat_id]['job_description']}\n\n"
                     f"Job Site: {job_info[chat_id]['job_site']}\n\n"
                     f"Experience Level: {job_info[chat_id]['experience_level']}\n\n"
                     f"Salary: {job_info[chat_id]['salary']}\n\n"
                     f"Working Country and City: {job_info[chat_id]['working_country', 'working_city']}\n\n"
                    #  f"Working City: {job_info[chat_id]['working_city']}\n"
                     f"Job/Application Close Date: {job_info[chat_id]['job_close_date']}\n\n"
                     f"Chat ID: {chat_id}\n"
                     f"/approve_{chat_id} - Approve this job post\n"
                     f"/reject_{chat_id} - Reject this job post")

@bot.message_handler(func=lambda message: message.text.startswith('/approve_'))
def handle_approve(message):
    chat_id = message.chat.id
    if str(chat_id) == ADMIN_CHAT_ID:
        try:
            target_chat_id = int(message.text.split('_')[1])
            if target_chat_id in pending_job_posts:
                job_title = pending_job_posts[target_chat_id]['job_title']
                bot.send_message(target_chat_id, f'Your job "{job_title}" has been approved for posting.')
                # Further action for approval (e.g., adding to database)
                del pending_job_posts[target_chat_id]
                bot.send_message(chat_id, f"Job post for chat ID {target_chat_id} has been approved.")
            else:
                bot.send_message(chat_id, "Invalid chat ID or job post not found.")
        except Exception as e:
            bot.send_message(chat_id, f"Error processing command: {str(e)}")
    else:
        bot.send_message(chat_id, 'You are not authorized to use this command.')

@bot.message_handler(func=lambda message: message.text.startswith('/reject_'))
def handle_reject(message):
    chat_id = message.chat.id
    if str(chat_id) == ADMIN_CHAT_ID:
        try:
            target_chat_id = int(message.text.split('_')[1])
            if target_chat_id in pending_job_posts:
                bot.send_message(target_chat_id, 'Your job post was not approved. Please review and correct the information.')
                # Further action for rejection (e.g., removing from pending list)
                del pending_job_posts[target_chat_id]
                bot.send_message(chat_id, f"Job post for chat ID {target_chat_id} has been rejected.")
            else:
                bot.send_message(chat_id, "Invalid chat ID or job post not found.")
        except Exception as e:
            bot.send_message(chat_id, f"Error processing command: {str(e)}")
    else:
        bot.send_message(chat_id, 'You are not authorized to use this command.')

bot.remove_webhook()
bot.polling()
