class UserData:
    def __init__(self):
        self.user_name = ""
        self.user_email = ""
        self.email_body = ""

    def get_user_info(self, user_name="", user_email="", email_body=""):
        if user_name:
            self.user_name = user_name
        if user_email:
            self.user_email = user_email
        if email_body:
            self.email_body = email_body

        self.print_user_info()

    def get_data(self):
        return {
            "user_name": self.user_name,
            "user_email": self.user_email,
            "email_body": self.email_body
        }
    
    def print_user_info(self):
        print("Name:", self.user_name)
        print("Email:", self.user_email)
        print("Message:", self.email_body)
