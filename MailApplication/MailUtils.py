import UserUtils as user_utils
from email.mime.text import MIMEText


class MailUtils:
    def __init__(self, user):
        self.sender = None
        self.port = user_utils.PORT
        self.smtp_server = user_utils.SMTP_GMAIL_SERVER
        self.user = user

    def send_mail(self, sender_mail, receiver_mail, mail_content, mail_subject):
        self.sender = sender_mail
        my_email = MIMEText(mail_content, "html")
        my_email["From"] = self.sender
        my_email["To"] = receiver_mail
        my_email["Subject"] = mail_subject
        self.user.server.sendmail(self.sender, receiver_mail, my_email.as_string())
        return True
