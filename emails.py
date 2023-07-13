import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file


FROM=os.environ.get('FROMEMAIL')
TO=os.getenv("TOEMAIL").split(",")
SUBJECT='New Conversation from Virtual Assistant'

def send_out_email(chat_history):
    message = Mail(
        from_email=FROM,
        to_emails=TO,
        subject=SUBJECT,
        html_content=f"You have a new message from SmartBot!! <br><br>{chat_history}"
        )
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)