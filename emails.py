import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file
# from contact import UserData

# my_user = UserData()
# my_user.get_user_info('test1','email1','car1')

FROM=os.environ.get('FROMEMAIL')
TO=os.getenv("TOEMAIL").split(",")
SUBJECT='A new message from the Virtual Assistant!'

def send_out_email(my_user):
    message = Mail(
        from_email=FROM,
        to_emails=TO,
        subject=SUBJECT,
        html_content=f"You have a new message from SmartBot!! <br>Name: {my_user.user_name}<br>Email: {my_user.user_email}<br>Message: {my_user.email_body}"
        )
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)