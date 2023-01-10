import pymysql

import UserUtils as user_utils
from email.mime.text import MIMEText
import string
import random
from datetime import datetime
import mysql.connector


class MailUtils:
    def __init__(self, user):
        self.receiver_id = None
        self.sender_id = None
        self.mail_sent_date = None
        self.mail_received_date = None
        self.mail_subject = None
        self.mail_junk = None
        self.mail_read = None
        self.mail_flag = None
        self.mail_content = None
        self.mail_info_id = None
        self.mail_id = None
        self.sender = None
        self.port = user_utils.PORT
        self.smtp_server = user_utils.SMTP_GMAIL_SERVER
        self.user = user
        self.mysql = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="SaiChand449@",
            database='pp_mail',
            charset='utf8mb4'
        )

    def set_mail_id(self, mail_id):
        self.mail_id = mail_id

    def get_receiver_id(self, receiver_mail):
        self.user.set_user_email(email=receiver_mail)
        user_details = self.user.check_user_exists()
        return user_details['user'][0]['user_id']

    def send_mail(self, sender_mail, receiver_mail, mail_content, mail_subject, sender_id):
        self.sender = sender_mail
        my_email = MIMEText(mail_content, "html")
        my_email["From"] = self.sender
        my_email["To"] = receiver_mail
        my_email["Subject"] = mail_subject
        self.mail_content = mail_content
        self.mail_flag = False
        self.mail_read = False
        self.mail_junk = False
        self.mail_subject = mail_subject
        self.mail_received_date = self.mail_sent_date = datetime.now()
        self.mail_info_id = "".join([random.choice(string.ascii_letters + string.digits) for n in range(30)])
        self.mail_id = "".join([random.choice(string.ascii_letters + string.digits) for n in range(30)])
        self.sender_id = sender_id
        self.receiver_id = self.get_receiver_id(receiver_mail=receiver_mail)
        self.create_mail_info()
        self.create_pp_mail()
        self.update_user_mail_info()
        self.user.server.sendmail(self.sender, receiver_mail, my_email.as_string())
        return 'True'

    def create_mail_info(self):
        cursor = self.mysql.cursor(dictionary=True)
        cursor.execute(
            "INSERT INTO mails_info(mail_body,mail_flag,mail_id,mail_info_id,mail_junk,mail_read,mail_received_date,mail_sent_date,mail_subject) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (self.mail_content, self.mail_flag, self.mail_id, self.mail_info_id, self.mail_junk, self.mail_read,
             self.mail_received_date, self.mail_sent_date, self.mail_subject))
        self.mysql.commit()
        cursor.close()

    def create_pp_mail(self):
        cursor = self.mysql.cursor(dictionary=True)
        cursor.execute(
            "INSERT INTO pp_mails(mail_id,mail_info_id,sender_id,receiver_id) VALUES (%s,%s,%s,%s)",
            (self.mail_id, self.mail_info_id, self.sender_id, self.receiver_id))
        self.mysql.commit()
        cursor.close()

    def get_user_inbox_all(self, receiver_id):
        cursor = self.mysql.cursor(dictionary=True)
        cursor.execute(
            "SELECT COUNT(*) as mails FROM mails_info INNER JOIN pp_mails WHERE pp_mails.mail_info_id = mails_info.mail_info_id AND pp_mails.receiver_id = %s",
            (receiver_id,)
        )
        data = cursor.fetchall()
        cursor.close()
        return data

    def get_user_inbox_unread(self):
        cursor = self.mysql.cursor(dictionary=True)
        cursor.execute(
            "SELECT COUNT(*) as mails FROM mails_info INNER JOIN pp_mails WHERE pp_mails.mail_info_id = mails_info.mail_info_id AND pp_mails.receiver_id = %s AND mails_info.mail_read = 0",
            (self.receiver_id,)
        )
        data = cursor.fetchall()
        cursor.close()
        return data

    def get_user_sent_mails(self):
        cursor = self.mysql.cursor(dictionary=True)
        cursor.execute(
            "SELECT COUNT(*) as mails FROM mails_info INNER JOIN pp_mails ON pp_mails.mail_info_id = mails_info.mail_info_id WHERE pp_mails.sender_id = %s",
            (self.sender_id,)
        )
        data = cursor.fetchall()
        cursor.close()
        return data

    def update_user_mail_info(self):
        pass

    def get_full_mail(self):
        cursor = self.mysql.cursor(dictionary=True)
        cursor.execute(
            """ SELECT mails_info.mail_subject, 
	                mails_info.mail_body, mails_info.mail_sent_date, 
                    mails_info.mail_received_date,
                    users.first_name, users.last_name,
                    users.email
                FROM pp_mails 
	                INNER JOIN mails_info ON pp_mails.mail_info_id = mails_info.mail_info_id
                    INNER JOIN users ON users.user_id = pp_mails.sender_id
                WHERE pp_mails.mail_id =%s""", (self.mail_id,)
        )
        data = cursor.fetchall()
        cursor.close()
        cursor = self.mysql.cursor(dictionary=True)
        cursor.execute(
            "UPDATE mails_info AS mi INNER JOIN pp_mails as pp ON pp.mail_info_id = mi.mail_info_id SET mi.mail_read = 1 WHERE pp.mail_id = %s",
            (self.mail_id,)
        )
        self.mysql.commit()
        cursor.close()
        return data
