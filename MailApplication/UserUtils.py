import pymysql as pymysql
from flask_mysqldb import MySQL
import datetime
from passlib.hash import sha256_crypt
import string
import random
import smtplib
import ssl
import mysql.connector
from MailUtils import MailUtils

PORT = 465  # For SSL
SMTP_GMAIL_SERVER = "smtp.gmail.com"


class UserUtils:
    def __init__(self, app):
        self.server = None
        self.mail = MailUtils(user=self)
        self.first_name = None
        self.last_name = None
        self.gender = None
        self.email = None
        self.password = None
        self.user_usage = None
        self.phone_number = None
        self.date_of_birth = None
        self.joined_on = datetime.datetime.now()
        self.app = app
        self.app.config['MYSQL_HOST'] = 'localhost'
        self.app.config['MYSQL_USER'] = 'root'
        self.app.config['MYSQL_PASSWORD'] = ''
        self.app.config['MYSQL_DB'] = 'pp_mail'
        self.app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
        self.user_id = None
        self.mysql = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="SaiChand449@",
            database='pp_mail',
            charset='utf8mb4'
        )

    def set_user_id(self, user_id):
        self.user_id = user_id

    def get_user_email(self):
        return self.email

    def set_user_email(self, email):
        self.email = email

    def check_user_exists(self):
        cursor = self.mysql.cursor(dictionary=True)
        cursor.execute("SELECT user_id, password, is_authenticated FROM users where email = %s", (self.email,))
        data = cursor.fetchall()
        cursor.close()
        result = {'user': data}
        if data == ():
            result['user_exists'] = False
            return result
        result['user_exists'] = True
        return result

    def login_user(self, email, password):
        self.email = email
        user = self.check_user_exists()
        user_details = {}
        for details in user['user']:
            user_details = details
        result = {'valid': False}
        if user_details.get('user_id') is not None:
            if sha256_crypt.verify(password, user_details.get('password')):
                if user_details.get('is_authenticated') == 1:
                    self.login_user_smtp(password=password, sender_mail=self.email, receiver_mail=self.email,
                                         message="Account logged in succesfully", subject="Account Log in Notification")
                result['user_id'] = user_details.get('user_id')
                cursor = self.mysql.cursor(dictionary=True)
                cursor.execute(
                    "UPDATE users SET active = true WHERE email=%s", (self.email,))
                self.mysql.commit()
                cursor.close()
                result['valid'] = True
        return result

    def login_user_smtp(self, password, sender_mail, receiver_mail, message, subject):
        context = ssl.create_default_context()
        self.server = smtplib.SMTP_SSL(SMTP_GMAIL_SERVER, PORT, context=context)
        self.server.login(self.email, password)
        msg = 'Subject: {}\n\n{}'.format(subject, message)
        self.server.sendmail(self.email, self.email, msg)

    def change_user_password(self, password):
        self.password = sha256_crypt.encrypt(password)
        cursor = self.mysql.cursor(dictionary=True)
        cursor.execute("Update users SET password = %s, is_authenticated=true WHERE user_id=%s",
                       (self.password, self.user_id))
        self.mysql.commit()
        cursor.close()
        return "Password changed Successfully."

    def get_user_details(self, user_id):
        cursor = self.mysql.cursor(dictionary=True)
        cursor.execute(
            "SELECT users.first_name, users.is_authenticated, users.last_name, users.gender, users.email, users.user_usage, users.phone_number, users.user_id, users.active, users.joined_on, users.profile_picture, user_mails_info.inbox_count, user_mails_info.draft_count, user_mails_info.sent_count, user_mails_info.junk_count from users  INNER JOIN user_mails_info ON users.user_id=user_mails_info.user_id AND users.user_id=%s", (user_id,))
        data = cursor.fetchall()
        cursor.close()
        user_details = {}
        for user in data:
            user_details = user
        user_details['inbox_count'] = self.mail.get_user_inbox_all(receiver_id=user_id)[0]['mails']
        return user_details

    def logout_user(self, user_id):
        cursor = self.mysql.cursor(dictionary=True)
        cursor.execute("UPDATE users SET active=0 WHERE user_id=%s", (user_id,))
        self.mysql.commit()
        cursor.close()
        return True

    def register_user(self, first_name, last_name, gender, date_of_birth, email, password, user_usage, phone_number):
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender
        self.date_of_birth = date_of_birth
        self.email = email
        self.password = sha256_crypt.encrypt(password)
        self.phone_number = phone_number
        self.user_usage = user_usage
        self.user_id = "".join([random.choice(string.ascii_letters + string.digits) for n in range(30)])
        if not self.check_user_exists()['user_exists']:
            cursor = self.mysql.cursor(dictionary=True)
            cursor.execute("INSERT INTO users(user_id,first_name,last_name,gender,date_of_birth,email,password,phone_number,user_usage,joined_on) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                           (self.user_id, self.first_name, self.last_name, self.gender, self.date_of_birth, self.email,
                            self.password, self.phone_number, self.user_usage,
                            self.joined_on))
            self.mysql.commit()
            cursor.close()
            self.create_user_mail_info()
            return True
        return False

    def get_user_server(self):
        return self.server

    def create_user_mail_info(self):
        cursor = self.mysql.cursor(dictionary=True)
        cursor.execute(
            "INSERT INTO user_mails_info(user_id) VALUES (%s)",
            (self.user_id,))
        self.mysql.commit()
        cursor.close()

    def get_user_mails(self, user_id, start, per_page):
        cursor = self.mysql.cursor(dictionary=True)
        cursor.execute("SELECT * FROM mails_info INNER JOIN pp_mails ON pp_mails.mail_info_id = mails_info.mail_info_id INNER JOIN users ON users.user_id = pp_mails.sender_id WHERE pp_mails.receiver_id =%s LIMIT %s, %s ",
                       (user_id, start, per_page,))
        data = cursor.fetchall()
        cursor.close()
        data = list(data)
        data.reverse()
        return data
